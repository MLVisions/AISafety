"""
Markdown processor for AI Safety website
Converts markdown content to HTML with custom extensions for tabs and other features
"""

import re
from typing import Any

import markdown
import yaml


class MarkdownProcessor:
    """Process markdown files with frontmatter and custom extensions"""

    def __init__(self) -> None:
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.attr_list',
            ],
            extension_configs={
                'markdown.extensions.codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False,
                },
                'markdown.extensions.toc': {
                    'permalink': False,
                },
            }
        )

    def parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        """Extract YAML frontmatter from markdown content"""
        if not content.startswith('---'):
            return {}, content

        try:
            # Split frontmatter and content
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}, content

            frontmatter = yaml.safe_load(parts[1])
            markdown_content = parts[2].strip()

            return frontmatter or {}, markdown_content
        except yaml.YAMLError:
            return {}, content

    def process_custom_shortcodes(self, content: str) -> str:
        """Process custom shortcodes like {{< tabs >}} and {{< callout-card >}}"""

        # Process tabs shortcode
        tab_pattern = r'{{< tabs >}}(.*?){{< /tabs >}}'
        content = re.sub(tab_pattern, self._process_tabs, content, flags=re.DOTALL)

        # Process callout-card shortcode
        # {{< callout-card "Title" "link" "description" >}}
        card_pattern = r'{{<\s*callout-card\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"\s*>}}'
        content = re.sub(card_pattern, self._process_callout_card, content)

        return content

    def process_internal_links(self, content: str) -> str:
        """Convert internal markdown links (e.g. references.md) to .html for build output.

        This only rewrites relative links (not starting with http:// or https://).
        Example: [References](references.md#1) -> [References](references.html#1)
        """

        def _repl(m: re.Match[str]) -> str:
            path = m.group(1)
            anchor = m.group(2) or ""
            # change trailing .md to .html
            if path.lower().endswith(".md"):
                new_path = path[:-3] + ".html"
            else:
                new_path = path
            return f"({new_path}{anchor})"

        # Match markdown link targets that are relative .md files, with optional anchor
        pattern = r"\((?!https?://)([^)#]+\.md)(#[^)]*)?\)"
        return re.sub(pattern, _repl, content)

    def _process_tabs(self, match: re.Match[str]) -> str:
        """Convert tabs shortcode to HTML"""
        tabs_content = match.group(1)

        # Extract individual tabs
        tab_pattern = r'{{< tab "([^"]*)" "([^"]*)" >}}(.*?){{< /tab >}}'
        tabs = re.findall(tab_pattern, tabs_content, re.DOTALL)

        if not tabs:
            return match.group(0)  # Return original if no tabs found

        # Generate tab container HTML
        html = ['<div class="tab-container">']

        # Tab buttons
        for i, (title, tab_id, _) in enumerate(tabs):
            active_class = ' active' if i == 0 else ''
            html.append(f'<button class="tab-button{active_class}" data-tab="{tab_id}">{title}</button>')

        html.append('</div>')

        # Tab content
        for i, (_, tab_id, content) in enumerate(tabs):
            display_style = 'block' if i == 0 else 'none'
            processed_content = self.md.convert(content.strip())
            html.append(f'<div class="tab-content" id="{tab_id}" style="display: {display_style};">')
            html.append(processed_content)
            html.append('</div>')

        return '\n'.join(html)

    @staticmethod
    def _process_callout_card(match: re.Match[str]) -> str:
        """Convert a callout-card shortcode to an HTML card element."""
        title = match.group(1)
        link = match.group(2)
        description = match.group(3)
        return (
            f'<div class="callout-card">'
            f'<a href="{link}">'
            f'<h3>{title}</h3>'
            f'<p>{description}</p>'
            f'<span class="callout-card-arrow">&#8594;</span>'
            f'</a></div>'
        )

    def process_images(self, content: str) -> str:
        """Process image markdown and wrap in chart-wrapper if needed"""

        # Pattern for standalone images (not in tabs)
        img_pattern = r'^!\[([^\]]*)\]\(([^)]+)\)$'

        def wrap_image(match: re.Match[str]) -> str:
            alt_text = match.group(1)
            src = match.group(2)
            return f'<div class="chart-wrapper"><img src="{src}" alt="{alt_text}" loading="lazy" /></div>'

        # Process line by line to only wrap standalone images
        lines = content.split('\n')
        processed_lines = []

        for line in lines:
            line = line.strip()
            if re.match(img_pattern, line):
                processed_lines.append(re.sub(img_pattern, wrap_image, line))
            else:
                processed_lines.append(line)

        return '\n'.join(processed_lines)

    def convert(self, content: str) -> tuple[dict[str, Any], str]:
        """Convert markdown content to HTML with frontmatter"""

        # Parse frontmatter
        frontmatter, markdown_content = self.parse_frontmatter(content)

        # Rewrite internal .md links to .html so built HTML links are correct
        markdown_content = self.process_internal_links(markdown_content)

        # Process custom shortcodes
        markdown_content = self.process_custom_shortcodes(markdown_content)

        # Process images
        markdown_content = self.process_images(markdown_content)

        # Convert to HTML
        html_content = self.md.convert(markdown_content)

        # Reset markdown processor for next use
        self.md.reset()

        return frontmatter, html_content
