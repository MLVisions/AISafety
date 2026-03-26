"""
CLI argument parser and helpers for the AI Safety website.
"""

import argparse
import sys
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="aisafety",
        description="AI Safety Website — build and automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  aisafety                              Build site from existing content
  aisafety build                        Build site (explicit)
  aisafety build --market-plots         Build + regenerate market plots
  aisafety auto                         Full automation cycle
  aisafety auto --page economy          Full pipeline for one page
  aisafety research --page economy      Research one page only
  aisafety market-data                  Fetch market data + simulations
  aisafety references                   Sync references.md
  aisafety llm-config                   Configure LLM provider/model
""",
    )

    sub = parser.add_subparsers(dest="command")

    p_build = sub.add_parser("build", help="Build the static site")
    p_build.add_argument(
        "--market-plots", action="store_true",
        help="Also fetch live data and regenerate market plots",
    )

    p_auto = sub.add_parser("auto", help="Full automation cycle")
    p_auto.add_argument("--page", help="Target a single page")
    p_auto.add_argument("--skip-research", action="store_true")
    p_auto.add_argument("--skip-market-data", action="store_true")
    p_auto.add_argument("--skip-build", action="store_true")

    p_research = sub.add_parser("research", help="Content research only (no build)")
    p_research.add_argument("--page", help="Target a single page")

    sub.add_parser("market-data", help="Fetch market data and run simulations")
    sub.add_parser("references", help="Sync references.md from content citations")
    sub.add_parser("llm-config", help="Configure LLM provider/model interactively")

    return parser


def print_result(result: dict[str, Any]) -> None:
    """Print a pipeline result summary and ``sys.exit(1)`` on failure."""
    success = result.get("success", False)
    duration = result.get("duration", "")
    if success:
        print(f"\n✓ Done.{f'  ({duration})' if duration else ''}")
    else:
        print(f"\n✗ Finished with errors.{f'  ({duration})' if duration else ''}")
        for err in result.get("errors", []):
            print(f"  - {err}")
        sys.exit(1)
