"""
Reference manager - engineered (non-AI) reference synchronization.

Scans all content files for citations (tracking which H2 section each
appears under), merges agent-provided references, deduplicates, and
writes a clean references.md organized by page and section.
"""

import re
from pathlib import Path
from typing import Any

from .utils.file_operations import (
    list_content_files,
    read_markdown_file,
    write_markdown_file,
)

# ---------------------------------------------------------------------------
# Citation extraction
# ---------------------------------------------------------------------------


def extract_citations_from_file(file_path: str) -> list[dict[str, Any]]:
    """
    Extract all external citations from a single markdown file.

    Tracks which H2 section each citation falls under so references.md
    can be organized by page and section.

    Returns a list of dicts with keys:
        text, url, type, originating_page, originating_section
    """
    page_name = Path(file_path).stem
    if page_name == "references":
        return []  # don't self-reference

    try:
        _fm, content = read_markdown_file(file_path)
    except Exception:
        return []

    citations: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    # Parse line-by-line to track the current H2 section
    current_section = ""
    for line in content.split("\n"):
        # Detect H2 headings
        h2_match = re.match(r"^##\s+(.+)", line)
        if h2_match:
            current_section = h2_match.group(1).strip()
            continue

        # Extract markdown links to external URLs
        for text, url in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", line):
            if url not in seen_urls:
                seen_urls.add(url)
                citations.append({
                    "text": text.strip(),
                    "url": url.strip(),
                    "type": _classify_url(text, url),
                    "originating_page": page_name,
                    "originating_section": current_section,
                })

    return citations


def extract_all_citations(content_dir: str = "src/content") -> list[dict[str, Any]]:
    """
    Extract and deduplicate citations from every content file.

    Returns a flat list ordered by (page, section, text).
    """
    all_citations: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for file_path in list_content_files(content_dir):
        for cite in extract_citations_from_file(file_path):
            if cite["url"] not in seen_urls:
                seen_urls.add(cite["url"])
                all_citations.append(cite)

    return sorted(
        all_citations,
        key=lambda c: (c["originating_page"], c.get("originating_section", ""), c["text"].lower()),
    )


def merge_agent_references(
    existing: list[dict[str, Any]],
    agent_refs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Merge references returned by research agents into the existing list.

    Agent references that are already present (by URL) are skipped;
    new ones are appended.
    """
    seen = {c["url"] for c in existing}
    merged = list(existing)
    for ref in agent_refs:
        if ref.get("url") and ref["url"] not in seen:
            seen.add(ref["url"])
            merged.append({
                "text": ref.get("text", _title_from_url(ref["url"])),
                "url": ref["url"],
                "type": ref.get("type", _classify_url("", ref["url"])),
                "originating_page": ref.get("originating_page", ""),
                "originating_section": ref.get("originating_section", ""),
            })
    return sorted(
        merged,
        key=lambda c: (c["originating_page"], c.get("originating_section", ""), c["text"].lower()),
    )


# ---------------------------------------------------------------------------
# References file generation
# ---------------------------------------------------------------------------


def _page_display_name(page_name: str) -> str:
    """Map a page slug to a human-readable heading.

    Uses PAGE_CONFIGS as the single source of truth for page titles.
    """
    from .utils.page_config import PAGE_CONFIGS

    cfg = PAGE_CONFIGS.get(page_name)
    return cfg.title if cfg else page_name.title()


def build_references_markdown(citations: list[dict[str, Any]]) -> str:
    """
    Build the body of references.md organized by originating page and section.

    Structure:
        ## Economy & Policy
        ### Macroeconomic Landscape
        [1] Citation text — [View Source](url)
        ...
    """
    lines: list[str] = []
    counter = 1
    current_page = ""
    current_section = ""

    for cite in citations:
        page = cite.get("originating_page", "")
        section = cite.get("originating_section", "")

        # New page heading
        if page != current_page:
            current_page = page
            current_section = ""
            if lines:
                lines.append("")
            lines.append(f"## {_page_display_name(page)}")
            lines.append("")

        # New section sub-heading
        if section and section != current_section:
            current_section = section
            lines.append(f"### {section}")
            lines.append("")

        # Citation entry
        lines.append(f"**[{counter}]** {cite['text']} — [View Source]({cite['url']})")
        lines.append("")
        counter += 1

    # Methodology note
    lines.append("## Methodology Notes")
    lines.append("")
    lines.append(
        "All sources are selected for authority, recency, and relevance. "
        "Government and academic sources are preferred for statistical claims. "
        "References are automatically synchronized from content pages during "
        "each build cycle and organized by the page and section they support."
    )

    return "\n".join(lines)


def sync_references_file(
    content_dir: str = "src/content",
    agent_refs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Full reference sync: extract citations, merge agent refs, write file.

    Returns a report dict.
    """
    # 1. Extract from content
    citations = extract_all_citations(content_dir)

    # 2. Merge any agent-provided references
    if agent_refs:
        citations = merge_agent_references(citations, agent_refs)

    # 3. Build markdown
    body = build_references_markdown(citations)

    # 4. Write
    ref_path = str(Path(content_dir) / "references.md")
    frontmatter = {
        "title": "References & Sources",
        "tagline": "Research citations and data sources",
        "description": (
            "Comprehensive list of academic sources, reports, and data "
            "supporting our analysis and recommendations."
        ),
    }
    # backup=False: references.md is generated, not authored
    success = write_markdown_file(ref_path, body, frontmatter=frontmatter, backup=False)

    return {
        "success": success,
        "total_citations": len(citations),
        "output_file": ref_path,
        "by_page": _count_by_page(citations),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _classify_url(text: str, url: str) -> str:
    """Classify a citation by its URL domain and link text."""
    url_l = url.lower()
    text_l = text.lower()

    if any(d in url_l for d in [".gov", "treasury.gov", "bls.gov", "fed.org"]):
        return "government"
    if any(d in url_l for d in [".edu", "scholar.google", "arxiv.org", "nature.com"]):
        return "academic"
    if any(d in url_l for d in ["wsj.com", "bloomberg.com", "ft.com", "reuters.com", "coinmarketcap", "coindoo"]):
        return "financial"
    if any(d in url_l for d in ["openai.com", "microsoft.com", "google.com", "meta.com", "anthropic.com"]):
        return "tech_industry"
    if any(k in text_l for k in ["report", "study", "survey", "research"]):
        return "report"
    return "general"


def _title_from_url(url: str) -> str:
    """Derive a human-readable title from a URL."""
    try:
        domain = url.split("/")[2].replace("www.", "")
        return f"Source: {domain}"
    except (IndexError, AttributeError):
        return "Source"


def _count_by_page(citations: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in citations:
        page = c.get("originating_page", "unknown")
        counts[page] = counts.get(page, 0) + 1
    return counts
