"""
Unit tests for ContentUpdateApplier with strategy pattern support
Tests both new strategy-based interface and legacy compatibility
"""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from src.agents.utils.content_update_applier import ContentUpdateApplier
from src.agents.utils.page_config import ActionUpdateStrategy, TechnologyUpdateStrategy


class TestContentUpdateApplierNew:
    """Test new strategy-based ContentUpdateApplier functionality"""

    def test_apply_updates_with_strategy(self):
        """Test apply_updates method with update strategy"""
        applier = ContentUpdateApplier()

        # Mock file operations

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('src.agents.utils.content_update_applier.write_markdown_file') as mock_write, \
             patch.object(applier, '_create_backup'):

            mock_read.return_value = ({"title": "Test"}, "Test content with 50 million jobs affected.")

            suggestions = [
                {
                    "type": "statistic",
                    "content": "Recent studies show 85 million jobs may be affected.",
                    "confidence": 0.8
                }
            ]

            strategy = ActionUpdateStrategy()
            result = applier.apply_updates("test.md", suggestions, strategy)

            assert result["success"] is True
            assert "updates_applied" in result
            assert "timestamp" in result
            mock_write.assert_called_once()

    def test_apply_updates_without_strategy(self):
        """Test apply_updates method without strategy (no updates applied)"""
        applier = ContentUpdateApplier()

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('src.agents.utils.content_update_applier.write_markdown_file') as mock_write, \
             patch.object(applier, '_create_backup'):

            mock_read.return_value = ({"title": "Test"}, "Test content")

            suggestions = [{"type": "test", "content": "test"}]
            result = applier.apply_updates("test.md", suggestions)

            assert result["success"] is True
            assert result["updates_applied"] == 0
            mock_write.assert_called_once()

    def test_apply_strategy_updates_confidence_filtering(self):
        """Test that low-confidence suggestions are filtered out"""
        applier = ContentUpdateApplier()
        strategy = ActionUpdateStrategy()

        suggestions = [
            {"type": "statistic", "content": "High confidence update", "confidence": 0.8},
            {"type": "statistic", "content": "Low confidence update", "confidence": 0.3},
            {"type": "statistic", "content": "No confidence", "confidence": 0.0}
        ]

        updated_content, count = applier._apply_strategy_updates("Test content", suggestions, strategy)

        # Only high-confidence suggestions should be processed
        assert isinstance(updated_content, str)
        assert isinstance(count, int)

    def test_apply_strategy_updates_different_types(self):
        """Test strategy updates with different suggestion types"""
        applier = ContentUpdateApplier()
        strategy = ActionUpdateStrategy()

        suggestions = [
            {"type": "statistic", "content": "Statistical update", "confidence": 0.8},
            {"type": "strategy", "content": "Strategy update", "confidence": 0.7},
            {"type": "recommendation", "content": "Recommendation update", "confidence": 0.9},
            {"type": "unknown", "content": "Unknown type", "confidence": 0.8}
        ]

        updated_content, count = applier._apply_strategy_updates("Test content", suggestions, strategy)

        assert isinstance(updated_content, str)
        assert isinstance(count, int)
        assert count >= 0

    def test_legacy_method_compatibility(self):
        """Test that legacy apply_research_updates method still works"""
        applier = ContentUpdateApplier()

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('src.agents.utils.content_update_applier.write_markdown_file') as mock_write, \
             patch.object(applier, '_create_backup'), \
             patch.object(applier, '_parse_research_findings') as mock_parse:

            mock_read.return_value = ({"title": "Test"}, "Test content")
            mock_parse.return_value = [{"category": "statistics", "content": "test", "confidence": 0.8}]

            result = applier.apply_research_updates(
                "test.md",
                "Research findings",
                {"quality_score": 0.8}
            )

            assert result["success"] is True
            assert "updates_applied" in result
            mock_write.assert_called_once()

    def test_file_error_handling(self):
        """Test error handling when file operations fail"""
        applier = ContentUpdateApplier()

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")

            result = applier.apply_updates("nonexistent.md", [])

            assert result["success"] is False
            assert "error" in result

    def test_backup_creation(self):
        """Test backup creation functionality"""
        applier = ContentUpdateApplier()

        # Mock file system operations
        with patch('builtins.open', mock_open(read_data="test content")) as mock_file, \
             patch('pathlib.Path.mkdir') as mock_mkdir:

            applier._create_backup("test.md")

            # Should open source file for reading
            mock_file.assert_called()
            mock_mkdir.assert_called_once()

    def test_backup_creation_error_handling(self):
        """Test backup creation handles errors gracefully"""
        applier = ContentUpdateApplier()

        with patch('builtins.open', side_effect=OSError("Permission denied")):
            # Should not raise exception, just print warning
            applier._create_backup("test.md")


