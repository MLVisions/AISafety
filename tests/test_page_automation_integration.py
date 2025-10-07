"""
Integration tests for generalized page automation framework
Tests the PageAutomationBridge and supporting components
"""

from unittest.mock import patch

import pytest

from src.agents.utils.infrastructure_bridges import PageAutomationBridge
from src.agents.utils.page_config import get_page_config, get_update_strategy
from src.agents.utils.validation_enhancer_factory import ValidationEnhancerFactory


class TestPageAutomationIntegration:
    """Integration tests for generalized page automation workflow"""

    def test_page_automation_bridge_initialization(self):
        """Test PageAutomationBridge initialization with different page types"""
        # Test action page
        action_bridge = PageAutomationBridge("action")
        assert action_bridge.page_name == "action"
        assert action_bridge.page_config.content_file == "action.md"
        assert "social_researcher" in action_bridge.page_config.research_agents

        # Test technology page
        tech_bridge = PageAutomationBridge("technology")
        assert tech_bridge.page_name == "technology"
        assert tech_bridge.page_config.content_file == "technology.md"
        assert "technology_researcher" in tech_bridge.page_config.research_agents

        # Test LLM page
        llm_bridge = PageAutomationBridge("llm")
        assert llm_bridge.page_name == "llm"
        assert llm_bridge.page_config.content_file == "llm.md"
        assert "technology_researcher" in llm_bridge.page_config.research_agents

    def test_page_config_validation(self):
        """Test page configuration validation"""
        # Valid page configurations
        valid_pages = ["action", "technology", "llm"]
        for page_name in valid_pages:
            config = get_page_config(page_name)
            assert config.page_name == page_name
            assert config.content_file.endswith('.md')
            assert len(config.research_agents) > 0
            assert len(config.research_keywords) > 0

        # Invalid page raises error
        with pytest.raises(ValueError, match="Unknown page"):
            get_page_config("invalid_page")

    def test_validation_enhancer_factory(self):
        """Test ValidationEnhancerFactory creates correct enhancers"""
        # Test action enhancer
        action_enhancer = ValidationEnhancerFactory.create_enhancer("action")
        assert action_enhancer is not None

        # Test technology enhancer
        tech_enhancer = ValidationEnhancerFactory.create_enhancer("technology")
        assert tech_enhancer is not None

        # Test LLM enhancer (should be same as technology)
        llm_enhancer = ValidationEnhancerFactory.create_enhancer("llm")
        assert llm_enhancer is not None

        # Invalid page raises error
        with pytest.raises(ValueError, match="No validation enhancer"):
            ValidationEnhancerFactory.create_enhancer("invalid_page")

    def test_update_strategy_factory(self):
        """Test update strategy factory creates correct strategies"""
        # Test action strategy
        action_strategy = get_update_strategy("action")
        assert action_strategy is not None

        # Test technology strategy
        tech_strategy = get_update_strategy("technology")
        assert tech_strategy is not None

        # Test LLM strategy
        llm_strategy = get_update_strategy("llm")
        assert llm_strategy is not None

        # Invalid page raises error
        with pytest.raises(ValueError, match="No update strategy"):
            get_update_strategy("invalid_page")

    def test_validation_enhancer_content_processing(self):
        """Test validation enhancers process content correctly"""
        # Test action content validation
        action_enhancer = ValidationEnhancerFactory.create_enhancer("action")
        action_content = """
        ### Build community
        **Form local AI-check groups**

        Join or organise local groups to share knowledge and support mental health.
        These groups provide practical steps you can take today.
        """

        action_result = action_enhancer.validate_content(action_content)
        assert "score" in action_result
        assert isinstance(action_result["score"], (int, float))
        assert 0 <= action_result["score"] <= 1

        # Test technology content validation
        tech_enhancer = ValidationEnhancerFactory.create_enhancer("technology")
        tech_content = """
        ### Latest Model Developments
        GPT-4 achieves 85% accuracy on standardized benchmarks.

        New transformer architectures released in 2024 show improved performance.
        Neural network training requires significant computational resources.
        """

        tech_result = tech_enhancer.validate_content(tech_content)
        assert "score" in tech_result
        assert isinstance(tech_result["score"], (int, float))
        assert 0 <= tech_result["score"] <= 1

    def test_update_strategy_methods(self):
        """Test update strategy methods work correctly"""
        # Test action update strategy
        action_strategy = get_update_strategy("action")

        test_content = "AI may displace as many as 50 million jobs by 2030."
        test_suggestion = {
            "content": "Recent studies show 85 million jobs may be affected.",
            "type": "statistic",
            "confidence": 0.8
        }

        updated_content = action_strategy.update_statistics(test_content, test_suggestion)
        assert isinstance(updated_content, str)

        # Test technology update strategy
        tech_strategy = get_update_strategy("technology")

        tech_content = "Current models achieve 70% accuracy on benchmarks."
        tech_suggestion = {
            "content": "Latest GPT-4 model shows 92% accuracy on same benchmarks.",
            "type": "statistic",
            "confidence": 0.9
        }

        tech_updated = tech_strategy.update_statistics(tech_content, tech_suggestion)
        assert isinstance(tech_updated, str)

    @patch('src.agents.utils.infrastructure_bridges.PageAutomationBridge._build_site')
    @patch('src.agents.utils.infrastructure_bridges.PageAutomationBridge._validate_content')
    @patch('src.agents.utils.infrastructure_bridges.PageAutomationBridge._apply_content_updates')
    @patch('src.agents.utils.infrastructure_bridges.PageAutomationBridge._process_research')
    def test_page_automation_workflow(self, mock_research, mock_updates, mock_validate, mock_build):
        """Test complete page automation workflow with mocked components"""
        # Setup mocks
        mock_research.return_value = [
            {"content": "Test research content", "agent": "test_agent"}
        ]
        mock_updates.return_value = {"updates_applied": 3}
        mock_validate.return_value = {"score": 0.85}
        mock_build.return_value = {"build_time": 2.5}

        # Test action page automation
        bridge = PageAutomationBridge("action")
        result = bridge.execute_automation()

        # Verify workflow execution
        assert result["success"] is True
        assert result["page"] == "action"
        assert "research_processed" in result
        assert "updates_applied" in result
        assert "validation_score" in result
        assert "build_time" in result
        assert len(result["workflow_stages"]) == 4

        # Verify all workflow stages were called
        mock_research.assert_called_once()
        mock_updates.assert_called_once()
        mock_validate.assert_called_once()
        mock_build.assert_called_once()

    def test_multiple_page_automation_compatibility(self):
        """Test that multiple page types can be automated with same framework"""
        page_types = ["action", "technology", "llm"]

        for page_type in page_types:
            # Each page type should be initializable
            bridge = PageAutomationBridge(page_type)
            assert bridge.page_name == page_type

            # Each should have the required components
            assert bridge.page_config is not None
            assert bridge.update_strategy is not None
            assert bridge.validation_enhancer is not None
            assert bridge.content_applier is not None

            # Each should have valid configuration
            config = bridge.page_config
            assert config.content_file.endswith('.md')
            assert len(config.research_agents) > 0
            assert len(config.validation_focus) > 0
            assert len(config.update_patterns) > 0


