"""
Integration tests for generalized page automation framework
Tests the PageAutomationBridge and supporting components
"""

import pytest

from src.agents.utils.infrastructure_bridges import PageAutomationBridge
from src.agents.utils.page_config import get_page_config
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

    def test_page_config_validation(self):
        """Test page configuration validation"""
        # Valid page configurations
        valid_pages = ["action", "technology", "llm"]
        for page_name in valid_pages:
            config = get_page_config(page_name)
            assert config.page_name == page_name
            assert config.content_file.endswith('.md')
            assert len(config.research_agents) > 0
            assert len(config.research_focus) > 0

        # Invalid page raises error
        with pytest.raises(ValueError, match="Unknown page"):
            get_page_config("nonexistent_page")

    def test_validation_enhancer_factory(self):
        """Test validation enhancer factory creates correct validators"""
        for page_name in ["action", "technology", "llm"]:
            enhancer = ValidationEnhancerFactory.create_enhancer(page_name)
            assert enhancer is not None
            # Validators should have validate_content method
            assert hasattr(enhancer, 'validate_content')
