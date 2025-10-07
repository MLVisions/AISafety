"""
Unit tests for ValidationEnhancerFactory and related classes
Tests the factory pattern and validation logic
"""


import pytest

from src.agents.utils.validation_enhancer_factory import (
    ActionValidationEnhancer,
    TechnologyValidationEnhancer,
    ValidationEnhancerFactory,
)


class TestValidationEnhancerFactory:
    """Test ValidationEnhancerFactory class"""

    def test_create_enhancer_valid_pages(self):
        """Test factory creates correct enhancers for valid pages"""
        # Test action enhancer
        action_enhancer = ValidationEnhancerFactory.create_enhancer("action")
        assert isinstance(action_enhancer, ActionValidationEnhancer)

        # Test technology enhancer
        tech_enhancer = ValidationEnhancerFactory.create_enhancer("technology")
        assert isinstance(tech_enhancer, TechnologyValidationEnhancer)

        # Test LLM enhancer (should be same as technology)
        llm_enhancer = ValidationEnhancerFactory.create_enhancer("llm")
        assert isinstance(llm_enhancer, TechnologyValidationEnhancer)

    def test_create_enhancer_invalid_page(self):
        """Test factory raises error for invalid page"""
        with pytest.raises(ValueError, match="No validation enhancer"):
            ValidationEnhancerFactory.create_enhancer("invalid_page")

    def test_all_enhancers_implement_interface(self):
        """Test all enhancers implement ValidationEnhancer interface"""
        page_types = ["action", "technology", "llm", "economy", "society"]

        for page_type in page_types:
            enhancer = ValidationEnhancerFactory.create_enhancer(page_type)
            assert hasattr(enhancer, 'validate_content')
            assert callable(enhancer.validate_content)


class TestActionValidationEnhancer:
    """Test ActionValidationEnhancer class"""

    def setUp(self):
        self.enhancer = ActionValidationEnhancer()

    def test_validate_content_basic(self):
        """Test basic content validation functionality"""
        enhancer = ActionValidationEnhancer()
        content = """
        ### Build community
        **Form local AI-check groups**

        Join or organise local groups to share knowledge and support practical steps.
        You should start by finding existing communities in your area.
        """

        result = enhancer.validate_content(content)

        # Check required fields
        assert "score" in result
        assert isinstance(result["score"], (int, float))
        assert 0 <= result["score"] <= 1
        assert "strategy_feasibility" in result
        assert "resource_accessibility" in result
        assert "clarity" in result
        assert "actionability" in result

    def test_validate_content_empty_string(self):
        """Test validation with empty content"""
        enhancer = ActionValidationEnhancer()
        result = enhancer.validate_content("")

        assert "score" in result
        assert result["score"] >= 0

    def test_validate_strategy_feasibility(self):
        """Test strategy feasibility validation"""
        enhancer = ActionValidationEnhancer()

        # Content with feasibility indicators
        feasible_content = """
        Start with practical, achievable steps. Begin gradually with realistic goals.
        These accessible methods provide step-by-step guidance.
        """

        score = enhancer._validate_strategy_feasibility(feasible_content)
        assert isinstance(score, float)
        assert 0 <= score <= 1

        # Should score higher than content without indicators
        basic_content = "Some random content without feasibility indicators."
        basic_score = enhancer._validate_strategy_feasibility(basic_content)
        assert score >= basic_score

    def test_validate_resource_accessibility(self):
        """Test resource accessibility validation"""
        enhancer = ActionValidationEnhancer()

        # Content with accessibility indicators
        accessible_content = """
        Free online courses are available. Join local community groups.
        These accessible resources provide practical tutorials and guides.
        """

        score = enhancer._validate_resource_accessibility(accessible_content)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0  # Should detect accessibility indicators

    def test_validate_clarity(self):
        """Test clarity validation"""
        enhancer = ActionValidationEnhancer()

        # Content with clear action verbs and examples
        clear_content = """
        Build your skills by learning new technologies. Create projects to practice.
        For example, start with simple automation scripts. Join communities to engage with others.
        """

        score = enhancer._validate_clarity(clear_content)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0  # Should detect action verbs and examples

    def test_validate_actionability(self):
        """Test actionability validation"""
        enhancer = ActionValidationEnhancer()

        # Content with actionable steps
        actionable_content = """
        1. First, research available resources in your area.
        2. Then, connect with local groups.
        3. Next, start building relevant skills.
        You should begin with these practical steps. You can make progress today.
        """

        score = enhancer._validate_actionability(actionable_content)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0  # Should detect steps and calls to action

    def test_error_handling(self):
        """Test error handling in validation"""
        enhancer = ActionValidationEnhancer()

        # Test with problematic content that might cause errors
        try:
            result = enhancer.validate_content("Content that might cause issues: \x00\x01")
            # If it doesn't raise, should return valid structure
            assert "score" in result
        except (TypeError, AttributeError, ValueError):
            # Some content might cause expected errors
            pass


