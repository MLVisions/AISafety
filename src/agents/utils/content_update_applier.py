"""
Content update applier for applying agent research findings to markdown files
Handles parsing agent outputs and updating content while preserving structure
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .file_operations import read_markdown_file, write_markdown_file

logger = logging.getLogger(__name__)


class ContentUpdateApplier:
    """
    Applies agent research findings to content files
    Preserves existing structure, navigation, and formatting
    Uses strategy pattern for page-specific update logic
    """

    def __init__(self, base_dir: str = "src/content"):
        """
        Initialize ContentUpdateApplier

        Args:
            base_dir: Base directory for content files
        """
        self.base_dir = Path(base_dir)
        self.automation_outputs_dir = Path("automation_outputs")

    def apply_updates(
        self,
        file_path: str,
        updates: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Apply structured updates to content file
        SIMPLIFIED: Expects structured updates from AI agents, no strategies needed

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

            # Create backup before updating
            self._create_backup(file_path)

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

                    else:
                        logger.warning(f"Unknown update type: {update_type}")
                        updates_skipped += 1

                except Exception as update_error:
                    logger.error(f"Error applying individual update: {update_error}")
                    updates_skipped += 1

            # Only write if we actually made changes
            if updates_applied > 0:
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
                "backup_created": True
            }

        except Exception as e:
            logger.error(f"Error applying updates to {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }

    # LEGACY METHOD - kept for backward compatibility, will be removed
    def apply_research_updates(
        self,
        file_path: str,
        research_findings: str,
        validation_results: dict[str, Any],
        preserve_structure: bool = True
    ) -> dict[str, Any]:
        """
        DEPRECATED: Legacy method for applying research updates
        Use apply_updates() with ContentUpdateStrategy instead
        """
        try:
            # Parse research findings into suggestions format
            suggestions = self._parse_research_findings(research_findings)

            # Apply using legacy logic for backward compatibility
            frontmatter, current_content = read_markdown_file(file_path)
            updated_content = self._apply_legacy_updates(
                current_content, suggestions, validation_results, preserve_structure
            )

            self._create_backup(file_path)
            write_markdown_file(file_path, updated_content, frontmatter)

            return {
                "success": True,
                "file_path": file_path,
                "updates_applied": len(suggestions),
                "validation_score": validation_results.get("quality_score", 0),
                "timestamp": datetime.now().isoformat(),
                "backup_created": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }

    def _parse_research_findings(self, research_findings: str) -> list[dict[str, Any]]:
        """
        Parse research findings to extract actionable update suggestions

        Args:
            research_findings: Raw research findings text

        Returns:
            List of update suggestions with metadata
        """
        suggestions = []

        # Look for specific update patterns in research findings
        patterns = {
            "statistics": r"(?i)(?:statistic|data|number|percentage)[:.]?\s*(.+?)(?:\n|$)",
            "trends": r"(?i)(?:trend|development|change|shift)[:.]?\s*(.+?)(?:\n|$)",
            "strategies": r"(?i)(?:strategy|approach|method|technique)[:.]?\s*(.+?)(?:\n|$)",
            "recommendations": r"(?i)(?:recommend|suggest|advise|propose)[:.]?\s*(.+?)(?:\n|$)",
            "updates": r"(?i)(?:update|revise|modify|change)[:.]?\s*(.+?)(?:\n|$)"
        }

        for category, pattern in patterns.items():
            matches = re.findall(pattern, research_findings, re.MULTILINE)
            for match in matches:
                suggestions.append({
                    "category": category,
                    "content": match.strip(),
                    "confidence": self._calculate_suggestion_confidence(match)
                })

        return suggestions

    def _apply_strategy_updates(
        self,
        current_content: str,
        suggestions: list[dict[str, Any]],
        update_strategy: Any  # ContentUpdateStrategy removed
    ) -> tuple[str, int]:
        """
        DEPRECATED: Old strategy-based update system
        This method is kept only for backward compatibility with existing tests
        Will be removed once agent output format is updated

        Args:
            current_content: Current file content
            suggestions: List of update suggestions
            update_strategy: Strategy for page-specific updates

        Returns:
            Tuple of (updated_content, updates_applied_count)
        """
        updated_content = current_content
        updates_applied = 0

        # Filter high-confidence suggestions
        high_confidence_suggestions = [
            s for s in suggestions
            if s.get("confidence", 0) > 0.6
        ]

        for suggestion in high_confidence_suggestions:
            original_content = updated_content

            try:
                # Apply strategy-specific updates based on suggestion type
                if suggestion.get("type") == "statistic":
                    updated_content = update_strategy.update_statistics(updated_content, suggestion)
                elif suggestion.get("type") == "strategy":
                    updated_content = update_strategy.update_strategies(updated_content, suggestion)
                elif suggestion.get("type") == "recommendation":
                    updated_content = update_strategy.update_recommendations(updated_content, suggestion)

                # Count successful updates
                if updated_content != original_content:
                    updates_applied += 1
            except Exception as e:
                # Strategy error - continue with next suggestion
                logger.warning(f"Strategy error for {suggestion.get('type')} suggestion: {e}")
                continue

        return updated_content, updates_applied

    # LEGACY METHOD - kept for backward compatibility
    def _apply_legacy_updates(
        self,
        current_content: str,
        update_suggestions: list[dict[str, Any]],
        validation_results: dict[str, Any],
        preserve_structure: bool
    ) -> str:
        """
        DEPRECATED: Legacy update logic for backward compatibility
        """
        updated_content = current_content

        # Only apply high-confidence suggestions that pass validation
        high_confidence_suggestions = [
            s for s in update_suggestions
            if s["confidence"] > 0.7 and validation_results.get("quality_score", 0) > 0.6
        ]

        for suggestion in high_confidence_suggestions:
            if suggestion["category"] == "statistics":
                updated_content = self._legacy_update_statistics(updated_content, suggestion)
            elif suggestion["category"] == "strategies":
                updated_content = self._legacy_update_strategies(updated_content, suggestion)
            elif suggestion["category"] == "recommendations":
                updated_content = self._legacy_update_recommendations(updated_content, suggestion)

        # Add research update timestamp if not preserving strict structure
        if not preserve_structure:
            updated_content = self._add_update_timestamp(updated_content)

        return updated_content

    # LEGACY METHODS - kept for backward compatibility, will be removed
    def _legacy_update_statistics(self, content: str, suggestion: dict[str, Any]) -> str:
        """DEPRECATED: Legacy update statistical information in content"""
        # For action.md, look for existing statistics to update
        suggestion_text = suggestion["content"]

        # Look for patterns like "as many as X jobs" or "X% of workers"
        if "jobs" in suggestion_text.lower():
            # Update job displacement statistics
            job_pattern = r"as many as (\d+(?:,\d{3})*|\d+) (?:million )?jobs"
            if re.search(job_pattern, content, re.IGNORECASE):
                # Extract new number from suggestion
                new_number_match = re.search(r"(\d+(?:,\d{3})*|\d+) (?:million )?jobs", suggestion_text, re.IGNORECASE)
                if new_number_match:
                    new_number = new_number_match.group(1)
                    content = re.sub(
                        job_pattern,
                        f"as many as {new_number} jobs",
                        content,
                        flags=re.IGNORECASE
                    )

        return content

    def _legacy_update_strategies(self, content: str, suggestion: dict[str, Any]) -> str:
        """DEPRECATED: Legacy update strategy recommendations in content"""
        # For action.md, strategies are in specific sections
        suggestion_text = suggestion["content"]

        # Look for relevant strategy sections to enhance
        if "ai" in suggestion_text.lower() and "skills" in suggestion_text.lower():
            # Enhance the "Reskill & adapt" section
            reskill_pattern = r"(### Reskill & adapt\n\*\*Build AI‑adjacent skills\*\*\n\n)(.*?)(?=\n---|\n###|$)"
            if re.search(reskill_pattern, content, re.DOTALL):
                # Add new strategy insight if it's valuable
                if len(suggestion_text) > 50 and "complement" in suggestion_text.lower():
                    enhanced_text = f"\\1\\2\n\n*Recent insight: {suggestion_text[:100]}...*"
                    content = re.sub(reskill_pattern, enhanced_text, content, flags=re.DOTALL)

        return content

    def _legacy_update_recommendations(self, content: str, suggestion: dict[str, Any]) -> str:
        """DEPRECATED: Legacy update recommendation content"""
        # For action.md, recommendations can be added as updates to existing sections
        suggestion_text = suggestion["content"]

        # Add valuable recommendations as context to existing strategies
        if len(suggestion_text) > 30:
            # Look for the end of practical content before references
            ref_pattern = r"(\*For detailed sources and research citations.*)"
            if re.search(ref_pattern, content):
                # Add recommendation before references
                addition = f"\n\n### Recent Development\n*{suggestion_text}*\n\n"
                content = re.sub(ref_pattern, addition + "\\1", content)

        return content

    def _calculate_suggestion_confidence(self, suggestion_text: str) -> float:
        """
        Calculate confidence score for a suggestion

        Args:
            suggestion_text: Text of the suggestion

        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence

        # Increase confidence for specific indicators
        if len(suggestion_text) > 20:
            confidence += 0.1
        if re.search(r"\d+", suggestion_text):  # Contains numbers/statistics
            confidence += 0.2
        if any(word in suggestion_text.lower() for word in ["research", "study", "report", "analysis"]):
            confidence += 0.2
        if any(word in suggestion_text.lower() for word in ["recommend", "suggest", "should", "important"]):
            confidence += 0.1

        return min(confidence, 1.0)

    def _create_backup(self, file_path: str) -> None:
        """Create backup of file before updating"""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            file_path_obj = Path(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path_obj.stem}_{timestamp}{file_path_obj.suffix}"
            backup_path = backup_dir / backup_name

            with open(file_path, encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())

        except Exception as e:
            print(f"Warning: Could not create backup: {e}")

    def _add_update_timestamp(self, content: str) -> str:
        """Add update timestamp to content"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        timestamp_marker = f"\n\n*Last updated: {timestamp}*\n"

        # Add before references section if it exists
        ref_pattern = r"(\*For detailed sources and research citations.*)"
        if re.search(ref_pattern, content):
            return re.sub(ref_pattern, timestamp_marker + "\\1", content)
        else:
            return content + timestamp_marker

    def get_automation_outputs(self) -> list[str]:
        """
        Get list of automation output files for processing

        Returns:
            List of output file paths
        """
        if not self.automation_outputs_dir.exists():
            return []

        output_files = []
        for file_path in self.automation_outputs_dir.glob("*.md"):
            output_files.append(str(file_path))

        return output_files
