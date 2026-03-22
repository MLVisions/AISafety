#!/usr/bin/env python3
"""
AI Safety Website Builder
Main build script to generate the complete website with optional automation
"""

import argparse
import sys
from pathlib import Path

from src.builders.site_builder import SiteBuilder


def build_basic() -> None:
    """Basic build function without automation"""
    print("AI Safety Website Builder")
    print("=" * 50)

    project_root = Path(__file__).parent
    builder = SiteBuilder(str(project_root))

    try:
        builder.build()
    except Exception as e:
        print(f"\nBuild failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def build_with_automation(mode: str = "full", page: str | None = None) -> None:
    """Build with full automation pipeline via the Orchestrator."""
    from src.agents.orchestrator import Orchestrator

    print("AI Safety Website Builder (Automation Mode)")
    print("=" * 55)

    orch = Orchestrator()

    if mode == "market-data":
        print("Running market data updates only...")
        results = orch.run_market_data()
    elif mode == "content":
        pages = [page] if page else None
        label = f"content research for '{page}'" if page else "content research"
        print(f"Running {label}...")
        results = orch.run_full_cycle(pages=pages, skip_market_data=True, skip_build=True)
    elif mode == "page":
        if not page:
            print("Error: --page is required for 'page' mode")
            sys.exit(1)
        print(f"Running full pipeline for '{page}'...")
        results = orch.run_full_cycle(pages=[page])
    else:
        print("Running full automation cycle...")
        results = orch.run_full_cycle()

    if results.get("success", False):
        print("\nAutomation complete.")
        if "duration" in results:
            print(f"Duration: {results['duration']}")
    else:
        print("\nAutomation had errors:")
        for error in results.get("errors", []):
            print(f"  - {error}")
        sys.exit(1)


def main() -> None:
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="AI Safety Website Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aisafety                                       # Basic build only
  aisafety --auto                                # Full automation cycle
  aisafety --auto market-data                    # Market data updates only
  aisafety --auto content                        # Content research (all pages)
  aisafety --auto content --page economy         # Research one page only
  aisafety --auto page --page economy            # Full pipeline for one page
        """
    )

    parser.add_argument(
        "--auto", "--automation",
        nargs="?",
        const="full",
        choices=["full", "market-data", "content", "page"],
        help="Enable automation mode (default: full)"
    )
    parser.add_argument(
        "--page",
        help="Target a specific page (e.g. economy, technology, society)"
    )

    args = parser.parse_args()

    if args.auto:
        build_with_automation(args.auto, page=args.page)
    else:
        build_basic()


if __name__ == "__main__":
    main()
