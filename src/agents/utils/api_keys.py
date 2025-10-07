"""
API key management utilities for CrewAI agents
Provides secure access to API keys from standard locations
"""

import os
from pathlib import Path


def get_openai_api_key() -> str:
    """
    Read OpenAI API key from standard locations and set environment variable.
    Locations checked in order of preference:
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
                        # Set environment variable for agents to use
                        os.environ['OPENAI_API_KEY'] = api_key
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
        service: Service name (e.g., 'openai', 'gemini', 'polygon')

    Returns:
        API key if found, None otherwise
    """
    env_var = f"{service.upper()}_API_KEY"
    return os.getenv(env_var)


def setup_agent_environment() -> None:
    """
    Setup environment for CrewAI agents
    Call this before initializing any agents to ensure proper API key setup
    """
    # Get OpenAI API key (this will set the environment variable)
    try:
        get_openai_api_key()
    except ValueError:
        # Key not found, let the calling code handle it
        pass

    # Set any other environment variables needed for agents
    if not os.getenv('SERPER_API_KEY'):
        serper_key = get_api_key('serper')
        if serper_key:
            os.environ['SERPER_API_KEY'] = serper_key
