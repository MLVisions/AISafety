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
  aisafety build --page economy         Build one page only
  aisafety build --plots                Build + regenerate market plots
  aisafety update                       Research + apply + validate + build
  aisafety update --page economy        Full pipeline for one page
  aisafety update --page economy --plots  Update + market data + plots
  aisafety update --page economy --section "Geopolitical & Market Risks"
  aisafety update --no-build            Research + apply only (no site build)
  aisafety market                       Fetch market data + simulations + plots
  aisafety market --plots-only          Regenerate plots from cached data
  aisafety config                       Interactive LLM configuration
  aisafety config --show                Show current configuration
  aisafety config --model openai/gpt-5  Set default model
  aisafety config --set-key openai key  Set API key for a provider
""",
    )

    sub = parser.add_subparsers(dest="command")

    p_build = sub.add_parser("build", help="Build the static site from markdown")
    p_build.add_argument("--page", help="Build a single page only")
    p_build.add_argument(
        "--plots", action="store_true",
        help="Also regenerate market plots from cached data",
    )

    p_update = sub.add_parser("update", help="Research, apply updates, validate, and build")
    p_update.add_argument("--page", help="Target a single page")
    p_update.add_argument(
        "--section", action="append", metavar="HEADING",
        help="Target specific H2 section(s); can be repeated",
    )
    p_update.add_argument(
        "--no-build", action="store_true",
        help="Skip the site build step (research + apply + validate only)",
    )
    p_update.add_argument(
        "--plots", action="store_true",
        help="Also fetch market data and regenerate plots (slow)",
    )

    p_market = sub.add_parser("market", help="Fetch market data and run simulations")
    p_market.add_argument(
        "--plots-only", action="store_true",
        help="Skip data fetching; regenerate plots from cached CSV",
    )

    p_config = sub.add_parser("config", help="Configure LLM provider and model")
    p_config.add_argument("--show", action="store_true", help="Show current configuration")
    p_config.add_argument("--model", help="Set default model (e.g. openai/gpt-5.4)")
    p_config.add_argument(
        "--set-key", nargs=2, metavar=("PROVIDER", "KEY_OR_PATH"),
        help="Set API key for a provider (value or path to key file)",
    )

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
