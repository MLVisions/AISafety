"""
Main site builder for AI Safety website

Handles markdown processing, plot generation, and HTML output
"""

import os
import shutil
from pathlib import Path

from .icon_generator import generate_all_icons
from .markdown_processor import MarkdownProcessor
from .plot_generator import generate_all_plots
from .template_engine import TemplateEngine


class SiteBuilder:
    """Build the complete website from markdown sources"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.content_dir = self.src_dir / "content"
        self.templates_dir = self.src_dir / "templates"
        self.static_dir = self.src_dir / "static"
        self.data_dir = self.src_dir / "data"
        self.output_dir = self.project_root / "docs"

        # Initialize processors
        self.markdown_processor = MarkdownProcessor()
        self.template_engine = TemplateEngine(str(self.templates_dir))

    def clean_output(self) -> None:
        """Clean the output directory"""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def copy_static_assets(self) -> None:
        """Copy static files (CSS, JS, images) to output"""
        print("📁 Copying static assets...")

        # Copy all files from static directory
        if self.static_dir.exists():
            for item in self.static_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.output_dir)
                elif item.is_dir():
                    shutil.copytree(item, self.output_dir / item.name, dirs_exist_ok=True)

    def generate_plots(self) -> None:
        """Generate all plots and icons"""
        print("🎨 Generating navigation icons...")

        # Store current directory and change to project root for consistent paths
        original_cwd = os.getcwd()
        try:
            os.chdir(str(self.project_root))

            # Ensure output images directory exists
            images_dir = self.output_dir / "images"
            images_dir.mkdir(exist_ok=True)

            # Generate icons and plots
            generate_all_icons()
            print("📊 Generating plots...")
            generate_all_plots(
                data_dir=str(self.data_dir),
                output_dir=str(images_dir)
            )
        finally:
            os.chdir(original_cwd)

    def process_markdown_files(self) -> None:
        """Process all markdown files and generate HTML"""
        print("📝 Processing markdown files...")

        # Get all markdown files
        md_files = list(self.content_dir.glob("*.md"))

        for md_file in md_files:
            print(f"   Processing {md_file.name}...")

            # Read and process markdown
            with open(md_file, encoding='utf-8') as f:
                content = f.read()

            frontmatter, html_content = self.markdown_processor.convert(content)

            # Determine output filename and template
            page_name = md_file.stem
            output_file = self.output_dir / f"{page_name}.html"

            # Render appropriate template
            if page_name == 'index':
                html_output = self.template_engine.render_index(html_content, frontmatter)
            else:
                html_output = self.template_engine.render_content_page(
                    html_content, frontmatter, page_name
                )

            # Write output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_output)

    def create_page_sections(self, html_content: str) -> str:
        """Wrap content sections in proper HTML structure"""

        # Split content by h2 headers to create sections
        import re

        # Find all h2 headers and split content
        sections = re.split(r'(<h2[^>]*>.*?</h2>)', html_content)

        if len(sections) <= 1:
            # No h2 headers, wrap entire content
            return f'<section class="content-section">{html_content}</section>'

        result = []
        current_section = ""

        for _, section in enumerate(sections):
            if section.strip():
                if re.match(r'<h2[^>]*>', section):
                    # This is an h2 header, start new section
                    if current_section.strip():
                        result.append(f'<section class="content-section">{current_section}</section>')
                    current_section = section
                else:
                    # This is content, add to current section
                    current_section += section

        # Add final section
        if current_section.strip():
            result.append(f'<section class="content-section">{current_section}</section>')

        return '\n'.join(result)

    def build(self) -> None:
        """Build the complete website"""
        print("🚀 Building AI Safety Website...")
        print("=" * 50)

        # Clean and prepare output directory
        self.clean_output()

        # Copy static assets first
        self.copy_static_assets()

        # Generate plots
        self.generate_plots()

        # Process markdown and generate HTML
        self.process_markdown_files()

        print("\n✅ Website build complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print("🌐 Ready for deployment to GitHub Pages")


def main() -> None:
    """Main entry point for the build script"""
    import sys

    # Get project root from command line or use current directory
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    builder = SiteBuilder(project_root)
    builder.build()


if __name__ == "__main__":
    main()
