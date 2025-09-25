"""
Tests for the markdown processor module - Core functionality only
"""

# Add src to path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from builders.markdown_processor import MarkdownProcessor


class TestMarkdownProcessor:
    """Test core MarkdownProcessor functionality"""

    def test_parse_frontmatter_with_yaml(self, sample_markdown_content):
        """Test parsing frontmatter from markdown content"""
        processor = MarkdownProcessor()
        frontmatter, content = processor.parse_frontmatter(sample_markdown_content)

        assert frontmatter["title"] == "Test Page"
        assert frontmatter["tagline"] == "Test tagline"
        assert frontmatter["description"] == "Test description"
        assert "# Test Content" in content

    def test_parse_frontmatter_without_yaml(self):
        """Test parsing content without frontmatter"""
        content = "# Just a heading\n\nSome content."
        processor = MarkdownProcessor()
        frontmatter, processed_content = processor.parse_frontmatter(content)

        assert frontmatter == {}
        assert processed_content == content

    def test_convert_basic_markdown(self):
        """Test basic markdown to HTML conversion"""
        content = "# Heading\n\n**Bold text** and *italic text*"
        processor = MarkdownProcessor()
        frontmatter, html = processor.convert(content)

        assert frontmatter == {}
        assert "<h1" in html
        assert "Heading" in html
        assert "<strong>Bold text</strong>" in html
        assert "<em>italic text</em>" in html

    def test_convert_with_frontmatter(self, sample_markdown_content):
        """Test complete conversion process with frontmatter"""
        processor = MarkdownProcessor()
        frontmatter, html = processor.convert(sample_markdown_content)

        # Check frontmatter extraction
        assert frontmatter["title"] == "Test Page"

        # Check basic HTML structure
        assert "<h1" in html
        assert "Test Content" in html
