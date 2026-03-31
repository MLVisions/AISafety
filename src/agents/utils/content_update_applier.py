"""
Content update applier for applying agent research findings to markdown files
Handles parsing agent outputs and updating content while preserving structure
"""

import logging
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .file_operations import read_markdown_file, write_markdown_file

logger = logging.getLogger(__name__)


class ContentUpdateApplier:
    """
    Applies structured updates from research agents to content files.
    Preserves existing structure, navigation, and formatting.
    """

    def __init__(self, base_dir: str = "src/content"):
        """
        Initialize ContentUpdateApplier

        Args:
            base_dir: Base directory for content files
        """
        self.base_dir = Path(base_dir)

    def apply_updates(
        self,
        file_path: str,
        updates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply section-level updates to a content markdown file.

        Each update must have ``section_title`` (the H2/H3 heading) and
        ``new_content`` (the complete replacement body).  The heading
        itself is preserved; everything under it until the next heading
        at the same or higher level is replaced.

        Updates with ``confidence`` <= 0.7 are silently skipped.
        """
        try:
            frontmatter, content = read_markdown_file(file_path)

            applied = 0
            skipped = 0
            details: list[dict[str, str]] = []

            for update in updates:
                if update.get("confidence", 0) <= 0.7:
                    skipped += 1
                    continue

                section = update.get("section_title", "")
                new_body = update.get("new_content", "")

                if not section or not new_body:
                    logger.warning("Update missing section_title or new_content")
                    skipped += 1
                    continue

                rewritten = self._rewrite_section(content, section, new_body)
                if rewritten is not None:
                    old_body = self._section_body(content, section)
                    if old_body is not None:
                        ratio = SequenceMatcher(
                            None, old_body.strip(), new_body.strip()
                        ).ratio()
                        if ratio > 0.9:
                            logger.info(
                                "Skipped cosmetic change to '%s' "
                                "(similarity %.0f%%)",
                                section,
                                ratio * 100,
                            )
                            skipped += 1
                            continue
                    content = rewritten
                    applied += 1
                    details.append({"section": section, "change": f"Rewrote: {section}"})
                    logger.info(f"Rewrote section '{section}'")
                else:
                    logger.warning(f"Section not found: {section}")
                    skipped += 1

            if applied > 0:
                write_markdown_file(file_path, content, frontmatter)
                logger.info(f"Applied {applied} updates to {file_path}")

            return {
                "success": True,
                "file_path": file_path,
                "updates_applied": applied,
                "updates_skipped": skipped,
                "update_details": details,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error applying updates to {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def _section_body(content: str, heading: str) -> str | None:
        """Return the body text under *heading*, or ``None`` if not found."""
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
            return None

        end_idx = len(lines)
        for j in range(start_idx + 1, len(lines)):
            m = re.match(r"^(#{1,6})\s+", lines[j])
            if m and len(m.group(1)) <= heading_level:
                end_idx = j
                break
        return "\n".join(lines[start_idx + 1 : end_idx])

    @staticmethod
    def _rewrite_section(content: str, heading: str, new_body: str) -> str | None:
        """Replace the body of a markdown section identified by *heading*.

        Finds the heading line (any ``#`` level), then replaces everything
        from the line after the heading up to (but not including) the next
        heading at the same or higher level.  The heading itself is kept.

        Structural lines (images, HTML elements, and italic captions that
        follow images) are preserved from the old section body and appended
        after the new content.  This prevents the LLM from accidentally
        dropping plot references, ticker dropdowns, and similar elements
        it has no knowledge of.

        Returns the updated content, or ``None`` if the heading was not found.
        """
        lines = content.split("\n")
        # Strip any leading '#' markers so both "### Foo" and "Foo" match
        heading_lower = re.sub(r"^#{1,6}\s*", "", heading.strip()).lower()

        start_idx: int | None = None
        heading_level: int = 0

        for i, line in enumerate(lines):
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip().lower()
                if title == heading_lower:
                    start_idx = i
                    heading_level = level
                    break

        if start_idx is None:
            return None

        # Find end of section: next heading at same or higher level
        end_idx = len(lines)
        for j in range(start_idx + 1, len(lines)):
            m = re.match(r"^(#{1,6})\s+", lines[j])
            if m and len(m.group(1)) <= heading_level:
                end_idx = j
                break

        # Extract structural lines from the old section body that the
        # LLM would not know to reproduce (images, HTML, captions).
        old_body_lines = lines[start_idx + 1 : end_idx]
        preserved: list[str] = []
        for idx, line in enumerate(old_body_lines):
            stripped = line.strip()
            is_structural = (
                re.match(r"^!\[.*\]\(.*\)$", stripped)  # image
                or stripped.startswith("<div")           # HTML open
                or stripped.startswith("</div")          # HTML close
                or re.match(r"^<[a-z]", stripped)        # other HTML
                or stripped.startswith("{{<")            # shortcodes
            )
            if is_structural:
                preserved.append(line)
                # Also keep a caption line immediately following an image
                # (possibly separated by a single blank line)
                if re.match(r"^!\[.*\]\(.*\)$", stripped):
                    for offset in (1, 2):
                        nxt = idx + offset
                        if nxt < len(old_body_lines):
                            next_line = old_body_lines[nxt].strip()
                            if next_line.startswith("*") and next_line.endswith("*"):
                                preserved.append(old_body_lines[nxt])
                                break
                            if next_line:  # non-blank, non-caption → stop
                                break
            # Keep italic caption lines that follow images (caught above)
            # but skip standalone ones to avoid duplicating normal text.

        # Only append preserved lines that the LLM did not already include
        new_body_stripped = new_body.strip()
        unique_preserved = [
            p for p in preserved if p.strip() not in new_body_stripped
        ]

        # Reassemble: heading line + blank + new body + preserved lines + rest
        before = lines[: start_idx + 1]
        after = lines[end_idx:]
        parts = ["\n".join(before), "", new_body_stripped]
        if unique_preserved:
            parts.append("")
            parts.extend(unique_preserved)
        parts.append("")
        parts.append("\n".join(after))
        return "\n".join(parts)




