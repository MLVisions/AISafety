"""
Unit tests for BaseAgent multimodal content block construction.
"""

from unittest.mock import MagicMock, patch

from agents.base_agent import BaseAgent


class TestMultimodalContentBlocks:
    """Tests for _call_llm multimodal handling."""

    def _make_agent(self) -> BaseAgent:
        """Create a BaseAgent with mocked agents.yaml config."""
        with patch("agents.base_agent._load_agents_yaml", return_value={
            "test_agent": {
                "role": "test researcher",
                "goal": "test",
                "backstory": "test background",
            }
        }):
            return BaseAgent("test_agent")

    @patch("agents.base_agent.litellm")
    @patch("agents.base_agent.get_llm_config")
    def test_documents_use_correct_litellm_format(
        self, mock_config: MagicMock, mock_litellm: MagicMock
    ) -> None:
        """Document content blocks should use litellm's file format."""
        mock_config.return_value = MagicMock(
            model="openai/gpt-4o", api_key="test-key", temperature=None
        )
        mock_litellm.supports_vision.return_value = True

        mock_pdf_input = MagicMock(return_value=True)
        with patch("litellm.utils.supports_pdf_input", mock_pdf_input):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content='{"test": true}'))]
            mock_litellm.completion.return_value = mock_response

            agent = self._make_agent()
            agent._call_llm(
                system_prompt="sys",
                user_prompt="user",
                documents=[{"mime": "application/pdf", "data": "AQID"}],
            )

        call_kwargs = mock_litellm.completion.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        user_msg = messages[1]
        content = user_msg["content"]

        # Find the file block
        file_blocks = [b for b in content if b.get("type") == "file"]
        assert len(file_blocks) == 1
        file_block = file_blocks[0]["file"]

        # Must have file_data as data URI, must NOT have filename
        assert "file_data" in file_block
        assert file_block["file_data"] == "data:application/pdf;base64,AQID"
        assert "filename" not in file_block

    @patch("agents.base_agent.litellm")
    @patch("agents.base_agent.get_llm_config")
    def test_images_use_image_url_format(
        self, mock_config: MagicMock, mock_litellm: MagicMock
    ) -> None:
        """Image content blocks should use standard image_url format."""
        mock_config.return_value = MagicMock(
            model="openai/gpt-4o", api_key="test-key", temperature=None
        )
        mock_litellm.supports_vision.return_value = True

        mock_pdf_input = MagicMock(return_value=False)
        with patch("litellm.utils.supports_pdf_input", mock_pdf_input):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
            mock_litellm.completion.return_value = mock_response

            agent = self._make_agent()
            agent._call_llm(
                system_prompt="sys",
                user_prompt="user",
                images=[{"url": "data:image/png;base64,ABC123"}],
            )

        call_kwargs = mock_litellm.completion.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        user_msg = messages[1]
        content = user_msg["content"]

        img_blocks = [b for b in content if b.get("type") == "image_url"]
        assert len(img_blocks) == 1
        assert img_blocks[0]["image_url"]["url"] == "data:image/png;base64,ABC123"

    @patch("agents.base_agent.litellm")
    @patch("agents.base_agent.get_llm_config")
    def test_no_vision_falls_back_to_text(
        self, mock_config: MagicMock, mock_litellm: MagicMock
    ) -> None:
        """When vision is not supported, images are skipped and text-only sent."""
        mock_config.return_value = MagicMock(
            model="openai/gpt-3.5-turbo", api_key="test-key", temperature=None
        )
        mock_litellm.supports_vision.return_value = False

        mock_pdf_input = MagicMock(return_value=False)
        with patch("litellm.utils.supports_pdf_input", mock_pdf_input):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
            mock_litellm.completion.return_value = mock_response

            agent = self._make_agent()
            agent._call_llm(
                system_prompt="sys",
                user_prompt="user prompt here",
                images=[{"url": "data:image/png;base64,ABC"}],
                documents=[{"mime": "application/pdf", "data": "AQID"}],
            )

        call_kwargs = mock_litellm.completion.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        user_msg = messages[1]
        # Should be plain text, not multimodal content blocks
        assert isinstance(user_msg["content"], str)
        assert "user prompt here" in user_msg["content"]

    @patch("agents.base_agent.litellm")
    @patch("agents.base_agent.get_llm_config")
    def test_vision_yes_pdf_no_only_images_sent(
        self, mock_config: MagicMock, mock_litellm: MagicMock
    ) -> None:
        """Vision-capable model without PDF support should send images only."""
        mock_config.return_value = MagicMock(
            model="openai/gpt-4-vision", api_key="test-key", temperature=None
        )
        mock_litellm.supports_vision.return_value = True

        mock_pdf_input = MagicMock(return_value=False)
        with patch("litellm.utils.supports_pdf_input", mock_pdf_input):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
            mock_litellm.completion.return_value = mock_response

            agent = self._make_agent()
            agent._call_llm(
                system_prompt="sys",
                user_prompt="user",
                images=[{"url": "data:image/png;base64,ABC"}],
                documents=[{"mime": "application/pdf", "data": "AQID"}],
            )

        call_kwargs = mock_litellm.completion.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        user_msg = messages[1]
        content = user_msg["content"]

        # Should have image blocks but no file blocks
        img_blocks = [b for b in content if b.get("type") == "image_url"]
        file_blocks = [b for b in content if b.get("type") == "file"]
        assert len(img_blocks) == 1
        assert len(file_blocks) == 0
