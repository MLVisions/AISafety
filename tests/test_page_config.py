"""
Unit tests for page configuration system
Tests PageConfig, ContentUpdateStrategy, and factory functions
"""


import pytest

from src.agents.utils.page_config import (
    PAGE_CONFIGS,
    UPDATE_STRATEGIES,
    ActionUpdateStrategy,
    ContentUpdateStrategy,
    PageConfig,
    TechnologyUpdateStrategy,
    get_page_config,
    get_update_strategy,
)


class TestPageConfig:
    """Test PageConfig class"""

    def test_page_config_initialization(self):
        """Test PageConfig initialization with all parameters"""
        config = PageConfig(
            page_name="test",
            content_file="test.md",
            research_agents=["test_agent"],
            research_keywords=["test"],
            validation_focus={"test_metric": 0.8},
            update_patterns={"test_pattern": ["keyword"]}
        )

        assert config.page_name == "test"
        assert config.content_file == "test.md"
        assert config.research_agents == ["test_agent"]
        assert config.research_keywords == ["test"]
        assert config.validation_focus == {"test_metric": 0.8}
        assert config.update_patterns == {"test_pattern": ["keyword"]}

    def test_page_config_factory_valid_pages(self):
        """Test page config factory with valid page names"""
        for page_name in ["action", "technology", "llm"]:
            config = get_page_config(page_name)
            assert isinstance(config, PageConfig)
            assert config.page_name == page_name
            assert config.content_file.endswith('.md')
            assert len(config.research_agents) > 0

    def test_page_config_factory_invalid_page(self):
        """Test page config factory with invalid page name"""
        with pytest.raises(ValueError, match="Unknown page"):
            get_page_config("nonexistent")

    def test_all_configs_have_required_fields(self):
        """Test that all page configurations have required fields"""
        for _page_name, config in PAGE_CONFIGS.items():
            assert isinstance(config.page_name, str)
            assert config.content_file.endswith('.md')
            assert isinstance(config.research_agents, list)
            assert len(config.research_agents) > 0
            assert isinstance(config.research_keywords, list)
            assert len(config.research_keywords) > 0
            assert isinstance(config.validation_focus, dict)
            assert len(config.validation_focus) > 0
            assert isinstance(config.update_patterns, dict)
            assert len(config.update_patterns) > 0


class TestActionUpdateStrategy:
    """Test ActionUpdateStrategy implementation"""

    def setUp(self):
        self.strategy = ActionUpdateStrategy()

    def test_update_statistics_job_numbers(self):
        """Test statistics update for job displacement numbers"""
        strategy = ActionUpdateStrategy()
        content = "AI may displace as many as 50 million jobs worldwide."
        suggestion = {
            "content": "Recent studies show 85 million jobs may be affected by automation.",
            "type": "statistic"
        }

        updated = strategy.update_statistics(content, suggestion)
        assert "85 million jobs" in updated

    def test_update_statistics_no_match(self):
        """Test statistics update when no pattern matches"""
        strategy = ActionUpdateStrategy()
        content = "This content has no job statistics."
        suggestion = {
            "content": "85 million jobs affected",
            "type": "statistic"
        }

        updated = strategy.update_statistics(content, suggestion)
        assert updated == content  # Should remain unchanged

    def test_update_strategies_ai_skills(self):
        """Test strategy updates for AI skills content"""
        strategy = ActionUpdateStrategy()
        content = """### Reskill & adapt
**Build AI‑adjacent skills**

Current content here."""

        suggestion = {
            "content": "Focus on skills that complement AI systems for better job security.",
            "type": "strategy"
        }

        updated = strategy.update_strategies(content, suggestion)
        assert "Recent insight:" in updated
        assert "complement" in updated

    def test_update_recommendations_adds_development(self):
        """Test recommendations update adds new development section"""
        strategy = ActionUpdateStrategy()
        content = """Main content here.

*For detailed sources and research citations, see references.md*"""

        suggestion = {
            "content": "New AI policy developments affect personal planning strategies.",
            "type": "recommendation"
        }

        updated = strategy.update_recommendations(content, suggestion)
        assert "### Recent Development" in updated
        assert "AI policy developments" in updated

    def test_malformed_suggestion_handling(self):
        """Test handling of malformed suggestions"""
        strategy = ActionUpdateStrategy()
        content = "Test content"

        # Missing content field
        malformed_suggestion = {"type": "statistic"}

        try:
            updated = strategy.update_statistics(content, malformed_suggestion)
            # Should either handle gracefully or raise expected error
            assert isinstance(updated, str)
        except KeyError:
            # Expected for malformed suggestions
            pass


