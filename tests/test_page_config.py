"""
Unit tests for page configuration system
Tests PageConfig and factory functions
"""

import pytest

from src.agents.utils.page_config import (
    PAGE_CONFIGS,
    PageConfig,
    SectionAgentConfig,
    get_page_config,
)


class TestPageConfig:
    """Test PageConfig class"""

    def test_page_config_initialization(self) -> None:
        """Test PageConfig initialization with all parameters"""
        config = PageConfig(
            page_name="test",
            content_file="test.md",
            title="Test",
            section_agents=[
                SectionAgentConfig("Test Section", "test_agent", "test_task"),
            ],
            validation_thresholds={"test_metric": 0.8},
        )

        assert config.page_name == "test"
        assert config.content_file == "test.md"
        assert len(config.section_agents) == 1
        assert config.section_agents[0].section == "Test Section"
        assert config.section_agents[0].agent == "test_agent"
        assert config.section_agents[0].task == "test_task"
        assert config.validation_thresholds == {"test_metric": 0.8}

    def test_page_config_factory_valid_pages(self) -> None:
        """Test page config factory with valid page names"""
        for page_name in ["action", "technology", "llm", "economy", "society", "privacy"]:
            config = get_page_config(page_name)
            assert isinstance(config, PageConfig)
            assert config.page_name == page_name
            assert config.content_file.endswith('.md')
            assert len(config.section_agents) > 0

    def test_page_config_factory_invalid_page(self) -> None:
        """Test page config factory with invalid page name"""
        with pytest.raises(ValueError):
            get_page_config("nonexistent_page")

    def test_all_page_configs_registered(self) -> None:
        """Test that all expected page configs are registered"""
        expected_pages = ["action", "technology", "llm", "economy", "society", "privacy"]
        for page in expected_pages:
            assert page in PAGE_CONFIGS

    def test_action_page_config(self) -> None:
        """Test action page configuration"""
        config = get_page_config("action")
        assert config.page_name == "action"
        assert config.content_file == "action.md"
        agents = {sa.agent for sa in config.section_agents}
        assert "social_researcher" in agents
        assert config.validation_thresholds is not None

    def test_technology_page_config(self) -> None:
        """Test technology page configuration"""
        config = get_page_config("technology")
        assert config.page_name == "technology"
        assert config.content_file == "technology.md"
        agents = {sa.agent for sa in config.section_agents}
        assert "technology_researcher" in agents

    def test_llm_page_config(self) -> None:
        """Test LLM page configuration"""
        config = get_page_config("llm")
        assert config.page_name == "llm"
        assert config.content_file == "llm.md"
        agents = {sa.agent for sa in config.section_agents}
        assert "technology_researcher" in agents

    def test_economy_page_config(self) -> None:
        """Test economy page configuration"""
        config = get_page_config("economy")
        assert config.page_name == "economy"
        assert config.content_file == "economy.md"
        agents = {sa.agent for sa in config.section_agents}
        assert "market_researcher" in agents
        assert "geopolitics_researcher" in agents
        assert "digital_assets_researcher" in agents
        sections = {sa.section for sa in config.section_agents}
        assert "Macroeconomic Landscape" in sections
        assert "Geopolitical & Market Risks" in sections
        assert "Financial System Evolution" in sections

    def test_society_page_config(self) -> None:
        """Test society page configuration"""
        config = get_page_config("society")
        assert config.page_name == "society"
        assert config.content_file == "society.md"
        agents = {sa.agent for sa in config.section_agents}
        assert "social_researcher" in agents

    def test_privacy_page_config(self) -> None:
        """Test privacy page configuration"""
        config = get_page_config("privacy")
        assert config.page_name == "privacy"
        assert config.content_file == "privacy.md"
        agents = {sa.agent for sa in config.section_agents}
        assert "policy_researcher" in agents

    def test_section_agent_config_structure(self) -> None:
        """Test that all section_agents have valid structure"""
        for page_name, config in PAGE_CONFIGS.items():
            for sa in config.section_agents:
                assert sa.section, f"{page_name}: section must not be empty"
                assert sa.agent, f"{page_name}: agent must not be empty"
                assert sa.task, f"{page_name}: task must not be empty"

    def test_economy_has_five_section_agents(self) -> None:
        """Test economy page has dedicated agents for each key section"""
        config = get_page_config("economy")
        # Economy has 5 section agents (macro, geopolitics, policy, financial infra, strategy)
        assert len(config.section_agents) == 5
        tasks = {sa.task for sa in config.section_agents}
        assert "economy_macro_task" in tasks
        assert "economy_geopolitics_task" in tasks
        assert "economy_policy_task" in tasks
        assert "economy_financial_infra_task" in tasks
        assert "economy_strategy_task" in tasks
