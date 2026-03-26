"""CLI entry point for AI Safety website."""

from .build import build_parser, print_result


def main() -> None:
    """Entry point for ``uv run aisafety``."""
    args = build_parser().parse_args()
    command = args.command or "build"

    if command == "build":
        from builders.site_builder import SiteBuilder

        SiteBuilder(".").build(
            include_market_plots=getattr(args, "market_plots", False),
        )

    elif command == "auto":
        from .orchestrator import Orchestrator

        print_result(
            Orchestrator().run_full_cycle(
                pages=[args.page] if args.page else None,
                skip_research=args.skip_research,
                skip_market_data=args.skip_market_data,
                skip_build=args.skip_build,
            )
        )

    elif command == "research":
        from .orchestrator import Orchestrator

        print_result(
            Orchestrator().run_full_cycle(
                pages=[args.page] if args.page else None,
                skip_market_data=True,
                skip_build=True,
            )
        )

    elif command == "market-data":
        from .orchestrator import Orchestrator

        print_result(Orchestrator().run_market_data())

    elif command == "references":
        from .orchestrator import Orchestrator

        print_result(Orchestrator().run_references_only())

    elif command == "llm-config":
        from .utils.llm_config import _setup_config

        _setup_config()
