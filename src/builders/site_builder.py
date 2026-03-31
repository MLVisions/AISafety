"""
Main site builder for AI Safety website.

Handles markdown processing, plot generation, and HTML output.
All generated assets (icons, plots) live in src/static/ and are copied
to docs/ on build.  There is exactly one copy of each file.
"""

import shutil
from pathlib import Path
from typing import Any

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

    def sync_references(self, agent_refs: list[dict[str, Any]] | None = None) -> None:
        """Sync references.md from citations across all content files."""
        from agents.utils.reference_manager import sync_references_file

        print("Syncing references...")
        sync_references_file(
            content_dir=str(self.content_dir),
            agent_refs=agent_refs,
        )

    def process_markdown_files(self, pages: list[str] | None = None) -> None:
        """Process markdown files and generate HTML.

        Args:
            pages: If provided, only process these page names (stems).
                   None processes all content files.
        """
        from agents.utils.file_operations import list_content_files

        print("Processing markdown files...")
        md_files = [Path(f) for f in list_content_files(str(self.content_dir))]

        if pages:
            page_set = set(pages)
            # Always include references since it's derived
            page_set.add("references")
            md_files = [f for f in md_files if f.stem in page_set]

        for md_file in md_files:
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            frontmatter, html_content = self.markdown_processor.convert(content)

            page_name = md_file.stem
            output_file = self.output_dir / f"{page_name}.html"
            html_output = self.template_engine.render_page(html_content, frontmatter, page_name)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_output)

        print(f"  Rendered {len(md_files)} pages.")

    # ------------------------------------------------------------------
    # Top-level build
    # ------------------------------------------------------------------

    def build(
        self,
        include_market_plots: bool = False,
        agent_refs: list[dict[str, Any]] | None = None,
        pages: list[str] | None = None,
    ) -> None:
        """Build the complete website.

        Args:
            include_market_plots: If True, also fetch live ticker data and
                generate raw-ticker / category-comparison plots.
            agent_refs: Optional references from research agents to merge
                into references.md during the build.
            pages: If provided, only rebuild HTML for these page names.
                Static assets and references are always synced in full.
        """
        print("Building AI Safety Website")
        print("=" * 50)

        # 1. Generate market data assets into src/static/ (optional)
        if include_market_plots:
            self.generate_market_plots()

        # 2. Sync references.md from content citations
        self.sync_references(agent_refs=agent_refs)

        # 3. Clean docs/ and copy everything from src/static/
        if not pages:
            # Full build: clean and recopy everything
            self.clean_output()
            self.copy_static_assets()
        else:
            # Partial build: ensure output dir exists, refresh static assets
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.copy_static_assets()

        # 4. Render markdown -> HTML
        self.process_markdown_files(pages=pages)

        print("-" * 50)
        print(f"Build complete -> {self.output_dir}")