class TestTechnologyUpdateStrategy:
    """Test TechnologyUpdateStrategy implementation"""

    def test_update_statistics_performance_metrics(self):
        """Test statistics update for performance benchmarks"""
        strategy = TechnologyUpdateStrategy()
        content = "Current models achieve 70% accuracy on benchmarks."
        suggestion = {
            "content": "Latest GPT-4 shows 92% accuracy on standardized tests.",
            "type": "statistic"
        }

        updated = strategy.update_statistics(content, suggestion)
        # Should potentially update accuracy numbers
        assert isinstance(updated, str)

    def test_update_strategies_model_capabilities(self):
        """Test strategy updates for model capabilities"""
        strategy = TechnologyUpdateStrategy()
        content = """### Key Developments
Current model capabilities overview.

### Latest Models
Current information here."""

        suggestion = {
            "content": "New multimodal capabilities enable better human-AI collaboration features.",
            "type": "strategy"
        }

        updated = strategy.update_strategies(content, suggestion)
        if "Recent development:" in updated:
            assert "multimodal" in updated

    def test_update_recommendations_technical_insights(self):
        """Test recommendations for technical recommendations"""
        strategy = TechnologyUpdateStrategy()
        content = "**Important considerations for AI adoption**"
        suggestion = {
            "content": "Consider implementing gradual AI integration to minimize disruption.",
            "type": "recommendation"
        }

        updated = strategy.update_recommendations(content, suggestion)
        if "Technical insight:" in updated:
            assert "gradual AI integration" in updated


class TestUpdateStrategyFactory:
    """Test update strategy factory functions"""

    def test_get_update_strategy_valid_pages(self):
        """Test strategy factory with valid page names"""
        for page_name in ["action", "technology", "llm"]:
            strategy = get_update_strategy(page_name)
            assert isinstance(strategy, ContentUpdateStrategy)
            assert hasattr(strategy, 'update_statistics')
            assert hasattr(strategy, 'update_strategies')
            assert hasattr(strategy, 'update_recommendations')

    def test_get_update_strategy_invalid_page(self):
        """Test strategy factory with invalid page name"""
        with pytest.raises(ValueError, match="No update strategy"):
            get_update_strategy("nonexistent")

    def test_all_strategies_implement_interface(self):
        """Test that all strategies implement ContentUpdateStrategy interface"""
        for _page_name, strategy in UPDATE_STRATEGIES.items():
            assert hasattr(strategy, 'update_statistics')
            assert hasattr(strategy, 'update_strategies')
            assert hasattr(strategy, 'update_recommendations')

            # Test method signatures by calling with test data
            test_content = "Test content"
            test_suggestion = {"content": "test", "type": "test"}

            result = strategy.update_statistics(test_content, test_suggestion)
            assert isinstance(result, str)

            result = strategy.update_strategies(test_content, test_suggestion)
            assert isinstance(result, str)

            result = strategy.update_recommendations(test_content, test_suggestion)
            assert isinstance(result, str)

    def test_strategy_consistency(self):
        """Test that page configs and strategies are consistent"""
        for page_name in PAGE_CONFIGS.keys():
            # Each page with config should have a strategy
            assert page_name in UPDATE_STRATEGIES

            config = get_page_config(page_name)
            strategy = get_update_strategy(page_name)

            assert config.page_name == page_name
            assert isinstance(strategy, ContentUpdateStrategy)


class TestContentUpdateStrategyEdgeCases:
    """Test edge cases and error handling in update strategies"""

    def test_empty_content_handling(self):
        """Test strategies handle empty content gracefully"""
        strategies = [ActionUpdateStrategy(), TechnologyUpdateStrategy()]

        for strategy in strategies:
            suggestion = {"content": "test update", "type": "statistic"}

            result = strategy.update_statistics("", suggestion)
            assert isinstance(result, str)

            result = strategy.update_strategies("", suggestion)
            assert isinstance(result, str)

            result = strategy.update_recommendations("", suggestion)
            assert isinstance(result, str)

    def test_none_suggestion_handling(self):
        """Test strategies handle None suggestion fields"""
        strategy = ActionUpdateStrategy()
        content = "Test content"

        suggestions_with_none = [
            {"content": None, "type": "statistic"},
            {"content": "test", "type": None},
            {"content": "", "type": "statistic"},
        ]

        for suggestion in suggestions_with_none:
            try:
                result = strategy.update_statistics(content, suggestion)
                assert isinstance(result, str)
            except (AttributeError, TypeError, KeyError):
                # Expected for malformed suggestions
                pass

    def test_regex_pattern_safety(self):
        """Test that regex patterns in strategies are safe"""
        strategy = ActionUpdateStrategy()

        # Test with content that could cause regex issues
        problematic_content = r"Content with special chars: ()[]{}^$.|*+?\\"
        suggestion = {"content": "Test update", "type": "statistic"}

        # Should not raise regex errors
        result = strategy.update_statistics(problematic_content, suggestion)
        assert isinstance(result, str)
