"""
Automation orchestrator - coordinates the full update pipeline.

Per-page stages:
  1. Research    - LLM agents gather findings (AI)
  2. Apply       - Write structured updates to src/content/*.md (engineered)
  3. Validate    - Check content quality (engineered)

Cross-page stages (after all pages complete):
  4. References  - Sync references.md from citations across all content files
  5. Market data - Fetch ticker data and run investment simulations (if needed)
  6. Build       - Generate plots and rebuild docs/*.html from markdown (no AI)
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .reference_manager import sync_references_file
from .research_agents import create_research_agent
from .utils.content_update_applier import ContentUpdateApplier
from .utils.content_validation_utils import ContentValidationUtils
from .utils.page_config import PAGE_CONFIGS, get_content_pages, get_page_config

logger = logging.getLogger(__name__)


class Orchestrator:
    """Central automation controller for the AI Safety website."""

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.content_dir = self.project_root / "src" / "content"
        self.data_dir = self.project_root / "src" / "data"
        self.docs_dir = self.project_root / "docs"

        self.content_applier = ContentUpdateApplier(str(self.content_dir))
        self.content_validator = ContentValidationUtils(str(self.content_dir))

        self._setup_logging()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_full_cycle(
        self,
        pages: list[str] | None = None,
        skip_research: bool = False,
        skip_market_data: bool = False,
        skip_build: bool = False,
    ) -> dict[str, Any]:
        """
        Run the complete automation cycle for all (or specified) pages.

        Pipeline per page:
          1. Research - LLM agents gather findings (AI)
          2. Apply    - Write structured updates to src/content/*.md (engineered)
          3. Validate - Check content quality (engineered)

        Cross-page stages (after all pages):
          4. References  - Sync references.md from citations in all content files
          5. Market data - Fetch tickers and run simulations (if any page needs it)
          6. Build       - Regenerate plots and rebuild docs/*.html from markdown

        Args:
            pages: List of page names to update. None = all content pages.
            skip_research: Skip the LLM research step (useful for testing).
            skip_market_data: Skip market data fetching and economic modeling.
            skip_build: Skip plot regeneration and the final site build.

        Returns:
            Report dict with per-stage results.
        """
        start = datetime.now()
        pages = pages or get_content_pages()

        report: dict[str, Any] = {
            "start": start.isoformat(),
            "pages": pages,
            "stages": {},
            "success": True,
            "errors": [],
        }

        # Collect all agent references across pages
        all_agent_refs: list[dict[str, Any]] = []
        needs_market_data = False

        # Per-page pipeline
        for page_name in pages:
            logger.info(f"--- Processing {page_name} ---")
            page_report: dict[str, Any] = {}

            config = get_page_config(page_name)
            if config.has_data_fetching:
                needs_market_data = True

            try:
                # 1. Research
                if not skip_research:
                    research_result = self._research_page(page_name)
                    page_report["research"] = {
                        "updates_found": len(research_result.get("updates", [])),
                        "refs_found": len(research_result.get("references", [])),
                    }
                    all_agent_refs.extend(research_result.get("references", []))

                    # 2. Apply updates to markdown
                    updates = research_result.get("updates", [])
                    if updates:
                        apply_result = self._apply_updates(page_name, updates)
                        page_report["updates"] = apply_result
                else:
                    page_report["research"] = {"skipped": True}

                # 3. Validate
                validation = self._validate_page(page_name)
                page_report["validation"] = {
                    "quality_score": validation.get("quality_score", 0),
                    "issues": len(validation.get("issues", [])),
                }

            except Exception as e:
                logger.error(f"Page {page_name} failed: {e}")
                page_report["error"] = str(e)
                report["success"] = False
                report["errors"].append(f"{page_name}: {e}")

            report["stages"][page_name] = page_report

        # Cross-page stages
        try:
            # 4. Sync references
            ref_result = sync_references_file(
                content_dir=str(self.content_dir),
                agent_refs=all_agent_refs if all_agent_refs else None,
            )
            report["stages"]["references"] = ref_result
        except Exception as e:
            logger.error(f"Reference sync failed: {e}")
            report["errors"].append(f"references: {e}")

        # 5. Market data + economic modeling (if any page needs it)
        if needs_market_data and not skip_market_data:
            try:
                md_result = self._run_investment_pipeline()
                report["stages"]["market_data"] = md_result
            except Exception as e:
                logger.error(f"Market data pipeline failed: {e}")
                report["errors"].append(f"market_data: {e}")

        # 6. Build site (includes plot generation + markdown -> HTML)
        if not skip_build:
            try:
                # If we just fetched market data, regenerate market plots too
                build_result = self._build_site(
                    include_market_plots=needs_market_data and not skip_market_data,
                )
                report["stages"]["build"] = build_result
            except Exception as e:
                logger.error(f"Build failed: {e}")
                report["errors"].append(f"build: {e}")

        report["end"] = datetime.now().isoformat()
        report["duration"] = str(datetime.now() - start)
        return report

    def run_page(self, page_name: str, skip_build: bool = True) -> dict[str, Any]:
        """Run the pipeline for a single page."""
        return self.run_full_cycle(pages=[page_name], skip_build=skip_build)

    def run_build_only(self) -> dict[str, Any]:
        """Just rebuild the site (no research/updates)."""
        return self._build_site()

    def run_references_only(self) -> dict[str, Any]:
        """Just sync references from content files."""
        return sync_references_file(content_dir=str(self.content_dir))

    def run_market_data(self) -> dict[str, Any]:
        """Fetch market data and run investment pipeline."""
        return self._run_investment_pipeline()

    # ------------------------------------------------------------------
    # Pipeline stages
    # ------------------------------------------------------------------

    def _research_page(self, page_name: str) -> dict[str, Any]:
        """Run section-level research agents for a page and return structured findings."""
        config = get_page_config(page_name)
        content_path = str(self.content_dir / config.content_file)

        all_updates: list[dict[str, Any]] = []
        all_refs: list[dict[str, Any]] = []

        for sa in config.section_agents:
            logger.info(f"  Running {sa.agent} ({sa.task}) for {page_name} § {sa.section}")
            try:
                agent = create_research_agent(sa.agent, sa.task)
                result = agent.research_page(page_name, content_path, target_section=sa.section)
                updates = result.get("updates", [])
                logger.info(f"  Agent returned {len(updates)} updates")
                for i, u in enumerate(updates):
                    logger.info(
                        f"    [{i}] type={u.get('update_type')} "
                        f"section={u.get('section_title', '')!r} "
                        f"has_new_content={'new_content' in u and bool(u['new_content'])}"
                    )
                all_updates.extend(updates)
                # Tag each reference with the section it came from
                for ref in result.get("references", []):
                    ref.setdefault("originating_section", sa.section)
                all_refs.extend(result.get("references", []))
            except Exception as e:
                logger.warning(f"  Agent {sa.agent}/{sa.task} failed: {e}")

        return {"updates": all_updates, "references": all_refs}

    def _apply_updates(self, page_name: str, updates: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply structured updates to a page's markdown file."""
        config = get_page_config(page_name)
        content_path = str(self.content_dir / config.content_file)
        return self.content_applier.apply_updates(content_path, updates)

    def _validate_page(self, page_name: str) -> dict[str, Any]:
        """Run engineered validation on a page."""
        config = get_page_config(page_name)
        return self.content_validator.validate_single_file(config.content_file)

    def _build_site(self, include_market_plots: bool = False) -> dict[str, Any]:
        """
        Rebuild the static site from src/content/*.md -> docs/*.html.

        Delegates to ``SiteBuilder.build()`` which generates plots into
        src/static/, then cleans docs/ and copies everything over.
        """
        try:
            from src.builders.site_builder import SiteBuilder

            builder = SiteBuilder(str(self.project_root))
            builder.build(include_market_plots=include_market_plots)

            return {"success": True}
        except Exception as e:
            logger.error(f"Site build failed: {e}")
            return {"success": False, "error": str(e)}

    def _run_investment_pipeline(self) -> dict[str, Any]:
        """Run the investment/market data pipeline."""
        try:
            from .investment_pipeline import run_complete_investment_pipeline

            result = run_complete_investment_pipeline(
                output_dir=str(self.data_dir),
                generate_visualizations=True,
                update_plots=True,
                time_horizons=[3, 5, 10],
            )
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Investment pipeline failed: {e}")
            return {"success": False, "error": str(e)}

    def _verify_build_output(self) -> dict[str, Any]:
        """Check that the build produced expected output files."""
        expected = [f"{p}.html" for p in PAGE_CONFIGS] + ["style.css", "script.js"]
        missing = [f for f in expected if not (self.docs_dir / f).exists()]
        return {"success": len(missing) == 0, "missing": missing}

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _setup_logging(self) -> None:
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"automation_{datetime.now():%Y%m%d_%H%M%S}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AI Safety Website Automation")
    parser.add_argument(
        "mode",
        nargs="?",
        default="full",
        choices=["full", "build", "references", "market-data", "page"],
        help="Automation mode",
    )
    parser.add_argument("--page", help="Page name (for 'page' mode)")
    parser.add_argument("--skip-research", action="store_true")
    parser.add_argument("--skip-market-data", action="store_true")
    parser.add_argument("--skip-build", action="store_true")

    args = parser.parse_args()
    orch = Orchestrator()

    if args.mode == "build":
        result = orch.run_build_only()
    elif args.mode == "references":
        result = orch.run_references_only()
    elif args.mode == "market-data":
        result = orch.run_market_data()
    elif args.mode == "page":
        if not args.page:
            parser.error("--page required for 'page' mode")
        result = orch.run_page(args.page)
    else:
        result = orch.run_full_cycle(
            skip_research=args.skip_research,
            skip_market_data=args.skip_market_data,
            skip_build=args.skip_build,
        )

    success = result.get("success", False)
    print(f"\n{'OK' if success else 'FAILED'}: {result.get('duration', 'N/A')}")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
