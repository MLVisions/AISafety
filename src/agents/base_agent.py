"""
Base agent class for LLM-powered research and content agents.

Provider-agnostic — works with any provider supported by litellm.
Agent role/goal/backstory are loaded from agents.yaml so non-coders can
tweak behaviour by editing the YAML file.

Configure your provider/model via:
  uv run python -m src.agents.utils.llm_config
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

import yaml

from .utils.llm_config import get_llm_config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration loader
# ---------------------------------------------------------------------------

_AGENTS_YAML: dict[str, Any] | None = None


def _load_agents_yaml() -> dict[str, Any]:
    """Load and cache agents.yaml configuration."""
    global _AGENTS_YAML
    if _AGENTS_YAML is None:
        yaml_path = Path(__file__).parent / "agents.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"agents.yaml not found at {yaml_path}")
        with open(yaml_path) as f:
            _AGENTS_YAML = yaml.safe_load(f) or {}
    return _AGENTS_YAML


# ---------------------------------------------------------------------------
# Base agent
# ---------------------------------------------------------------------------


class BaseAgent:
    """
    Lightweight LLM agent that reads its personality from agents.yaml.

    Subclasses override ``build_prompt`` to inject page-specific context
    and ``parse_response`` to extract structured output.
    """

    def __init__(self, agent_name: str) -> None:
        config = _load_agents_yaml()
        if agent_name not in config:
            raise ValueError(f"Agent '{agent_name}' not found in agents.yaml")
        self.agent_name = agent_name
        self.role: str = config[agent_name]["role"]
        self.goal: str = config[agent_name]["goal"]
        self.backstory: str = config[agent_name]["backstory"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, task_description: str, context: str = "", **kwargs: Any) -> dict[str, Any]:
        """
        Execute the agent's task via the configured LLM provider.

        Returns a dict with at minimum ``{"raw": <str>, "success": True/False}``.
        Subclasses may add structured fields via ``parse_response``.
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task_description, context)

        try:
            raw_response = self._call_llm(system_prompt, user_prompt, **kwargs)
            result = self.parse_response(raw_response)
            result.setdefault("raw", raw_response)
            result.setdefault("success", True)
            return result
        except Exception as e:
            logger.error(f"Agent '{self.agent_name}' failed: {e}")
            return {"success": False, "error": str(e), "raw": ""}

    # ------------------------------------------------------------------
    # Override-able hooks
    # ------------------------------------------------------------------

    def parse_response(self, raw: str) -> dict[str, Any]:
        """
        Parse the raw LLM response into structured data.

        Default implementation tries to find a JSON block; subclasses can
        override for custom parsing.
        """
        # Try to extract JSON from the response
        json_str = self._extract_json(raw)
        if json_str:
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    return parsed
                return {"data": parsed}
            except json.JSONDecodeError:
                pass
        return {"raw": raw}

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_system_prompt(self) -> str:
        return (
            f"You are a {self.role}.\n\n"
            f"Goal: {self.goal}\n\n"
            f"Background: {self.backstory}\n\n"
            "Always respond with well-structured, evidence-based content. "
            "Include source URLs for every factual claim."
        )

    def _build_user_prompt(self, task: str, context: str) -> str:
        parts = [task]
        if context:
            parts.append(f"\n\nCurrent content for reference:\n{context}")
        return "\n".join(parts)

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **_kwargs: Any,
    ) -> str:
        """Call the LLM via litellm (provider-agnostic)."""
        import litellm

        cfg = get_llm_config()

        kwargs: dict[str, Any] = {
            "model": model or cfg.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "api_key": cfg.api_key,
        }

        # Only include optional params when explicitly set in config
        temp = temperature if temperature is not None else cfg.temperature
        if temp is not None:
            kwargs["temperature"] = temp
        tokens = max_tokens if max_tokens is not None else cfg.max_tokens
        if tokens is not None:
            kwargs["max_completion_tokens"] = tokens

        response = litellm.completion(**kwargs)
        return response.choices[0].message.content or ""

    @staticmethod
    def _extract_json(text: str) -> str | None:
        """Extract the first valid JSON object or array from *text*."""
        # Look inside ```json ... ``` fences first
        m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
        if m:
            return m.group(1)
        m = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", text)
        if m:
            return m.group(1)

        # Try each '{' as a potential JSON start, validate with json.loads
        for i, ch in enumerate(text):
            if ch == '{':
                # Find matching '}' from the end backwards
                for j in range(len(text) - 1, i, -1):
                    if text[j] == '}':
                        candidate = text[i:j + 1]
                        try:
                            json.loads(candidate)
                            return candidate
                        except json.JSONDecodeError:
                            continue
        return None
