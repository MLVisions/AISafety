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

from .research_agents import create_research_agent
from .utils.content_update_applier import ContentUpdateApplier
from .utils.content_validation_utils import ContentValidationUtils
from .utils.page_config import get_content_pages, get_page_config

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

    def run_update(
        self,
        pages: list[str] | None = None,
        sections: list[str] | None = None,
        build: bool = True,
        include_plots: bool = False,
    ) -> dict[str, Any]:
        """
        Run the content update pipeline for all (or specified) pages.

        Pipeline per page:
          1. Research - LLM agents gather findings (AI)
          2. Apply    - Write structured updates to src/content/*.md (engineered)
          3. Validate - Check content quality (engineered)

        Cross-page stages (after all pages):
          4. Market data - Fetch tickers and run simulations (only with include_plots)
          5. Build       - Sync references, rebuild HTML (+ plots if include_plots)

        Args:
            pages: List of page names to update. None = all content pages.
            sections: H2 headings to target. None = all sections on each page.
            build: Whether to build the site after updating content.
            include_plots: Also fetch market data and regenerate plots (slow).

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

        # Per-page pipeline
        for page_name in pages:
            logger.info(f"--- Processing {page_name} ---")
            page_report: dict[str, Any] = {}

            try:
                # 1. Research
                research_result = self._research_page(page_name, sections=sections)
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

        # 4. Market data + economic modeling (only when explicitly requested)
        if include_plots:
            try:
                md_result = self._run_investment_pipeline()
                report["stages"]["market_data"] = md_result
            except Exception as e:
                logger.error(f"Market data pipeline failed: {e}")
                report["errors"].append(f"market_data: {e}")

        # 5. Build site (includes references sync, markdown -> HTML, + plots if requested)
        if build:
            try:
                build_result = self._build_site(
                    include_market_plots=include_plots,
                    agent_refs=all_agent_refs or None,
                )
                report["stages"]["build"] = build_result
            except Exception as e:
                logger.error(f"Build failed: {e}")
                report["errors"].append(f"build: {e}")

        report["end"] = datetime.now().isoformat()
        report["duration"] = str(datetime.now() - start)
        return report

    def run_market(self, plots_only: bool = False) -> dict[str, Any]:
        """Fetch market data and run investment pipeline.

        Args:
            plots_only: If True, skip data fetching and only regenerate
                plots from cached CSV data.
        """
        start = datetime.now()
        try:
            if plots_only:
                result = self._regenerate_market_plots()
            else:
                result = self._run_investment_pipeline()
            result.setdefault("duration", str(datetime.now() - start))
            return result
        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)],
                "duration": str(datetime.now() - start),
            }

    # ------------------------------------------------------------------
    # Pipeline stages
    # ------------------------------------------------------------------

    def _research_page(
        self, page_name: str, sections: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run section-level research agents for a page and return structured findings."""
        config = get_page_config(page_name)
        content_path = str(self.content_dir / config.content_file)

        all_updates: list[dict[str, Any]] = []
        all_refs: list[dict[str, Any]] = []

        agents = config.section_agents
        if sections:
            agents = [sa for sa in agents if sa.section in sections]

        for sa in agents:
            logger.info(f"  Running {sa.agent} ({sa.task}) for {page_name} § {sa.section}")
            try:
                agent = create_research_agent(sa.agent, sa.task)
                result = agent.research_page(page_name, content_path, target_section=sa.section)
                updates = result.get("updates", [])
                logger.info(f"  Agent returned {len(updates)} updates")
                for i, u in enumerate(updates):
                    logger.info(
                        f"    [{i}] section={u.get('section_title', '')!r} "
                        f"confidence={u.get('confidence', 0)} "
                        f"has_content={bool(u.get('new_content'))}"
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

    def _build_site(
        self,
        include_market_plots: bool = False,
        agent_refs: list[dict[str, Any]] | None = None,
        pages: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Rebuild the static site from src/content/*.md -> docs/*.html.

        References are synced as part of each build so references.md is
        always current.  Delegates to ``SiteBuilder.build()``.
        """
        try:
            from builders.site_builder import SiteBuilder

            builder = SiteBuilder(str(self.project_root))
            builder.build(
                include_market_plots=include_market_plots,
                agent_refs=agent_refs,
                pages=pages,
            )

            return {"success": True}
        except Exception as e:
            logger.error(f"Site build failed: {e}")
            return {"success": False, "error": str(e)}

    def _regenerate_market_plots(self) -> dict[str, Any]:
        """Regenerate market plots from cached data without fetching."""
        try:
            from builders.site_builder import SiteBuilder

            builder = SiteBuilder(str(self.project_root))
            builder.generate_market_plots()
            return {"success": True}
        except Exception as e:
            logger.error(f"Plot regeneration failed: {e}")
            return {"success": False, "error": str(e)}

    def _run_investment_pipeline(self) -> dict[str, Any]:
        """Run the investment/market data pipeline."""
        try:
            from market.investment_pipeline import run_complete_investment_pipeline

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
