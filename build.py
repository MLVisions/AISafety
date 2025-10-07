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
    print("🚀 AI Safety Website Builder (Basic Mode)")
    print("=" * 50)

    # Get project root
    project_root = Path(__file__).parent

    # Create and run site builder
    builder = SiteBuilder(str(project_root))

    try:
        builder.build()
        print("\n✅ Build completed successfully!")
        print(f"Website built in: {builder.output_dir}")

    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def build_with_automation(mode: str = "full") -> None:
    """Build with full automation pipeline"""
    try:
        from src.agents.automation_controller import AutomationController

        print("🤖 AI Safety Website Builder (Automation Mode)")
        print("=" * 55)

        controller = AutomationController()

        if mode == "market-data":
            print("📈 Running market data updates only...")
            results = controller.run_market_data_only()
        elif mode == "content":
            print("📝 Running content research only...")
            results = controller.run_content_research_only()
        else:
            print("🔄 Running full automation cycle...")
            results = controller.run_full_automation_cycle()

        if results['success']:
            print("\n✅ Automated build completed successfully!")
            if 'total_duration' in results:
                print(f"⏱️  Total time: {results['total_duration']}")
        else:
            print("\n❌ Automated build failed:")
            for error in results.get('errors', []):
                print(f"  • {error}")
            sys.exit(1)

    except ImportError:
        print("⚠️  Automation system not available, falling back to basic build...")
        build_basic()
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        print("⚠️  Falling back to basic build...")
        build_basic()


def main() -> None:
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="AI Safety Website Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Basic build only
  python build.py --auto             # Full automation cycle
  python build.py --auto market-data # Market data updates only
  python build.py --auto content     # Content research only
        """
    )

    parser.add_argument(
        "--auto", "--automation",
        nargs="?",
        const="full",
        choices=["full", "market-data", "content"],
        help="Enable automation mode (default: full)"
    )

    args = parser.parse_args()

    if args.auto:
        build_with_automation(args.auto)
    else:
        build_basic()


if __name__ == "__main__":
    main()
