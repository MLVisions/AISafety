"""
API key management utilities for CrewAI agents
Provides secure access to API keys from standard locations
"""

import os
from pathlib import Path


def get_openai_api_key() -> str:
    """
    Read OpenAI API key from standard locations in order of preference:
    1. Environment variable OPENAI_API_KEY
    2. ~/.config/personal_gpt/api_key.txt

    Returns:
        str: The OpenAI API key

    Raises:
        ValueError: If no API key is found in any location
    """
    # First, check environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        return api_key.strip()

    # Check standard config locations
    config_paths = [
        Path.home() / '.config' / 'personal_gpt' / 'api_key.txt'
    ]

    for path in config_paths:
        if path.exists() and path.is_file():
            try:
                with open(path, encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key:
                        return api_key
            except OSError:
                # Continue to next path if this one fails
                continue

    raise ValueError(
        "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
        "or create ~/.config/personal_gpt/api_key.txt with your API key."
    )


def get_api_key(service: str) -> str | None:
    """
    Generic API key getter for various services

    Args:
        service: Service name (e.g., 'serper', 'alpha_vantage', 'polygon')

    Returns:
        API key if found, None otherwise
    """
    env_var = f"{service.upper()}_API_KEY"
    return os.getenv(env_var)


def set_openai_key_env() -> None:
    """
    Set OpenAI API key as environment variable if not already set
    Useful for agents that need the key in environment
    """
    if not os.getenv('OPENAI_API_KEY'):
        try:
            api_key = get_openai_api_key()
            os.environ['OPENAI_API_KEY'] = api_key
        except ValueError:
            # Key not found, let the calling code handle it
            pass
