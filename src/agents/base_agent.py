"""
Base agent class for LLM-powered research and content agents.

Provider-agnostic — works with any provider supported by litellm.
Agent role/goal/backstory are loaded from agents.yaml so non-coders can
tweak behaviour by editing the YAML file.

Configure your provider/model via:
  uv run aisafety llm-config
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

import litellm
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

    def run(
        self,
        task_description: str,
        context: str = "",
        images: list[dict[str, str]] | None = None,
        documents: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute the agent's task via the configured LLM provider.

        Args:
            task_description: The task prompt for the agent.
            context: Additional context (e.g. current page content).
            images: Optional list of dicts with ``url`` keys containing
                ``data:<mime>;base64,...`` strings for vision-capable models.
            documents: Optional list of dicts with ``mime`` and ``data``
                (base64) keys for PDF document attachments.

        Returns a dict with at minimum ``{"raw": <str>, "success": True/False}``.
        Subclasses may add structured fields via ``parse_response``.
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task_description, context)

        try:
            raw_response = self._call_llm(
                system_prompt, user_prompt,
                images=images, documents=documents,
                **kwargs,
            )
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
        images: list[dict[str, str]] | None = None,
        documents: list[dict[str, str]] | None = None,
        **_kwargs: Any,
    ) -> str:
        """Call the LLM via litellm (provider-agnostic).

        When *images* are provided and the model supports vision, image
        content blocks are included.  When *documents* (PDFs) are provided
        and the model supports PDF input, file content blocks are included.
        Unsupported attachment types are logged and skipped.
        """
        from litellm.utils import supports_pdf_input

        cfg = get_llm_config()
        resolved_model = model or cfg.model

        can_vision = litellm.supports_vision(model=resolved_model)
        can_pdf = supports_pdf_input(resolved_model, None)

        # Determine which attachments the model can actually accept
        send_images = images if (images and can_vision) else None
        send_docs = documents if (documents and can_pdf) else None

        if images and not can_vision:
            logger.warning(
                "Model %s does not support vision; %d image(s) will be skipped",
                resolved_model, len(images),
            )
        if documents and not can_pdf:
            logger.warning(
                "Model %s does not support PDF input; %d document(s) will be skipped",
                resolved_model, len(documents),
            )

        # Build user message — multimodal when attachments are accepted
        user_message: dict[str, Any]
        if send_images or send_docs:
            user_content: list[dict[str, Any]] = [
                {"type": "text", "text": user_prompt},
            ]
            for img in (send_images or []):
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": img["url"]},
                })
            for doc in (send_docs or []):
                user_content.append({
                    "type": "file",
                    "file": {
                        "file_data": f"data:{doc['mime']};base64,{doc['data']}",
                    },
                })
            user_message = {"role": "user", "content": user_content}
            logger.info(
                "Including %d image(s) and %d document(s) in request",
                len(send_images or []),
                len(send_docs or []),
            )
        else:
            user_message = {"role": "user", "content": user_prompt}

        kwargs: dict[str, Any] = {
            "model": resolved_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                user_message,
            ],
            "api_key": cfg.api_key,
        }

        temp = temperature if temperature is not None else cfg.temperature
        if temp is not None:
            kwargs["temperature"] = temp

        response = litellm.completion(**kwargs, drop_params=True)
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
