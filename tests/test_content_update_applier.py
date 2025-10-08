"""
Unit tests for ContentUpdateApplier with structured update format
"""

from unittest.mock import patch

from src.agents.utils.content_update_applier import ContentUpdateApplier


class TestStructuredUpdates:
    """Test structured update functionality"""

    def test_apply_statistic_update(self):
        """Test applying a statistic update"""
        applier = ContentUpdateApplier()

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('src.agents.utils.content_update_applier.write_markdown_file') as mock_write, \
             patch.object(applier, '_create_backup'):

            original_content = "Test content with 50 million jobs affected by AI."
            mock_read.return_value = ({"title": "Test"}, original_content)

            structured_updates = [
                {
                    "section_title": "Employment Impact",
                    "update_type": "statistic_update",
                    "original_text": "50 million jobs affected",
                    "updated_text": "85 million jobs affected",
                    "reason": "Updated with 2024 data",
                    "source_url": "https://example.com/source",
                    "confidence": 0.9
                }
            ]

            result = applier.apply_updates("test.md", structured_updates)

            assert result["success"] is True
            assert result["updates_applied"] == 1

    def test_confidence_filtering(self):
        """Test that low-confidence updates are skipped"""
        applier = ContentUpdateApplier()

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('src.agents.utils.content_update_applier.write_markdown_file') as mock_write, \
             patch.object(applier, '_create_backup'):

            original_content = "Test content."
            mock_read.return_value = ({"title": "Test"}, original_content)

            structured_updates = [
                {
                    "section_title": "Test",
                    "update_type": "statistic_update",
                    "original_text": "Test",
                    "updated_text": "Updated",
                    "reason": "Low confidence",
                    "source_url": "",
                    "confidence": 0.5
                }
            ]

            result = applier.apply_updates("test.md", structured_updates)

            assert result["success"] is True
            assert result["updates_applied"] == 0
            mock_write.assert_not_called()
