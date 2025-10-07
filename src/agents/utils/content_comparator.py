"""
Content Comparator - Analyzes differences between old and new content
Ensures meaningful updates while preserving existing quality content
"""

import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .file_operations import read_markdown_file


class ContentComparator:
    """
    Analyzes content changes to determine if updates preserve meaning
    and improve accuracy without unnecessary rewording
    """

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize the content comparator

        Args:
            similarity_threshold: Minimum similarity score to consider content equivalent
        """
        self.similarity_threshold = similarity_threshold

    def compare_content(
        self,
        old_content: str,
        new_content: str,
        content_type: str = "general"
    ) -> dict[str, Any]:
        """
        Compare old and new content to analyze changes

        Args:
            old_content: Original content text
            new_content: Updated content text
            content_type: Type of content (general, data, citations)

        Returns:
            Dictionary with comparison analysis
        """
        comparison = {
            "overall_similarity": self._calculate_similarity(old_content, new_content),
            "changes": self._analyze_changes(old_content, new_content),
            "recommendations": [],
            "preserve_original": False,
            "content_type": content_type
        }

        # Analyze by content type
        if content_type == "data":
            comparison.update(self._analyze_data_changes(old_content, new_content))
        elif content_type == "citations":
            comparison.update(self._analyze_citation_changes(old_content, new_content))
        else:
            comparison.update(self._analyze_general_changes(old_content, new_content))

        # Generate recommendations
        comparison["recommendations"] = self._generate_recommendations(comparison)

        return comparison

    def compare_files(self, old_file: str | Path, new_file: str | Path) -> dict[str, Any]:
        """
        Compare two markdown files

        Args:
            old_file: Path to original file
            new_file: Path to updated file

        Returns:
            File comparison analysis
        """
        old_file = Path(old_file)
        new_file = Path(new_file)

        # Read files
        old_frontmatter, old_content = read_markdown_file(str(old_file))
        new_frontmatter, new_content = read_markdown_file(str(new_file))

        # Compare content
        content_comparison = self.compare_content(old_content, new_content)

        # Compare frontmatter
        frontmatter_comparison = self._compare_frontmatter(old_frontmatter, new_frontmatter)

        return {
            "file_comparison": {
                "old_file": str(old_file),
                "new_file": str(new_file),
                "content": content_comparison,
                "frontmatter": frontmatter_comparison
            }
        }

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity score between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _analyze_changes(self, old_text: str, new_text: str) -> dict[str, Any]:
        """Analyze specific types of changes between texts"""
        changes = {
            "additions": [],
            "deletions": [],
            "modifications": [],
            "word_count_change": len(new_text.split()) - len(old_text.split()),
            "sentence_count_change": new_text.count('.') - old_text.count('.')
        }

        # Use difflib to find detailed changes
        matcher = SequenceMatcher(None, old_text.split(), new_text.split())

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                changes["additions"].append(" ".join(new_text.split()[j1:j2]))
            elif tag == 'delete':
                changes["deletions"].append(" ".join(old_text.split()[i1:i2]))
            elif tag == 'replace':
                changes["modifications"].append({
                    "old": " ".join(old_text.split()[i1:i2]),
                    "new": " ".join(new_text.split()[j1:j2])
                })

        return changes

    def _analyze_data_changes(self, old_content: str, new_content: str) -> dict[str, Any]:
        """Analyze changes in data-heavy content (statistics, numbers, dates)"""
        data_analysis: dict[str, Any] = {
            "data_updates": [],
            "date_updates": [],
            "statistical_changes": [],
            "accuracy_improvements": []
        }

        # Find number/percentage changes
        number_pattern = r'\b\d+(?:\.\d+)?%?\b'
        old_numbers = re.findall(number_pattern, old_content)
        new_numbers = re.findall(number_pattern, new_content)

        if old_numbers != new_numbers:
            data_analysis["statistical_changes"] = {
                "old_values": old_numbers,
                "new_values": new_numbers
            }

        # Find date changes
        date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\b\d{4}\b'
        old_dates = re.findall(date_pattern, old_content)
        new_dates = re.findall(date_pattern, new_content)

        if old_dates != new_dates:
            data_analysis["date_updates"] = {
                "old_dates": old_dates,
                "new_dates": new_dates
            }

        return data_analysis

    def _analyze_citation_changes(self, old_content: str, new_content: str) -> dict[str, Any]:
        """Analyze changes in citations and references"""
        citation_analysis = {
            "new_citations": [],
            "removed_citations": [],
            "updated_citations": []
        }

        # Extract citations using markdown link pattern
        citation_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'

        old_citations = set(re.findall(citation_pattern, old_content))
        new_citations = set(re.findall(citation_pattern, new_content))

        citation_analysis["new_citations"] = list(new_citations - old_citations)
        citation_analysis["removed_citations"] = list(old_citations - new_citations)

        return citation_analysis

    def _analyze_general_changes(self, old_content: str, new_content: str) -> dict[str, Any]:
        """Analyze general content changes (tone, structure, clarity)"""
        general_analysis = {
            "tone_preserved": True,
            "structure_preserved": True,
            "clarity_improved": False,
            "unnecessary_rewording": False
        }

        # Check if structure is preserved (headers, sections)
        old_headers = re.findall(r'^#{1,6}\s+(.+)$', old_content, re.MULTILINE)
        new_headers = re.findall(r'^#{1,6}\s+(.+)$', new_content, re.MULTILINE)

        if old_headers != new_headers:
            general_analysis["structure_preserved"] = False

        # Check for unnecessary rewording (high similarity but different words)
        similarity = self._calculate_similarity(old_content, new_content)
        if 0.7 < similarity < 0.95:  # Similar but not identical
            # Check if changes are just rewording vs meaningful updates
            changes = self._analyze_changes(old_content, new_content)
            if len(changes["additions"]) == len(changes["deletions"]):
                general_analysis["unnecessary_rewording"] = True

        return general_analysis

    def _compare_frontmatter(self, old_fm: dict[str, Any], new_fm: dict[str, Any]) -> dict[str, Any]:
        """Compare frontmatter between files"""
        return {
            "changed_fields": [],
            "new_fields": list(set(new_fm.keys()) - set(old_fm.keys())),
            "removed_fields": list(set(old_fm.keys()) - set(new_fm.keys())),
            "modified_values": {
                key: {"old": old_fm[key], "new": new_fm[key]}
                for key in old_fm.keys() & new_fm.keys()
                if old_fm[key] != new_fm[key]
            }
        }

    def _generate_recommendations(self, comparison: dict[str, Any]) -> list[str]:
        """Generate recommendations based on comparison analysis"""
        recommendations = []

        similarity = comparison["overall_similarity"]
        changes = comparison["changes"]

        # High similarity with few meaningful changes
        if similarity > self.similarity_threshold:
            if changes["word_count_change"] < 10:
                recommendations.append("Consider preserving original content - changes appear minimal")

        # Check for unnecessary rewording
        if comparison.get("unnecessary_rewording", False):
            recommendations.append("Avoid unnecessary rewording - focus on accuracy and new information")

        # Data-specific recommendations
        if comparison.get("statistical_changes"):
            recommendations.append("Verify statistical updates are accurate and properly cited")

        # Citation-specific recommendations
        if comparison.get("new_citations"):
            recommendations.append("Ensure new citations are properly formatted and accessible")

        # Structure preservation
        if not comparison.get("structure_preserved", True):
            recommendations.append("Consider preserving existing structure for consistency")

        return recommendations

    def should_preserve_original(self, comparison: dict[str, Any]) -> bool:
        """
        Determine if original content should be preserved based on comparison

        Args:
            comparison: Result from compare_content()

        Returns:
            True if original content should be preserved
        """
        # Preserve if very similar and no meaningful improvements
        if comparison["overall_similarity"] > self.similarity_threshold:
            changes = comparison["changes"]

            # Check if changes are minimal and don't add value
            if (len(changes["additions"]) < 3 and
                len(changes["modifications"]) < 3 and
                not comparison.get("statistical_changes") and
                not comparison.get("new_citations")):
                return True

        # Preserve if marked as unnecessary rewording
        if comparison.get("unnecessary_rewording", False):
            return True

        return False
