"""
LLM configuration — provider-agnostic.

All LLM settings are read from a single YAML config file.
API keys are stored in separate files and referenced by path.

Default config path: ~/.config/aisafety/aisafety_config.yaml
Override with env-var: AISAFETY_CONFIG_PATH=/path/to/config.yaml

Run ``uv run aisafety llm-config`` to create or update interactively.

Example aisafety_config.yaml
-----------------------------
model: openai/gpt-5.4
api_keys:
  openai: ~/.config/api_keys/openai/api_key.txt
  anthropic: ~/.config/api_keys/anthropic/api_key.txt
temperature: 0.7
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Default location — one file for all settings
_DEFAULT_CONFIG_PATH = Path.home() / ".config" / "aisafety" / "aisafety_config.yaml"


@dataclass
class LLMConfig:
    """Snapshot of LLM settings used by every agent."""

    model: str
    api_key: str
    temperature: float | None = None


def get_config_path() -> Path:
    """Return the resolved config file path."""
    override = os.getenv("AISAFETY_CONFIG_PATH")
    if override:
        return Path(override).expanduser()
    return _DEFAULT_CONFIG_PATH


def _read_key_file(path_str: str) -> str:
    """Read an API key from a file, expanding ~ and stripping whitespace."""
    key_path = Path(path_str).expanduser()
    if not key_path.exists():
        raise FileNotFoundError(f"API key file not found: {key_path}")
    return key_path.read_text().strip()


def get_llm_config() -> LLMConfig:
    """
    Load LLM settings from the YAML config file.

    The ``api_keys`` mapping stores ``provider: /path/to/key.txt``.
    The provider is derived from the model string (e.g. ``openai/gpt-5.4``
    → ``openai``).
    """
    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config not found at {config_path}\n"
            "Run:  uv run aisafety llm-config\n"
            "Or set AISAFETY_CONFIG_PATH to point to your config file."
        )

    with open(config_path) as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    model = data.get("model")
    if not model:
        raise ValueError(f"'model' is required in {config_path}")

    # Derive provider from model string (e.g. "openai/gpt-5.4" -> "openai")
    provider = str(model).split("/")[0] if "/" in str(model) else str(model)

    # Resolve API key from file path
    api_keys: dict[str, str] = data.get("api_keys", {})
    key_path = api_keys.get(provider)
    if not key_path:
        raise ValueError(
            f"No API key path for provider '{provider}' in {config_path}\n"
            f"Add to api_keys:\n  {provider}: /path/to/api_key.txt"
        )
    api_key = _read_key_file(key_path)

    raw_temp = data.get("temperature")
    return LLMConfig(
        model=str(model),
        api_key=api_key,
        temperature=float(raw_temp) if raw_temp is not None else None,
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
    print("Model examples (use litellm provider/model format):")
    print("  openai/gpt-5.4                 openai/o3-mini")
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

    # Derive provider from model
    provider = model.split("/")[0] if "/" in model else model
    existing_keys: dict[str, str] = existing.get("api_keys", {})

    print(f"\n  Provider detected: {provider}")
    print("  Enter the path to a file containing the API key.")
    key_path = (
        input(f"  api_key file [{existing_keys.get(provider, '')}]: ").strip()
        or existing_keys.get(provider, "")
    )
    if not key_path:
        print("Error: api_key file path is required.")
        sys.exit(1)

    # Validate the key file exists
    resolved = Path(key_path).expanduser()
    if not resolved.exists():
        print(f"Warning: key file not found at {resolved}")
        print("  You can create it later; config will be saved anyway.")

    existing_keys[provider] = key_path

    temp_default = existing.get("temperature", "")
    temperature_str = (
        input(f"  temperature [{temp_default}] (Enter to skip): ").strip()
        or str(temp_default) if temp_default != "" else ""
    )

    config_data: dict[str, Any] = {
        "model": model,
        "api_keys": existing_keys,
    }
    if temperature_str:
        config_data["temperature"] = float(temperature_str)

    # Write
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

    # Restrict permissions (owner-only read/write)
    config_path.chmod(0o600)

    print(f"\n✅ Config saved to {config_path}")
    print(f"   model:       {model}")
    print(f"   api_keys:    {existing_keys}")


# ------------------------------------------------------------------
# Programmatic config helpers (used by CLI flags and future Shiny app)
# ------------------------------------------------------------------


def _load_config_data() -> dict[str, Any]:
    """Load raw config data from YAML, or empty dict if missing."""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def _save_config_data(data: dict[str, Any]) -> None:
    """Write config data to YAML and restrict permissions."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    config_path.chmod(0o600)


def set_model(model: str) -> None:
    """Set the default model in the config file."""
    data = _load_config_data()
    data["model"] = model
    _save_config_data(data)


def set_api_key(provider: str, key_or_path: str) -> None:
    """Set the API key for a provider.

    *key_or_path* can be either a literal key string or a path to a
    file containing the key.  If the value looks like a file path
    (starts with ``/``, ``~``, or ``.``) and the resolved path exists,
    it is stored as a file reference; otherwise the value is written
    to the default key file location and that path is stored.
    """
    data = _load_config_data()
    api_keys: dict[str, str] = data.setdefault("api_keys", {})

    resolved = Path(key_or_path).expanduser()
    if resolved.is_file():
        # Store as file reference
        api_keys[provider] = key_or_path
    else:
        # Treat as literal key — write to standard location
        key_dir = Path.home() / ".config" / "api_keys" / provider
        key_dir.mkdir(parents=True, exist_ok=True)
        key_file = key_dir / "api_key.txt"
        key_file.write_text(key_or_path.strip())
        key_file.chmod(0o600)
        api_keys[provider] = str(key_file)

    _save_config_data(data)


def show_config() -> None:
    """Print the current configuration with masked API keys."""
    data = _load_config_data()
    if not data:
        print("No configuration found. Run:  uv run aisafety config")
        return

    print(f"Config file: {get_config_path()}")
    print(f"  model:       {data.get('model', '(not set)')}")

    temp = data.get("temperature")
    if temp is not None:
        print(f"  temperature: {temp}")

    api_keys: dict[str, str] = data.get("api_keys", {})
    for provider, key_path in api_keys.items():
        try:
            key = _read_key_file(key_path)
            print(f"  {provider} key:  {_mask(key)}  ({key_path})")
        except FileNotFoundError:
            print(f"  {provider} key:  (file not found: {key_path})")


def _mask(value: str) -> str:
    """Mask an API key for display, showing only last 4 chars."""
    if not value or len(value) < 8:
        return ""
    return "•" * (len(value) - 4) + value[-4:]


if __name__ == "__main__":
    _setup_config()
