"""
Content update applier for applying agent research findings to markdown files
Handles parsing agent outputs and updating content while preserving structure
"""

import logging
from datetime import datetime
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
        updates: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Apply structured updates to content file
        Expects structured updates from AI agents

        Args:
            file_path: Path to content file to update
            updates: List of structured updates from agents with:
                - section_title: Section identifier
                - update_type: "statistic_update", "content_addition", "content_deletion", "clarification"
                - original_text: Text to find (for replacements)
                - updated_text: New text (for replacements/additions)
                - insertion_point: Where to add (for additions)
                - new_content: Content to add (for additions)
                - reason: Explanation of change
                - source_url: Citation
                - confidence: Confidence score (0.0-1.0)

        Returns:
            Dictionary with update results and statistics
        """
        try:
            # Read current content
            frontmatter, current_content = read_markdown_file(file_path)

            # Apply structured updates
            updated_content = current_content
            updates_applied = 0
            updates_skipped = 0
            update_details = []

            # Sort updates by confidence (highest first)
            sorted_updates = sorted(updates, key=lambda x: x.get("confidence", 0), reverse=True)

            for update in sorted_updates:
                # Skip low-confidence updates
                if update.get("confidence", 0) <= 0.7:
                    updates_skipped += 1
                    logger.debug(f"Skipped low-confidence update: {update.get('reason', 'No reason provided')}")
                    continue

                update_type = update.get("update_type", "")

                try:
                    if update_type == "statistic_update":
                        # Replace specific text
                        original = update.get("original_text", "")
                        replacement = update.get("updated_text", "")

                        if original and original in updated_content:
                            updated_content = updated_content.replace(original, replacement, 1)
                            updates_applied += 1
                            update_details.append({
                                "type": update_type,
                                "section": update.get("section_title", ""),
                                "change": f"{original} → {replacement}"
                            })
                            logger.info(f"Applied statistic update in '{update.get('section_title', 'unknown')}': {original[:50]}...")
                        else:
                            logger.warning(f"Could not find original text to replace: {original[:50]}...")
                            updates_skipped += 1

                    elif update_type == "content_addition":
                        # Add new content at specified insertion point
                        new_content = update.get("new_content", "")
                        insertion_point = update.get("insertion_point", "")

                        # Try to find the insertion point and add after it
                        if insertion_point and insertion_point in updated_content:
                            # Find the paragraph and add new content after it
                            parts = updated_content.split(insertion_point, 1)
                            if len(parts) == 2:
                                # Find end of paragraph (double newline)
                                paragraph_end = parts[1].find("\n\n")
                                if paragraph_end != -1:
                                    updated_content = (
                                        parts[0] + insertion_point +
                                        parts[1][:paragraph_end] +
                                        "\n\n" + new_content +
                                        parts[1][paragraph_end:]
                                    )
                                    updates_applied += 1
                                    update_details.append({
                                        "type": update_type,
                                        "section": update.get("section_title", ""),
                                        "change": f"Added content after: {insertion_point[:30]}..."
                                    })
                                    logger.info(f"Added content in '{update.get('section_title', 'unknown')}'")
                                else:
                                    logger.warning("Could not find paragraph end after insertion point")
                                    updates_skipped += 1
                            else:
                                logger.warning("Could not split at insertion point")
                                updates_skipped += 1
                        else:
                            logger.warning(f"Could not find insertion point: {insertion_point[:50]}...")
                            updates_skipped += 1

                    elif update_type == "content_deletion":
                        # Remove specified content
                        content_to_remove = update.get("original_text", "")

                        if content_to_remove and content_to_remove in updated_content:
                            updated_content = updated_content.replace(content_to_remove, "", 1)
                            updates_applied += 1
                            update_details.append({
                                "type": update_type,
                                "section": update.get("section_title", ""),
                                "change": f"Removed: {content_to_remove[:50]}..."
                            })
                            logger.info(f"Deleted content in '{update.get('section_title', 'unknown')}'")
                        else:
                            logger.warning(f"Could not find content to delete: {content_to_remove[:50]}...")
                            updates_skipped += 1

                    elif update_type == "clarification":
                        # Replace text to improve clarity
                        original = update.get("original_text", "")
                        clarified = update.get("updated_text", "")

                        if original and original in updated_content:
                            updated_content = updated_content.replace(original, clarified, 1)
                            updates_applied += 1
                            update_details.append({
                                "type": update_type,
                                "section": update.get("section_title", ""),
                                "change": f"Clarified: {original[:30]}..."
                            })
                            logger.info(f"Applied clarification in '{update.get('section_title', 'unknown')}'")
                        else:
                            logger.warning(f"Could not find text to clarify: {original[:50]}...")
                            updates_skipped += 1

                    elif update_type == "section_rewrite":
                        # Replace entire section body under a heading
                        section_title = update.get("section_title", "")
                        new_body = update.get("new_content", "")

                        if section_title and new_body:
                            rewritten = self._rewrite_section(
                                updated_content, section_title, new_body,
                            )
                            if rewritten is not None:
                                updated_content = rewritten
                                updates_applied += 1
                                update_details.append({
                                    "type": update_type,
                                    "section": section_title,
                                    "change": f"Rewrote section: {section_title}",
                                })
                                logger.info(f"Rewrote section '{section_title}'")
                            else:
                                logger.warning(f"Could not find section to rewrite: {section_title}")
                                updates_skipped += 1
                        else:
                            logger.warning("section_rewrite requires section_title and new_content")
                            updates_skipped += 1

                    else:
                        logger.warning(f"Unknown update type: {update_type}")
                        updates_skipped += 1

                except Exception as update_error:
                    logger.error(f"Error applying individual update: {update_error}")
                    updates_skipped += 1

            # Only write if we actually made changes
            backup_created = False
            if updates_applied > 0:
                backup_created = Path(file_path).exists()
                write_markdown_file(file_path, updated_content, frontmatter)
                logger.info(f"Successfully applied {updates_applied} updates to {file_path}")
            else:
                logger.info(f"No updates applied to {file_path}")

            return {
                "success": True,
                "file_path": file_path,
                "updates_applied": updates_applied,
                "updates_skipped": updates_skipped,
                "update_details": update_details,
                "timestamp": datetime.now().isoformat(),
                "backup_created": backup_created,
            }

        except Exception as e:
            logger.error(f"Error applying updates to {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }

    @staticmethod
    def _rewrite_section(content: str, heading: str, new_body: str) -> str | None:
        """Replace the body of a markdown section identified by *heading*.

        Finds the heading line (any ``#`` level), then replaces everything
        from the line after the heading up to (but not including) the next
        heading at the same or higher level.  The heading itself is kept.

        Returns the updated content, or ``None`` if the heading was not found.
        """
        import re

        lines = content.split("\n")
        heading_lower = heading.strip().lower()

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

        # Reassemble: heading line + blank + new body + rest
        before = lines[: start_idx + 1]
        after = lines[end_idx:]
        return "\n".join(before) + "\n\n" + new_body.strip() + "\n\n" + "\n".join(after)




