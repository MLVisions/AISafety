"""
LLM configuration — provider-agnostic.

All LLM settings (provider, model, API key, parameters) are read from
a single YAML config file.  No provider-specific defaults or fallbacks.

Default config path: ~/.config/aisafety/llm.yaml
Override with env-var: LLM_CONFIG_PATH=/path/to/llm.yaml

Run ``uv run python -m src.agents.utils.llm_config`` to create or
update the config interactively.

Example llm.yaml
-----------------
model: openai/gpt-5-mini
api_key: sk-...
temperature: 0.3
max_tokens: 4096
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Default location — one file for all LLM settings
_DEFAULT_CONFIG_PATH = Path.home() / ".config" / "aisafety" / "llm.yaml"


@dataclass
class LLMConfig:
    """Snapshot of LLM settings used by every agent."""

    model: str
    api_key: str
    temperature: float | None = None
    max_tokens: int | None = None


def get_config_path() -> Path:
    """Return the resolved config file path."""
    override = os.getenv("LLM_CONFIG_PATH")
    if override:
        return Path(override).expanduser()
    return _DEFAULT_CONFIG_PATH


def get_llm_config() -> LLMConfig:
    """
    Load LLM settings from the YAML config file.

    Raises ``FileNotFoundError`` with setup instructions if the config
    file does not exist.  Raises ``ValueError`` if required fields are
    missing.
    """
    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"LLM config not found at {config_path}\n"
            "Run:  uv run python -m src.agents.utils.llm_config\n"
            "Or set LLM_CONFIG_PATH to point to your config file."
        )

    with open(config_path) as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    model = data.get("model")
    api_key = data.get("api_key")

    if not model:
        raise ValueError(f"'model' is required in {config_path}")
    if not api_key:
        raise ValueError(f"'api_key' is required in {config_path}")

    raw_temp = data.get("temperature")
    raw_tokens = data.get("max_tokens")
    return LLMConfig(
        model=str(model),
        api_key=str(api_key),
        temperature=float(raw_temp) if raw_temp is not None else None,
        max_tokens=int(raw_tokens) if raw_tokens is not None else None,
    )


# ------------------------------------------------------------------
# CLI — interactive config setup
# ------------------------------------------------------------------


def _setup_config() -> None:
    """Interactive CLI to create / update the config file."""
    config_path = get_config_path()

    print("=" * 50)
    print("  AI Safety — LLM Configuration")
    print("=" * 50)
    print(f"\nConfig file: {config_path}\n")

    # Load existing values if file exists
    existing: dict[str, Any] = {}
    if config_path.exists():
        with open(config_path) as f:
            existing = yaml.safe_load(f) or {}
        print("(Current values shown in brackets — press Enter to keep)\n")

    # Prompt for values
    print("Model examples:")
    print("  openai/gpt-5-mini              openai/gpt-4o-mini")
    print("  anthropic/claude-sonnet-4-20250514  gemini/gemini-2.5-flash")
    print("  ollama/llama3                   mistral/mistral-large-latest")
    print()

    model = (
        input(f"  model [{existing.get('model', '')}]: ").strip()
        or existing.get("model", "")
    )
    if not model:
        print("Error: model is required.")
        sys.exit(1)

    api_key = (
        input(f"  api_key [{_mask(existing.get('api_key', ''))}]: ").strip()
        or existing.get("api_key", "")
    )
    if not api_key:
        print("Error: api_key is required.")
        sys.exit(1)

    temperature = (
        input(f"  temperature [{existing.get('temperature', 0.3)}]: ").strip()
        or str(existing.get("temperature", 0.3))
    )
    max_tokens = (
        input(f"  max_tokens [{existing.get('max_tokens', 4096)}]: ").strip()
        or str(existing.get("max_tokens", 4096))
    )

    config_data = {
        "model": model,
        "api_key": api_key,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }

    # Write
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

    # Restrict permissions (owner-only read/write)
    config_path.chmod(0o600)

    print(f"\n✅ Config saved to {config_path}")
    print(f"   model:       {model}")
    print(f"   temperature:  {temperature}")
    print(f"   max_tokens:   {max_tokens}")


def _mask(value: str) -> str:
    """Mask an API key for display, showing only last 4 chars."""
    if not value or len(value) < 8:
        return ""
    return "•" * (len(value) - 4) + value[-4:]


if __name__ == "__main__":
    _setup_config()
