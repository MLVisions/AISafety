"""
Unit tests for ContentUpdateApplier with structured update format
"""

from unittest.mock import patch

import pytest

from agents.utils.content_update_applier import ContentUpdateApplier

# Shared sample markdown used by multiple tests
SAMPLE_MD = """\
## Introduction

Some intro text.

### Sub A

Body of sub A.

### Sub B

Body of sub B.

## Another Section

Another body.
"""


class TestStructuredUpdates:
    """Test structured update functionality"""

    def test_apply_section_rewrite(self) -> None:
        """Test applying a section rewrite via apply_updates"""
        applier = ContentUpdateApplier()

        with patch('agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('agents.utils.content_update_applier.write_markdown_file'):
            mock_read.return_value = ({"title": "Test"}, SAMPLE_MD)

            updates = [
                {
                    "section_title": "### Sub A",
                    "new_content": "Completely new sub A content.",
                    "reason": "Outdated",
                    "confidence": 0.95,
                },
            ]
            result = applier.apply_updates("test.md", updates)

            assert result["success"] is True
            assert result["updates_applied"] == 1

    def test_confidence_filtering(self) -> None:
        """Test that low-confidence updates are skipped"""
        applier = ContentUpdateApplier()

        with patch('agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('agents.utils.content_update_applier.write_markdown_file') as mock_write:

            mock_read.return_value = ({"title": "Test"}, SAMPLE_MD)

            updates = [
                {
                    "section_title": "Introduction",
                    "new_content": "Should not be applied.",
                    "reason": "Low confidence",
                    "confidence": 0.5,
                }
            ]

            result = applier.apply_updates("test.md", updates)

            assert result["success"] is True
            assert result["updates_applied"] == 0
            mock_write.assert_not_called()

    def test_missing_section_title_skipped(self) -> None:
        """Updates without section_title or new_content are skipped."""
        applier = ContentUpdateApplier()

        with patch('agents.utils.content_update_applier.read_markdown_file') as mock_read, \
             patch('agents.utils.content_update_applier.write_markdown_file') as mock_write:

            mock_read.return_value = ({"title": "Test"}, SAMPLE_MD)

            updates = [
                {"new_content": "No heading", "confidence": 0.95},
                {"section_title": "Introduction", "confidence": 0.95},
            ]

            result = applier.apply_updates("test.md", updates)

            assert result["success"] is True
            assert result["updates_applied"] == 0
            assert result["updates_skipped"] == 2
            mock_write.assert_not_called()


# ---------------------------------------------------------------------------
# Tests for _rewrite_section (static method)
# ---------------------------------------------------------------------------


class TestRewriteSection:
    """Test the _rewrite_section heading-matching logic."""

    def test_rewrite_h2_section(self) -> None:
        """Rewrite an H2 section by plain title."""
        result = ContentUpdateApplier._rewrite_section(
            SAMPLE_MD, "Introduction", "New intro.",
        )
        assert result is not None
        assert "New intro." in result
        assert "Some intro text." not in result
        # Heading itself should be preserved
        assert "## Introduction" in result

    def test_rewrite_h3_section_plain_title(self) -> None:
        """Rewrite an H3 subsection by plain title (no # prefix)."""
        result = ContentUpdateApplier._rewrite_section(
            SAMPLE_MD, "Sub A", "Replaced body A.",
        )
        assert result is not None
        assert "Replaced body A." in result
        assert "Body of sub A." not in result
        # Sibling H3 should be untouched
        assert "Body of sub B." in result

    def test_rewrite_h3_section_with_hash_prefix(self) -> None:
        """Agent returns section_title with '### ' prefix — must still match."""
        result = ContentUpdateApplier._rewrite_section(
            SAMPLE_MD, "### Sub B", "Replaced body B.",
        )
        assert result is not None
        assert "Replaced body B." in result
        assert "Body of sub B." not in result
        # Other sections untouched
        assert "Body of sub A." in result

    def test_rewrite_h2_with_hash_prefix(self) -> None:
        """Agent returns section_title with '## ' prefix for H2 heading."""
        result = ContentUpdateApplier._rewrite_section(
            SAMPLE_MD, "## Another Section", "Brand new content.",
        )
        assert result is not None
        assert "Brand new content." in result
        assert "Another body." not in result

    def test_rewrite_returns_none_for_unknown_heading(self) -> None:
        """Should return None when heading doesn't exist."""
        result = ContentUpdateApplier._rewrite_section(
            SAMPLE_MD, "Nonexistent Heading", "text",
        )
        assert result is None

    @pytest.mark.parametrize("heading", [
        "sub a",
        "SUB A",
        "  Sub A  ",
        "### Sub A",
        "###   Sub A  ",
    ])
    def test_rewrite_case_and_whitespace_insensitive(self, heading: str) -> None:
        """Heading match should be case- and whitespace-insensitive."""
        result = ContentUpdateApplier._rewrite_section(
            SAMPLE_MD, heading, "New body.",
        )
        assert result is not None
        assert "New body." in result
