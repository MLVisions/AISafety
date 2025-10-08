"""
Unit tests for page configuration system
Tests PageConfig and factory functions
"""

import pytest

from src.agents.utils.page_config import PAGE_CONFIGS, PageConfig, get_page_config


class TestPageConfig:
    """Test PageConfig class"""

    def test_page_config_initialization(self):
        """Test PageConfig initialization with all parameters"""
        config = PageConfig(
            page_name="test",
            content_file="test.md",
            research_agents=["test_agent"],
            research_focus=["test"],
            validation_thresholds={"test_metric": 0.8},
            system_instructions_key="test_updates"
        )

        assert config.page_name == "test"
        assert config.content_file == "test.md"
        assert config.research_agents == ["test_agent"]
        assert config.research_focus == ["test"]
        assert config.validation_thresholds == {"test_metric": 0.8}

    def test_page_config_factory_valid_pages(self):
        """Test page config factory with valid page names"""
        for page_name in ["action", "technology", "llm", "economy", "society", "privacy"]:
            config = get_page_config(page_name)
            assert isinstance(config, PageConfig)
            assert config.page_name == page_name
            assert config.content_file.endswith('.md')
            assert len(config.research_agents) > 0

    def test_page_config_factory_invalid_page(self):
        """Test page config factory with invalid page name"""
        with pytest.raises(ValueError):
            get_page_config("nonexistent_page")

    def test_all_page_configs_registered(self):
        """Test that all expected page configs are registered"""
        expected_pages = ["action", "technology", "llm", "economy", "society", "privacy"]
        for page in expected_pages:
            assert page in PAGE_CONFIGS

    def test_action_page_config(self):
        """Test action page configuration"""
        config = get_page_config("action")
        assert config.page_name == "action"
        assert config.content_file == "action.md"
        assert "social_researcher" in config.research_agents
        assert len(config.research_focus) > 0
        assert config.validation_thresholds is not None

    def test_technology_page_config(self):
        """Test technology page configuration"""
        config = get_page_config("technology")
        assert config.page_name == "technology"
        assert config.content_file == "technology.md"
        assert "technology_researcher" in config.research_agents
        assert len(config.research_focus) > 0

    def test_llm_page_config(self):
        """Test LLM page configuration"""
        config = get_page_config("llm")
        assert config.page_name == "llm"
        assert config.content_file == "llm.md"
        assert "technology_researcher" in config.research_agents

    def test_economy_page_config(self):
        """Test economy page configuration"""
        config = get_page_config("economy")
        assert config.page_name == "economy"
        assert config.content_file == "economy.md"
        assert "market_researcher" in config.research_agents

    def test_society_page_config(self):
        """Test society page configuration"""
        config = get_page_config("society")
        assert config.page_name == "society"
        assert config.content_file == "society.md"
        assert "social_researcher" in config.research_agents

    def test_privacy_page_config(self):
        """Test privacy page configuration"""
        config = get_page_config("privacy")
        assert config.page_name == "privacy"
        assert config.content_file == "privacy.md"
        assert "policy_researcher" in config.research_agents
