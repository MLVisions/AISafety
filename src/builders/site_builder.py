"""
Main site builder for AI Safety website.

Handles markdown processing, plot generation, and HTML output.
All generated assets (icons, plots) live in src/static/ and are copied
to docs/ on build.  There is exactly one copy of each file.
"""

import shutil
from pathlib import Path

from .markdown_processor import MarkdownProcessor
from .template_engine import TemplateEngine


class SiteBuilder:
    """Build the complete website from markdown sources."""

    def __init__(self, project_root: str = ".") -> None:
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.content_dir = self.src_dir / "content"
        self.templates_dir = self.src_dir / "templates"
        self.static_dir = self.src_dir / "static"
        self.data_dir = self.src_dir / "data"
        self.output_dir = self.project_root / "docs"

        self.markdown_processor = MarkdownProcessor()
        self.template_engine = TemplateEngine(str(self.templates_dir))

    # ------------------------------------------------------------------
    # Build stages
    # ------------------------------------------------------------------

    def clean_output(self) -> None:
        """Clean the output directory."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def copy_static_assets(self) -> None:
        """Copy static files (CSS, JS, images including icons) to output."""
        print("Copying static assets...")
        if self.static_dir.exists():
            for item in self.static_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.output_dir)
                elif item.is_dir():
                    shutil.copytree(item, self.output_dir / item.name, dirs_exist_ok=True)

    def generate_market_plots(self) -> None:
        """Generate raw ticker plots, comparison charts, and data files.

        Writes to src/static/ so ``copy_static_assets()`` picks them up.
        Only called when the user explicitly requests market-data updates.
        """
        from market.plot_functions import (
            create_category_comparison_plots,
            create_raw_ticker_plots,
            create_ticker_data_files,
            create_ticker_dropdown_data,
        )

        images_dir = self.static_dir / "images"
        images_dir.mkdir(exist_ok=True)

        print("Fetching live market data and generating ticker plots...")
        create_raw_ticker_plots(output_dir=str(images_dir / "raw_tickers"))
        create_category_comparison_plots(output_dir=str(images_dir / "category_comparisons"))

        data_dir = self.static_dir / "data"
        data_dir.mkdir(exist_ok=True)
        create_ticker_data_files(output_dir=str(data_dir / "tickers"))
        create_ticker_dropdown_data(output_file=str(data_dir / "ticker_dropdown.json"))

    def process_markdown_files(self) -> None:
        """Process all markdown files and generate HTML."""
        from agents.utils.file_operations import list_content_files

        print("Processing markdown files...")
        md_files = [Path(f) for f in list_content_files(str(self.content_dir))]

        for md_file in md_files:
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            frontmatter, html_content = self.markdown_processor.convert(content)

            page_name = md_file.stem
            output_file = self.output_dir / f"{page_name}.html"

            if page_name == "index":
                html_output = self.template_engine.render_index(html_content, frontmatter)
            else:
                html_output = self.template_engine.render_content_page(
                    html_content, frontmatter, page_name
                )

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_output)

        print(f"  Rendered {len(md_files)} pages.")

    # ------------------------------------------------------------------
    # Top-level build
    # ------------------------------------------------------------------

    def build(self, include_market_plots: bool = False) -> None:
        """Build the complete website.

        Args:
            include_market_plots: If True, also fetch live ticker data and
                generate raw-ticker / category-comparison plots.  Off by
                default because it requires network access and is slow.
        """
        print("Building AI Safety Website")
        print("=" * 50)

        # 1. Generate market data assets into src/static/ (optional)
        if include_market_plots:
            self.generate_market_plots()

        # 2. Clean docs/ and copy everything from src/static/
        self.clean_output()
        self.copy_static_assets()

        # 3. Render markdown -> HTML
        self.process_markdown_files()

        print("-" * 50)
        print(f"Build complete -> {self.output_dir}")
