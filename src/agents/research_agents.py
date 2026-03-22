"""
Research agent implementations.

Each agent wraps BaseAgent with page-specific prompt engineering.
The agents read current content, ask the LLM for updates, and return
structured findings with references that feed into the content update
and reference management pipelines.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

from .base_agent import BaseAgent
from .utils.file_operations import read_markdown_file

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Task description loader
# ---------------------------------------------------------------------------

_TASKS_YAML: dict[str, Any] | None = None
_WRITING_GUIDELINES: str | None = None


def _load_tasks_yaml() -> dict[str, Any]:
    global _TASKS_YAML
    if _TASKS_YAML is None:
        yaml_path = Path(__file__).parent / "tasks.yaml"
        with open(yaml_path) as f:
            _TASKS_YAML = yaml.safe_load(f) or {}
    return _TASKS_YAML


def _load_writing_guidelines() -> str:
    """Load writing guidelines YAML and serialize it fully for inclusion in prompts."""
    global _WRITING_GUIDELINES
    if _WRITING_GUIDELINES is None:
        yaml_path = Path(__file__).parent / "writing_guidelines.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                data = yaml.safe_load(f) or {}
            # Serialize the full YAML so agents see every rule
            _WRITING_GUIDELINES = (
                "WRITING STYLE RULES (follow strictly):\n"
                + yaml.dump(data, default_flow_style=False, width=120, sort_keys=False)
            )
        else:
            _WRITING_GUIDELINES = ""
    return _WRITING_GUIDELINES


# ---------------------------------------------------------------------------
# Structured output schema (shared by all research agents)
# ---------------------------------------------------------------------------

RESEARCH_OUTPUT_SCHEMA = """\
Respond with a JSON object matching this schema exactly:
{{
  "page": "<page_name>",
  "summary": "<brief summary of findings>",
  "updates": [
    {{
      "section_title": "<exact markdown heading the update belongs under>",
      "update_type": "statistic_update | content_addition | content_deletion | clarification | section_rewrite",
      "original_text": "<exact text to replace, for statistic_update/clarification/content_deletion>",
      "updated_text": "<replacement text, for statistic_update/clarification>",
      "insertion_point": "<text after which to insert, for content_addition>",
      "new_content": "<new paragraph(s) to add, for content_addition or section_rewrite>",
      "reason": "<why this change is needed>",
      "source_url": "<authoritative URL>",
      "confidence": 0.0
    }}
  ],
  "references": [
    {{
      "text": "<human-readable citation title>",
      "url": "<full URL>",
      "type": "government | academic | financial | tech_industry | report | general",
      "originating_page": "<page_name>"
    }}
  ]
}}

Update types:
- statistic_update: Replace a specific fact/figure (provide original_text + updated_text)
- content_addition: Insert new paragraph(s) after insertion_point
- content_deletion: Remove original_text
- clarification: Reword original_text for clarity (provide original_text + updated_text)
- section_rewrite: Replace the ENTIRE body of a section (provide section_title + new_content).
  Use this when a section is substantially outdated and needs wholesale refresh.
  The section heading itself is preserved; everything under it until the next
  heading at the same or higher level is replaced with new_content.

Rules:
- Only include updates with confidence > 0.7
- Every factual claim MUST link directly to its authoritative source URL.
  NEVER use references.md or references.html anchors.
  Example: **[claim text](https://source-url.com)** *(Source Name, Year)*
- Preserve the existing markdown structure and tone
- Do not use em dashes; use commas, semicolons, or rewrite instead
- Content must feel current: lead with recent data, then provide historical context
"""


def _get_full_output_schema() -> str:
    """Combine the output schema with writing guidelines."""
    guidelines = _load_writing_guidelines()
    if guidelines:
        return RESEARCH_OUTPUT_SCHEMA + "\n" + guidelines
    return RESEARCH_OUTPUT_SCHEMA


# ---------------------------------------------------------------------------
# Concrete research agents
# ---------------------------------------------------------------------------


class ResearchAgent(BaseAgent):
    """
    Generic research agent that can research any page.

    Reads the task description from tasks.yaml and the current page
    content, then asks the LLM for structured updates.
    """

    def __init__(self, agent_name: str, task_key: str) -> None:
        super().__init__(agent_name)
        tasks = _load_tasks_yaml()
        if task_key not in tasks:
            raise ValueError(f"Task '{task_key}' not found in tasks.yaml")
        self.task_description: str = tasks[task_key]["description"]
        self.expected_output: str = tasks[task_key].get("expected_output", "")

    def research_page(
        self,
        page_name: str,
        content_path: str,
        target_section: str | None = None,
    ) -> dict[str, Any]:
        """
        Research a specific page (optionally a specific section) and return
        structured findings.

        Args:
            page_name: Name of the page (e.g. "economy")
            content_path: Path to the markdown content file
            target_section: If provided, the H2 heading text to focus on.
                The prompt will instruct the agent to limit updates to
                this section.

        Returns:
            Dict with ``updates`` and ``references`` lists
        """
        from datetime import date

        # Read current content
        try:
            _frontmatter, current_content = read_markdown_file(content_path)
        except Exception:
            current_content = ""

        # Build the task prompt with output schema
        today = date.today().isoformat()
        section_directive = ""
        if target_section:
            section_directive = (
                f"TARGET SECTION: ## {target_section}\n"
                "Only produce updates for this section. "
                "Your output section_title values MUST match this heading.\n\n"
            )

        task = (
            f"Today's date: {today}\n"
            f"Page: {page_name}\n\n"
            f"{section_directive}"
            f"{self.task_description}\n\n"
            f"IMPORTANT: {_get_full_output_schema()}"
        )

        result = self.run(task, context=current_content)

        # Ensure required fields exist
        result.setdefault("page", page_name)
        result.setdefault("updates", [])
        result.setdefault("references", [])

        # Tag references with originating page
        for ref in result.get("references", []):
            ref.setdefault("originating_page", page_name)

        return result


# Convenience factory -------------------------------------------------------


def create_research_agent(agent_name: str, task_key: str) -> ResearchAgent:
    """Create a research agent by name and task key.

    Both values come from :class:`SectionAgentConfig` in ``page_config.py``
    so there is no static mapping here.
    """
    return ResearchAgent(agent_name, task_key)
