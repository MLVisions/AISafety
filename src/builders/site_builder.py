"""
Main site builder for AI Safety website.

Handles markdown processing, plot generation, and HTML output.
All generated assets (icons, plots) live in src/static/ and are copied
to docs/ on build.  There is exactly one copy of each file.
"""

import hashlib
import json
import os
import shutil
from pathlib import Path

from .markdown_processor import MarkdownProcessor
from .plot_generator import generate_all_plots
from .template_engine import TemplateEngine

PLOT_HASH_FILE = ".plot_cache.json"


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
    # Hashing helpers (for plot caching)
    # ------------------------------------------------------------------

    def _hash_data_files(self) -> dict[str, str]:
        """Compute MD5 hashes for all CSV data files."""
        hashes: dict[str, str] = {}
        if not self.data_dir.exists():
            return hashes
        for csv_file in sorted(self.data_dir.glob("*.csv")):
            md5 = hashlib.md5(csv_file.read_bytes()).hexdigest()  # noqa: S324
            hashes[csv_file.name] = md5
        return hashes

    def _load_plot_cache(self) -> dict[str, str]:
        cache_path = self.project_root / PLOT_HASH_FILE
        if cache_path.exists():
            return json.loads(cache_path.read_text())  # type: ignore[no-any-return]
        return {}

    def _save_plot_cache(self, hashes: dict[str, str]) -> None:
        cache_path = self.project_root / PLOT_HASH_FILE
        cache_path.write_text(json.dumps(hashes, indent=2) + "\n")

    def _plots_need_regeneration(self) -> bool:
        """Return True if CSV data changed since the last plot generation."""
        current = self._hash_data_files()
        cached = self._load_plot_cache()
        return current != cached

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

    def generate_plots(self, force: bool = False) -> None:
        """Generate data-driven plots from CSV files into src/static/images/.

        Skips regeneration when CSV data has not changed since the last build
        unless *force* is True.  Plots are written to the static assets
        directory so ``copy_static_assets()`` picks them up.
        """
        images_dir = self.static_dir / "images"
        images_dir.mkdir(exist_ok=True)

        if not force and not self._plots_need_regeneration():
            print("Plots up-to-date (data unchanged) -- skipping.")
            return

        print("Generating data plots from CSV files...")
        original_cwd = os.getcwd()
        try:
            os.chdir(str(self.project_root))
            generate_all_plots(
                data_dir=str(self.data_dir),
                output_dir=str(images_dir),
            )
        finally:
            os.chdir(original_cwd)

        self._save_plot_cache(self._hash_data_files())

    def generate_market_plots(self) -> None:
        """Generate raw ticker and category comparison plots (requires yfinance).

        Writes to src/static/ so ``copy_static_assets()`` picks them up.
        Only called when the user explicitly requests market-data updates.
        """
        from market.plot_functions import (
            create_category_comparison_plots,
            create_raw_ticker_plots,
            create_ticker_dropdown_data,
        )

        images_dir = self.static_dir / "images"
        images_dir.mkdir(exist_ok=True)

        print("Fetching live market data and generating ticker plots...")
        create_raw_ticker_plots(output_dir=str(images_dir / "raw_tickers"))
        create_category_comparison_plots(output_dir=str(images_dir / "category_comparisons"))

        data_dir = self.static_dir / "data"
        data_dir.mkdir(exist_ok=True)
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

        # 1. Generate updated assets into src/static/
        self.generate_plots()
        if include_market_plots:
            self.generate_market_plots()

        # 2. Clean docs/ and copy everything from src/static/
        self.clean_output()
        self.copy_static_assets()

        # 3. Render markdown -> HTML
        self.process_markdown_files()

        print("-" * 50)
        print(f"Build complete -> {self.output_dir}")
