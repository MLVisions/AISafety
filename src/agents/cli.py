"""CLI entry point for AI Safety website."""

from .build import build_parser, print_result


def main() -> None:
    """Entry point for ``uv run aisafety``."""
    args = build_parser().parse_args()
    command = args.command or "build"

    if command == "build":
        from builders.site_builder import SiteBuilder

        pages = [args.page] if getattr(args, "page", None) else None
        builder = SiteBuilder(".")
        builder.build(
            include_market_plots=getattr(args, "plots", False),
            pages=pages,
        )

    elif command == "update":
        from .orchestrator import Orchestrator

        print_result(
            Orchestrator().run_update(
                pages=[args.page] if getattr(args, "page", None) else None,
                sections=getattr(args, "section", None),
                build=not getattr(args, "no_build", False),
                include_plots=getattr(args, "plots", False),
            )
        )

    elif command == "market":
        from .orchestrator import Orchestrator

        print_result(
            Orchestrator().run_market(
                plots_only=getattr(args, "plots_only", False),
            )
        )

    elif command == "config":
        from .utils.llm_config import _setup_config, set_api_key, set_model, show_config

        if getattr(args, "show", False):
            show_config()
        elif getattr(args, "model", None):
            set_model(args.model)
            print(f"✓ Model set to {args.model}")
        elif getattr(args, "set_key", None):
            provider, key_or_path = args.set_key
            set_api_key(provider, key_or_path)
            print(f"✓ API key set for {provider}")
        else:
            _setup_config()
