"""
Integration tests for SiteBuilder.
"""

from pathlib import Path

import pytest

from builders.site_builder import SiteBuilder


class TestSiteBuilder:
    """Tests for SiteBuilder build pipeline."""

    @pytest.fixture()
    def project(self, tmp_path: Path) -> Path:
        """Create a minimal project structure for testing builds."""
        # Source content
        content_dir = tmp_path / "src" / "content"
        content_dir.mkdir(parents=True)
        (content_dir / "index.md").write_text(
            "---\ntitle: Test\ntagline: tag\nlayout: index\n---\n\n# Hello\n\nWorld.\n"
        )

        # Templates
        templates_dir = tmp_path / "src" / "templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "base.html").write_text(
            "<!DOCTYPE html><html><head><title>{{ title }}</title></head>"
            "<body>{% block content %}{% endblock %}</body></html>"
        )
        (templates_dir / "page.html").write_text(
            "{% extends 'base.html' %}"
            "{% block content %}{{ content }}{% endblock %}"
        )

        # Static assets
        static_dir = tmp_path / "src" / "static"
        static_dir.mkdir(parents=True)
        (static_dir / "style.css").write_text("body { margin: 0; }")

        # Data dir (for investment pipeline)
        (tmp_path / "src" / "data").mkdir(parents=True)

        # Output dir
        (tmp_path / "docs").mkdir(parents=True)

        return tmp_path

    def test_build_creates_html(self, project: Path) -> None:
        """Build should create HTML files from markdown sources."""
        builder = SiteBuilder(str(project))
        builder.build()

        output = project / "docs" / "index.html"
        assert output.exists()
        html = output.read_text()
        assert "<title>Test</title>" in html
        assert "Hello" in html

    def test_build_copies_static_assets(self, project: Path) -> None:
        """Build should copy CSS/JS to docs/."""
        builder = SiteBuilder(str(project))
        builder.build()

        css = project / "docs" / "style.css"
        assert css.exists()
        assert "margin" in css.read_text()

    def test_partial_build_keeps_existing_files(self, project: Path) -> None:
        """Partial build (--page) should not delete other files in docs/."""
        # Pre-populate docs with an existing file
        existing = project / "docs" / "other.html"
        existing.write_text("<html>existing</html>")

        builder = SiteBuilder(str(project))
        builder.build(pages=["index"])

        assert existing.exists(), "Partial build should not delete other files"
        assert (project / "docs" / "index.html").exists()

    def test_clean_output_removes_docs(self, project: Path) -> None:
        """clean_output should wipe the docs directory."""
        (project / "docs" / "old.html").write_text("old")

        builder = SiteBuilder(str(project))
        builder.clean_output()

        assert (project / "docs").exists()
        assert not (project / "docs" / "old.html").exists()

    def test_build_multiple_pages(self, project: Path) -> None:
        """Build should handle multiple content pages."""
        content_dir = project / "src" / "content"
        (content_dir / "about.md").write_text(
            "---\ntitle: About\ntagline: about us\nlayout: page\n---\n\n# About\n\nInfo.\n"
        )

        builder = SiteBuilder(str(project))
        builder.build()

        assert (project / "docs" / "index.html").exists()
        assert (project / "docs" / "about.html").exists()
