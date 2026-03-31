"""
Template engine for AI Safety website
Uses Jinja2 to render HTML templates with markdown content
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jinja2

from agents.utils.page_config import get_cta_page, get_nav_pages


class TemplateEngine:
    """Render HTML templates with content and context"""

    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        # Add custom filters
        self.env.filters['current_page'] = self._current_page_filter

    def _current_page_filter(self, page_name: str, current: str) -> str:
        """Add current-page class if this is the current page"""
        return 'current-page' if page_name == current else ''

    def get_navigation_context(self, current_page: str = '') -> dict[str, Any]:
        """Get navigation context from page_config (single source of truth)."""
        return {
            'pages': get_nav_pages(),
            'action_page': get_cta_page(),
            'current_page': current_page,
            'build_date': datetime.now(tz=timezone.utc).strftime('%B %Y'),
        }

    def render_page(self, content: str, frontmatter: dict[str, Any], current_page: str = '') -> str:
        """Render a page with content and navigation."""
        template = self.env.get_template('page.html')

        context = {
            'content': content,
            'title': frontmatter.get('title', 'AI Safety'),
            'tagline': frontmatter.get('tagline', ''),
            'meta_description': frontmatter.get('description', 'Navigate the AI tidal shift with comprehensive insights on economy, technology, society, privacy, and actionable steps for resilience.'),
            **self.get_navigation_context(current_page),
            **frontmatter
        }

        return template.render(**context)
