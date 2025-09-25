"""
Template engine for AI Safety website
Uses Jinja2 to render HTML templates with markdown content
"""

from pathlib import Path
from typing import Any

import jinja2


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
        """Get navigation context with page info"""
        pages = [
            {'name': 'index', 'url': 'index.html', 'title': 'Home', 'icon': 'home_icon.png'},
            {'name': 'economy', 'url': 'economy.html', 'title': 'Economy & Policy', 'icon': 'economy_icon.png'},
            {'name': 'technology', 'url': 'technology.html', 'title': 'AI & Technology', 'icon': 'ai_icon.png'},
            {'name': 'society', 'url': 'society.html', 'title': 'Society & Mental Health', 'icon': 'society_icon.png'},
            {'name': 'privacy', 'url': 'privacy.html', 'title': 'Privacy & Security', 'icon': 'privacy_icon.png'},
        ]

        action_page = {'name': 'action', 'url': 'action.html', 'title': 'What We Can Do Now', 'icon': 'action_icon.png'}

        return {
            'pages': pages,
            'action_page': action_page,
            'current_page': current_page
        }

    def render_page(self,
                   template_name: str,
                   content: str,
                   frontmatter: dict[str, Any],
                   current_page: str = '') -> str:
        """Render a page with content and navigation"""

        template = self.env.get_template(template_name)

        # Combine all context
        context = {
            'content': content,
            'title': frontmatter.get('title', 'AI Safety'),
            'tagline': frontmatter.get('tagline', ''),
            'meta_description': frontmatter.get('description', 'Navigate the AI tidal shift with comprehensive insights on economy, technology, society, privacy, and actionable steps for resilience.'),
            **self.get_navigation_context(current_page),
            **frontmatter
        }

        return template.render(**context)

    def render_index(self, content: str, frontmatter: dict[str, Any]) -> str:
        """Render the index page with special layout"""
        return self.render_page('index.html', content, frontmatter, 'index')

    def render_content_page(self, content: str, frontmatter: dict[str, Any], page_name: str) -> str:
        """Render a content page"""
        return self.render_page('page.html', content, frontmatter, page_name)


if __name__ == "__main__":
    # Test the template engine
    engine = TemplateEngine("../templates")

    test_frontmatter = {
        'title': 'Test Page',
        'tagline': 'Test tagline'
    }

    test_content = "<h1>Test Content</h1><p>This is test content.</p>"

    nav_context = engine.get_navigation_context('economy')
    print("Navigation context:", nav_context)
