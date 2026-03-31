"""
Research agent implementations.

Each agent wraps BaseAgent with page-specific prompt engineering.
The agents read current content, ask the LLM for updates, and return
structured findings with references that feed into the content update
and reference management pipelines.
"""

import base64
import logging
import mimetypes
import re
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
# Unified research instructions (appended to every task prompt)
# ---------------------------------------------------------------------------

_RESEARCH_INSTRUCTIONS: str | None = None


def _build_research_instructions() -> str:
    """Build the full instruction block appended to every research task.

    Combines three concerns into one authoritative prompt:
    1. **When to update** — guardrails against cosmetic rewording
    2. **Writing & formatting rules** — loaded from writing_guidelines.yaml
    3. **Output schema** — the JSON contract the applier expects
    """
    global _RESEARCH_INSTRUCTIONS
    if _RESEARCH_INSTRUCTIONS is not None:
        return _RESEARCH_INSTRUCTIONS

    guidelines = _load_writing_guidelines()

    _RESEARCH_INSTRUCTIONS = (
        "=== RESEARCH INSTRUCTIONS (follow strictly) ===\n\n"

        # ---- When to update ----
        "WHEN TO UPDATE:\n"
        "Only propose an update (confidence > 0.7) when one or more of these apply:\n"
        "- New data, statistics, or events have occurred since the existing content was written.\n"
        "- An existing claim is factually wrong or its source link is broken.\n"
        "- The section is missing important context that materially helps the reader.\n"
        "- The formatting violates the writing rules below (e.g., stats buried in prose\n"
        "  instead of a bulleted list, missing citations, prohibited punctuation).\n\n"
        "Do NOT propose an update that merely rewords, rephrases, or reorganizes content\n"
        "without adding new information or fixing an actual problem. Cosmetic changes\n"
        "alone should receive confidence 0.0 so they are skipped.\n\n"

        # ---- Writing & formatting ----
        + (guidelines + "\n\n" if guidelines else "")

        # ---- Output schema ----
        + "OUTPUT SCHEMA:\n"
        "Respond with a JSON object matching this schema exactly:\n"
        "{{\n"
        '  "page": "<page_name>",\n'
        '  "summary": "<brief summary of findings>",\n'
        '  "updates": [\n'
        "    {{\n"
        '      "section_title": "<exact markdown heading to rewrite>",\n'
        '      "new_content": "<complete replacement body for the section>",\n'
        '      "reason": "<why this update is needed>",\n'
        '      "confidence": 0.0\n'
        "    }}\n"
        "  ],\n"
        '  "references": [\n'
        "    {{\n"
        '      "text": "<human-readable citation title>",\n'
        '      "url": "<full URL>",\n'
        '      "type": "government | academic | financial | tech_industry | report | general",\n'
        '      "originating_page": "<page_name>"\n'
        "    }}\n"
        "  ]\n"
        "}}\n\n"
        "You are updating ONE section at a time. Return exactly one entry in the\n"
        '"updates" array with section_title matching the TARGET SECTION heading.\n'
        'Provide the complete new body for that section in "new_content". The\n'
        "heading itself is preserved automatically; only include the content that\n"
        "goes under it.\n\n"
        "Rules:\n"
        "- Only include updates with confidence > 0.7\n"
        "- Every factual claim MUST link directly to its authoritative source URL.\n"
        "  NEVER use references.md or references.html anchors.\n"
        "  Example: **[claim text](https://source-url.com)** *(Source Name, Year)*\n"
        "- Preserve the existing markdown structure and tone\n"
        "- Do not use em dashes; use commas, semicolons, or rewrite instead\n"
        "- Content must feel current: lead with recent data, then provide historical context\n"
        "- Provide the complete updated section content\n"
    )
    return _RESEARCH_INSTRUCTIONS


# ---------------------------------------------------------------------------
# Structural element extraction and vision support
# ---------------------------------------------------------------------------


def _extract_structural_elements(content: str, heading: str) -> list[dict[str, str]]:
    """Extract images and HTML elements from the section under *heading*.

    Returns a list of dicts, each with:
      kind:    "image" or "html"
      path:    relative image path (e.g. "images/market_trends.png") or ""
      alt:     alt-text for images, class name for HTML divs
      caption: caption text if present, else ""
    """
    lines = content.split("\n")
    heading_lower = re.sub(r"^#{1,6}\s*", "", heading.strip()).lower()

    start_idx: int | None = None
    heading_level = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m and m.group(2).strip().lower() == heading_lower:
            start_idx = i
            heading_level = len(m.group(1))
            break

    if start_idx is None:
        return []

    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        m = re.match(r"^(#{1,6})\s+", lines[j])
        if m and len(m.group(1)) <= heading_level:
            end_idx = j
            break

    body = lines[start_idx + 1 : end_idx]
    elements: list[dict[str, str]] = []
    for idx, line in enumerate(body):
        stripped = line.strip()
        img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if img:
            alt, src = img.group(1), img.group(2)
            caption = ""
            if idx + 1 < len(body):
                nxt = body[idx + 1].strip()
                if nxt.startswith("*") and nxt.endswith("*"):
                    caption = nxt.strip("* ")
            elements.append({"kind": "image", "path": src, "alt": alt, "caption": caption})
        elif stripped.startswith("<div"):
            class_match = re.search(r'class="([^"]+)"', stripped)
            cls = class_match.group(1) if class_match else "unknown"
            elements.append({"kind": "html", "path": "", "alt": cls, "caption": ""})

    return elements


