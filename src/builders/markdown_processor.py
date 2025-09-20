"""
Markdown processor for AI Safety website
Converts markdown content to HTML with custom extensions for tabs and other features
"""

import re
from typing import Dict, Any, Tuple
import markdown
from markdown.extensions import codehilite, toc, tables, fenced_code
import yaml


class MarkdownProcessor:
    """Process markdown files with frontmatter and custom extensions"""
    
    def __init__(self):
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
    
    def parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
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
        """Process custom shortcodes like {{< tabs >}}"""
        
        # Process tabs shortcode
        tab_pattern = r'{{< tabs >}}(.*?){{< /tabs >}}'
        content = re.sub(tab_pattern, self._process_tabs, content, flags=re.DOTALL)
        
        return content
    
    def _process_tabs(self, match) -> str:
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
    
    def process_images(self, content: str) -> str:
        """Process image markdown and wrap in chart-wrapper if needed"""
        
        # Pattern for standalone images (not in tabs)
        img_pattern = r'^!\[([^\]]*)\]\(([^)]+)\)$'
        
        def wrap_image(match):
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
    
    def convert(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Convert markdown content to HTML with frontmatter"""
        
        # Parse frontmatter
        frontmatter, markdown_content = self.parse_frontmatter(content)
        
        # Process custom shortcodes
        markdown_content = self.process_custom_shortcodes(markdown_content)
        
        # Process images
        markdown_content = self.process_images(markdown_content)
        
        # Convert to HTML
        html_content = self.md.convert(markdown_content)
        
        # Reset markdown processor for next use
        self.md.reset()
        
        return frontmatter, html_content


def process_markdown_file(file_path: str) -> Tuple[Dict[str, Any], str]:
    """Process a markdown file and return frontmatter and HTML content"""
    processor = MarkdownProcessor()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return processor.convert(content)


if __name__ == "__main__":
    # Test the processor
    test_content = """---
title: "Test Page"
layout: "page"
---

# Test Page

This is a **test** with *emphasis*.

## Section

- List item 1
- List item 2

![Test Image](images/test.png)
*Caption text*

{{< tabs >}}
{{< tab "Tab 1" "tab1" >}}
Content for tab 1
{{< /tab >}}
{{< tab "Tab 2" "tab2" >}}
Content for tab 2
{{< /tab >}}
{{< /tabs >}}
"""
    
    processor = MarkdownProcessor()
    frontmatter, html = processor.convert(test_content)
    print("Frontmatter:", frontmatter)
    print("HTML:", html)