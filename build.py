#!/usr/bin/env python3
"""
AI Safety Website Builder
Main build script to generate the complete website
"""

import sys
from pathlib import Path

# Add src to path so we can import our builders
sys.path.insert(0, str(Path(__file__).parent / "src"))

from builders.site_builder import SiteBuilder


def main() -> None:
    """Main build function"""
    print("🚀 AI Safety Website Builder")
    print("=" * 40)

    # Get project root
    project_root = Path(__file__).parent

    # Create and run site builder
    builder = SiteBuilder(str(project_root))

    try:
        builder.build()
        print("\nBuild completed successfully!")
        print(f"Website built in: {builder.output_dir}")

    except Exception as e:
        print(f"\n Build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