def _build_structural_prompt(elements: list[dict[str, str]]) -> str:
    """Convert structural elements to a text-based STRUCTURAL NOTE for the prompt.

    Always included so the agent knows what elements exist and where,
    regardless of whether the model can also see the actual images.
    """
    if not elements:
        return ""
    hints: list[str] = []
    for el in elements:
        if el["kind"] == "image":
            caption = f" — caption: {el['caption']}" if el["caption"] else ""
            hints.append(f"- Image: {el['path']} (alt=\"{el['alt']}\"){caption}")
        elif el["kind"] == "html":
            hints.append(f"- HTML element: <div class=\"{el['alt']}\">")
    return (
        "\nSTRUCTURAL NOTE: This section contains the following visual/interactive "
        "elements that are preserved automatically. Do NOT reproduce them in your "
        "output, but write a natural lead-in sentence before where they appear "
        "so the content flows into the visual element. If the actual image is "
        "included in this message, use what you see to write a more contextual "
        "transition:\n"
        + "\n".join(hints)
        + "\n"
    )


def _load_section_images(
    elements: list[dict[str, str]],
    static_dir: Path,
) -> list[dict[str, str]]:
    """Read image files from *static_dir* and return base64 data URLs.

    Each returned dict has a ``url`` key with a ``data:<mime>;base64,...``
    URI suitable for litellm's vision content blocks.  Images that cannot
    be found are silently skipped (the text hints still cover them).
    """
    images: list[dict[str, str]] = []
    for el in elements:
        if el["kind"] != "image" or not el["path"]:
            continue
        img_path = static_dir / el["path"]
        if not img_path.is_file():
            logger.debug("Image not found, skipping vision: %s", img_path)
            continue
        mime = mimetypes.guess_type(str(img_path))[0] or "image/png"
        data = img_path.read_bytes()
        b64 = base64.b64encode(data).decode()
        images.append({"url": f"data:{mime};base64,{b64}"})
        logger.debug("Loaded image for vision: %s (%d bytes)", img_path.name, len(data))
    return images


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
        self.local_files: list[str] = tasks[task_key].get("local_files", [])

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
        elements: list[dict[str, str]] = []
        if target_section:
            elements = _extract_structural_elements(current_content, target_section)
            structural_prompt = _build_structural_prompt(elements)
            section_directive = (
                f"TARGET SECTION: ## {target_section}\n"
                "Only produce updates for this section. "
                "Your output section_title values MUST match this heading.\n\n"
                + structural_prompt
            )

        task = (
            f"Today's date: {today}\n"
            f"Page: {page_name}\n\n"
            f"{section_directive}"
            f"{self.task_description}\n\n"
            f"{_build_research_instructions()}"
        )

        # Load actual image bytes for vision-capable models
        static_dir = Path(__file__).parent.parent / "static"
        section_images = _load_section_images(elements, static_dir) if elements else None

        # Load local reference data files (PDFs, images) specified in task config
        local_images: list[dict[str, str]] | None = None
        local_documents: list[dict[str, str]] | None = None
        if self.local_files:
            from .utils.local_data_loader import load_local_files

            attachments = load_local_files(self.local_files)
            imgs = [{"url": f"data:{a.mime};base64,{a.data}"} for a in attachments if a.kind == "image"]
            docs = [{"mime": a.mime, "data": a.data} for a in attachments if a.kind == "document"]
            local_images = imgs or None
            local_documents = docs or None

            if attachments:
                task += (
                    "\n\nLOCAL REFERENCE DATA: The following local files are attached. "
                    "You MUST incorporate relevant claims, data points, and perspectives "
                    "from these files into your updated content. Treat them as primary "
                    "source material — cite specific findings, quote key arguments, and "
                    "weave their insights into the narrative alongside your other research. "
                    "Do not ignore attached files.\n"
                    + "\n".join(f"- {a.filename}" for a in attachments)
                )

        # Merge section images with local images
        all_images = (section_images or []) + (local_images or []) or None

        result = self.run(task, context=current_content, images=all_images, documents=local_documents)

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