class TestTechnologyValidationEnhancer:
    """Test TechnologyValidationEnhancer class"""

    def test_validate_content_basic(self):
        """Test basic technology content validation"""
        enhancer = TechnologyValidationEnhancer()
        content = """
        ### Latest AI Models
        GPT-4 achieves 92% accuracy on standardized benchmarks.
        New transformer architectures released in 2024 show improved performance.
        Neural networks require significant training parameters for inference.
        """

        result = enhancer.validate_content(content)

        assert "score" in result
        assert isinstance(result["score"], (int, float))
        assert 0 <= result["score"] <= 1
        assert "technical_accuracy" in result
        assert "model_claims" in result
        assert "benchmark_accuracy" in result
        assert "release_dates" in result

    def test_validate_technical_accuracy(self):
        """Test technical accuracy validation"""
        enhancer = TechnologyValidationEnhancer()

        # Content with technical terms
        technical_content = """
        Neural networks use transformer attention mechanisms for training.
        The model parameters affect inference performance and algorithm efficiency.
        """

        score = enhancer._validate_technical_accuracy(technical_content)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0  # Should detect technical terms

    def test_validate_model_claims(self):
        """Test model claims validation"""
        enhancer = TechnologyValidationEnhancer()

        # Content with specific model mentions
        model_content = """
        GPT-4 outperforms previous versions. Claude 3 shows improvements.
        LLaMA 2 demonstrates better reasoning. PaLM 2 handles complex tasks.
        Gemini Pro provides multimodal capabilities.
        """

        score = enhancer._validate_model_claims(model_content)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0  # Should detect model names

    def test_validate_benchmark_accuracy(self):
        """Test benchmark accuracy validation"""
        enhancer = TechnologyValidationEnhancer()

        # Content with valid percentages
        benchmark_content = """
        The model achieves 85.6% accuracy on evaluation tasks.
        Performance improved to 92% on standardized tests.
        Baseline accuracy was 67.2% before optimization.
        """

        score = enhancer._validate_benchmark_accuracy(benchmark_content)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0  # Should detect valid percentages

    def test_validate_benchmark_accuracy_invalid_percentages(self):
        """Test benchmark validation with invalid percentages"""
        enhancer = TechnologyValidationEnhancer()

        # Content with invalid percentages
        invalid_content = "The model achieves 150% accuracy (impossible)."

        score = enhancer._validate_benchmark_accuracy(invalid_content)
        assert isinstance(score, float)
        assert score == 0  # Should reject invalid percentages

    def test_validate_release_dates(self):
        """Test release date validation"""
        enhancer = TechnologyValidationEnhancer()

        # Content with valid years
        date_content = """
        Released in 2023, the model builds on 2022 research.
        Updates from 2024 show continued progress since 2021.
        """

        score = enhancer._validate_release_dates(date_content)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0  # Should detect valid years


class TestValidationEnhancerEdgeCases:
    """Test edge cases and error handling for validation enhancers"""

    def test_empty_content_all_enhancers(self):
        """Test all enhancers handle empty content"""
        enhancer_types = ["action", "technology", "llm"]

        for enhancer_type in enhancer_types:
            enhancer = ValidationEnhancerFactory.create_enhancer(enhancer_type)
            result = enhancer.validate_content("")

            assert "score" in result
            assert isinstance(result["score"], (int, float))
            assert result["score"] >= 0

    def test_very_long_content(self):
        """Test enhancers handle very long content"""
        long_content = "This is a test sentence. " * 1000

        enhancer = ValidationEnhancerFactory.create_enhancer("action")
        result = enhancer.validate_content(long_content)

        assert "score" in result
        assert isinstance(result["score"], (int, float))

    def test_unicode_content(self):
        """Test enhancers handle unicode content"""
        unicode_content = """
        测试内容 with émojis 🚀 and special characters: àáâãäåæçèéêë
        Mixed language content should be handled gracefully.
        """

        enhancer = ValidationEnhancerFactory.create_enhancer("technology")
        result = enhancer.validate_content(unicode_content)

        assert "score" in result
        assert isinstance(result["score"], (int, float))

    def test_html_content_safety(self):
        """Test enhancers safely handle HTML content"""
        html_content = """
        <script>alert('test')</script>
        <div class="content">Regular content with HTML tags</div>
        <p>This should be processed safely</p>
        """

        enhancer = ValidationEnhancerFactory.create_enhancer("action")
        result = enhancer.validate_content(html_content)

        assert "score" in result
        assert isinstance(result["score"], (int, float))

    def test_regex_safety(self):
        """Test that regex patterns don't cause issues with special content"""
        special_content = r"""
        Content with regex special chars: ()[]{}^$.|*+?\
        And some normal content for validation testing.
        """

        enhancer = ValidationEnhancerFactory.create_enhancer("action")
        result = enhancer.validate_content(special_content)

        assert "score" in result
        assert isinstance(result["score"], (int, float))