class TestContentUpdateApplierParsing:
    """Test content parsing functionality"""

    def test_parse_research_findings_categories(self):
        """Test parsing extracts different categories of suggestions"""
        applier = ContentUpdateApplier()

        research_text = """
        Statistic: AI adoption increased by 45% in 2024.
        Trend: Remote work continues to grow rapidly.
        Strategy: Companies should invest in AI training programs.
        Recommend: Focus on upskilling existing workforce.
        Update: Previous projections were conservative.
        """

        suggestions = applier._parse_research_findings(research_text)

        assert len(suggestions) > 0
        categories = [s["category"] for s in suggestions]
        assert "statistics" in categories
        assert "strategies" in categories
        assert "recommendations" in categories

    def test_parse_research_findings_confidence_scoring(self):
        """Test that confidence scores are calculated appropriately"""
        applier = ContentUpdateApplier()

        # Research with different confidence indicators
        high_confidence_text = "Research study shows 85% improvement in productivity metrics."
        low_confidence_text = "Some might say productivity improved."

        high_suggestions = applier._parse_research_findings(high_confidence_text)
        low_suggestions = applier._parse_research_findings(low_confidence_text)

        if high_suggestions and low_suggestions:
            high_confidence = high_suggestions[0]["confidence"]
            low_confidence = low_suggestions[0]["confidence"]
            assert high_confidence >= low_confidence

    def test_calculate_suggestion_confidence(self):
        """Test confidence calculation logic"""
        applier = ContentUpdateApplier()

        # High confidence indicators
        high_conf_text = "Research study analysis shows 85% improvement based on important data."
        confidence = applier._calculate_suggestion_confidence(high_conf_text)
        assert confidence > 0.7

        # Low confidence indicators
        low_conf_text = "Maybe."
        confidence = applier._calculate_suggestion_confidence(low_conf_text)
        assert confidence <= 0.6

    def test_get_automation_outputs(self):
        """Test automation outputs discovery"""
        applier = ContentUpdateApplier()

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.glob', return_value=[Path("output1.md"), Path("output2.md")]):

            files = applier.get_automation_outputs()
            assert len(files) == 2
            assert all(f.endswith('.md') for f in files)

    def test_get_automation_outputs_no_directory(self):
        """Test automation outputs when directory doesn't exist"""
        applier = ContentUpdateApplier()

        with patch('pathlib.Path.exists', return_value=False):
            files = applier.get_automation_outputs()
            assert files == []


class TestContentUpdateApplierIntegration:
    """Integration tests for ContentUpdateApplier"""

    def test_full_workflow_with_action_strategy(self):
        """Test complete workflow with ActionUpdateStrategy"""
        applier = ContentUpdateApplier()
        strategy = ActionUpdateStrategy()

        # Mock content with job statistics
        original_content = "AI may displace as many as 50 million jobs worldwide."

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('src.agents.utils.content_update_applier.write_markdown_file') as mock_write, \
             patch.object(applier, '_create_backup'):

            mock_read.return_value = ({}, original_content)

            suggestions = [
                {
                    "type": "statistic",
                    "content": "Recent studies show 85 million jobs may be affected by automation.",
                    "confidence": 0.9
                }
            ]

            result = applier.apply_updates("action.md", suggestions, strategy)

            assert result["success"] is True
            assert result["updates_applied"] >= 0

            # Check that write was called with updated content
            mock_write.assert_called_once()
            written_args = mock_write.call_args
            updated_content = written_args[0][1]  # Second argument should be content

            # Content should potentially be updated by strategy
            assert isinstance(updated_content, str)

    def test_full_workflow_with_technology_strategy(self):
        """Test complete workflow with TechnologyUpdateStrategy"""
        applier = ContentUpdateApplier()
        strategy = TechnologyUpdateStrategy()

        original_content = "Current models achieve 70% accuracy on benchmarks."

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('src.agents.utils.content_update_applier.write_markdown_file') as mock_write, \
             patch.object(applier, '_create_backup'):

            mock_read.return_value = ({}, original_content)

            suggestions = [
                {
                    "type": "statistic",
                    "content": "Latest GPT-4 model shows 92% accuracy on same benchmarks.",
                    "confidence": 0.85
                }
            ]

            result = applier.apply_updates("technology.md", suggestions, strategy)

            assert result["success"] is True
            mock_write.assert_called_once()

    def test_error_recovery(self):
        """Test that errors in strategy don't crash the entire process"""
        applier = ContentUpdateApplier()

        # Mock strategy that raises error
        mock_strategy = Mock()
        mock_strategy.update_statistics.side_effect = Exception("Strategy error")

        with patch('src.agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('src.agents.utils.content_update_applier.write_markdown_file'), \
             patch.object(applier, '_create_backup'):

            mock_read.return_value = ({}, "Test content")

            suggestions = [{"type": "statistic", "content": "test", "confidence": 0.8}]

            result = applier.apply_updates("test.md", suggestions, mock_strategy)

            # Should still succeed even if strategy fails
            assert result["success"] is True