class TestGeneralizedFrameworkEdgeCases:
    """Test edge cases and error handling in generalized framework"""

    def test_invalid_page_names(self):
        """Test framework handles invalid page names gracefully"""
        invalid_names = ["", "nonexistent", "action.md", "123", None]

        for invalid_name in invalid_names:
            if invalid_name is not None:
                with pytest.raises((ValueError, TypeError)):
                    PageAutomationBridge(invalid_name)

    def test_empty_content_handling(self):
        """Test framework handles empty content gracefully"""
        enhancer = ValidationEnhancerFactory.create_enhancer("action")

        # Empty content should not crash
        result = enhancer.validate_content("")
        assert "score" in result
        assert result["score"] >= 0

        # Very short content
        result = enhancer.validate_content("AI")
        assert "score" in result
        assert result["score"] >= 0

    def test_malformed_suggestions_handling(self):
        """Test update strategies handle malformed suggestions"""
        strategy = get_update_strategy("action")

        # Missing fields
        malformed_suggestions = [
            {},
            {"content": ""},
            {"type": "statistic"},
            {"content": None, "type": "statistic"},
        ]

        test_content = "Test content for updates."

        for suggestion in malformed_suggestions:
            # Should not crash, may not update content
            try:
                updated = strategy.update_statistics(test_content, suggestion)
                assert isinstance(updated, str)
            except (KeyError, AttributeError, TypeError):
                # Expected for malformed suggestions
                pass
