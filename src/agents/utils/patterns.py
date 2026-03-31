"""
Shared regex patterns and extraction helpers for markdown content.

Centralizes link/citation extraction used by content_validation_utils
and reference_manager so the logic lives in exactly one place.
"""

import re
from typing import Any

# Compiled patterns
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
EXTERNAL_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")


def extract_markdown_links(content: str) -> list[tuple[str, str]]:
    """Return all ``(text, url)`` pairs from markdown links in *content*."""
    return MARKDOWN_LINK_RE.findall(content)


def extract_external_links(content: str) -> list[tuple[str, str]]:
    """Return ``(text, url)`` pairs for external (http/https) links only."""
    return EXTERNAL_LINK_RE.findall(content)


def extract_external_citations(content: str) -> list[str]:
    """Return formatted ``[text](url)`` strings for external links."""
    return [f"[{text}]({url})" for text, url in extract_external_links(content)]


def extract_citations_by_section(content: str, page_name: str) -> list[dict[str, Any]]:
    """Extract external citations tracking which H2 section each belongs to.

    Returns a list of dicts with keys:
        text, url, originating_page, originating_section
    """
    citations: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    current_section = ""

    for line in content.split("\n"):
        h2_match = re.match(r"^##\s+(.+)", line)
        if h2_match:
            current_section = h2_match.group(1).strip()
            continue

        for text, url in EXTERNAL_LINK_RE.findall(line):
            if url not in seen_urls:
                seen_urls.add(url)
                citations.append({
                    "text": text.strip(),
                    "url": url.strip(),
                    "originating_page": page_name,
                    "originating_section": current_section,
                })

    return citations
