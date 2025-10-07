"""
Enhanced Content Validator Agent - Uses ContentComparator for intelligent validation
Compares old vs new content to ensure meaningful updates while preserving quality
"""

import json
from pathlib import Path
from typing import Any

from crewai import Agent, Task
from crewai_tools import (  # type: ignore[import-untyped]
    SerperDevTool,
    WebsiteSearchTool,
)

from ..utils import read_markdown_file, setup_agent_environment
from ..utils.content_comparator import ContentComparator


class EnhancedContentValidatorAgent:
    """
    Enhanced content validator that compares old vs new content
    and makes intelligent decisions about content updates
    """

    def __init__(self, content_dir: str = "src/content"):
        self.content_dir = Path(content_dir)
        self.content_comparator = ContentComparator()

        # Setup agent environment
        setup_agent_environment()

        # Initialize CrewAI agent
        self.agent = Agent(
            role="Content Quality & Consistency Specialist",
            goal=(
                "Validate content updates by comparing old vs new versions. "
                "Ensure updates improve accuracy or add value without unnecessary "
                "rewording. Preserve existing quality content and maintain consistency."
            ),
            backstory=(
                "You are an expert content editor with deep expertise in maintaining "
                "editorial consistency. You understand that good content should only "
                "be changed when it improves accuracy, adds valuable information, or "
                "fixes errors. You avoid unnecessary rewording that doesn't improve "
                "meaning or clarity."
            ),
            tools=[SerperDevTool(), WebsiteSearchTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=15
        )

    def create_enhanced_validation_task(
        self,
        content_files: list[str] | None = None,
        research_findings: str = ""
    ) -> Task:
        """
        Create a task to validate content updates using comparison analysis

        Args:
            content_files: List of markdown files to validate
            research_findings: New research to consider for updates

        Returns:
            CrewAI Task for enhanced content validation
        """
        if content_files is None:
            content_files = [f.name for f in self.content_dir.glob("*.md")]

        task_description = f"""
        Perform enhanced content validation by comparing existing content with potential updates.

        Files to validate: {', '.join(content_files)}

        Validation Process:
        1. For each file, compare existing content with any proposed updates
        2. Identify changes that improve accuracy or add valuable information
        3. Flag unnecessary rewording that doesn't improve meaning
        4. Ensure all statistical claims and data points are current and accurate
        5. Verify all citations are accessible and properly formatted
        6. Maintain consistent tone and structure across all content

        Research Context:
        {research_findings[:500] + "..." if len(research_findings) > 500 else research_findings}

        Focus on:
        - Accuracy improvements based on latest research
        - Adding valuable new insights while preserving existing quality
        - Maintaining editorial consistency and professional tone
        - Ensuring proper citation of all claims
        """

        return Task(
            description=task_description,
            expected_output=(
                "Enhanced validation report with:\n"
                "- Content comparison analysis for each file\n"
                "- Recommendations for meaningful updates only\n"
                "- Identification of content that should be preserved\n"
                "- Accuracy verification of statistical claims\n"
                "- Citation accessibility check\n"
                "- Editorial consistency assessment"
            ),
            agent=self.agent
        )

    def validate_content_with_comparison(
        self,
        proposed_updates: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        Validate content by comparing current version with proposed updates

        Args:
            proposed_updates: Dictionary mapping file names to proposed new content

        Returns:
            Enhanced validation report with comparison analysis
        """
        if proposed_updates is None:
            proposed_updates = {}

        print("🔍 Performing enhanced content validation with comparison analysis...")

        validation_report: dict[str, Any] = {
            "validation_timestamp": "2025-01-27T12:00:00Z",
            "validation_type": "enhanced_comparison",
            "files_analyzed": 0,
            "comparisons": {},
            "recommendations": {},
            "preserve_original": {},
            "summary": {}
        }

        content_files = [f for f in self.content_dir.glob("*.md") if f.name != "references.md"]

        for file_path in content_files:
            file_name = file_path.name
            print(f"   📋 Analyzing {file_name}...")

            try:
                # Read current content
                current_frontmatter, current_content = read_markdown_file(str(file_path))

                # Check if there's a proposed update
                if file_name in proposed_updates:
                    proposed_content = proposed_updates[file_name]

                    # Perform comparison analysis
                    comparison = self.content_comparator.compare_content(
                        current_content,
                        proposed_content,
                        self._determine_content_type(file_name)
                    )

                    validation_report["comparisons"][file_name] = comparison
                    validation_report["recommendations"][file_name] = comparison["recommendations"]
                    validation_report["preserve_original"][file_name] = self.content_comparator.should_preserve_original(comparison)

                    print(f"   ✅ {file_name}: Similarity {comparison['overall_similarity']:.2f}")
                    if validation_report["preserve_original"][file_name]:
                        print(f"   📌 {file_name}: Recommend preserving original")

                else:
                    # Validate existing content without comparison
                    file_validation = self._validate_existing_content(file_path)
                    validation_report["comparisons"][file_name] = {
                        "type": "existing_only",
                        "validation": file_validation
                    }

                validation_report["files_analyzed"] += 1

            except Exception as e:
                print(f"   ❌ {file_name}: Validation failed - {e}")
                validation_report["comparisons"][file_name] = {
                    "error": f"Failed to analyze: {str(e)}"
                }

        # Generate summary
        validation_report["summary"] = self._generate_validation_summary(validation_report)

        # Save enhanced validation report
        report_file = self.content_dir.parent / "enhanced_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(validation_report, f, indent=2)

        print(f"📊 Enhanced validation complete. Report saved to {report_file}")
        return validation_report

    def _determine_content_type(self, file_name: str) -> str:
        """Determine content type for specialized analysis"""
        if file_name in ["economy.md", "technology.md"]:
            return "data"  # Data-heavy content
        elif file_name == "references.md":
            return "citations"  # Citation-heavy content
        else:
            return "general"  # General content

    def _validate_existing_content(self, file_path: Path) -> dict[str, Any]:
        """Validate existing content without comparison"""
        frontmatter, content = read_markdown_file(str(file_path))

        validation = {
            "word_count": len(content.split()),
            "citation_count": len(self._extract_citations(content)),
            "external_links": self._extract_links(content),
            "issues": [],
            "quality_indicators": {
                "has_citations": len(self._extract_citations(content)) > 0,
                "appropriate_length": 500 < len(content.split()) < 3000,
                "has_structure": content.count('#') > 2
            }
        }

        return validation

    def _extract_citations(self, content: str) -> list[str]:
        """Extract citations from content"""
        import re
        pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
        return re.findall(pattern, content)

    def _extract_links(self, content: str) -> list[str]:
        """Extract all external links from content"""
        import re
        pattern = r'https?://[^\s\)]+'
        return re.findall(pattern, content)

    def _generate_validation_summary(self, validation_report: dict[str, Any]) -> dict[str, Any]:
        """Generate summary of validation results"""
        comparisons = validation_report["comparisons"]
        preserve_count = sum(1 for preserve in validation_report["preserve_original"].values() if preserve)

        summary = {
            "total_files": validation_report["files_analyzed"],
            "files_with_comparisons": len([c for c in comparisons.values() if "overall_similarity" in c]),
            "files_to_preserve": preserve_count,
            "files_with_updates": len(comparisons) - preserve_count,
            "average_similarity": 0.0,
            "key_recommendations": []
        }

        # Calculate average similarity
        similarities = [
            c["overall_similarity"] for c in comparisons.values()
            if "overall_similarity" in c
        ]
        if similarities:
            summary["average_similarity"] = sum(similarities) / len(similarities)

        # Generate key recommendations
        if preserve_count > len(comparisons) * 0.7:
            summary["key_recommendations"].append("Most content is high quality - avoid unnecessary changes")

        if summary["average_similarity"] < 0.5:
            summary["key_recommendations"].append("Significant content changes detected - verify accuracy")

        return summary

    def create_content_update_recommendations(
        self,
        validation_report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create specific recommendations for content updates based on validation

        Args:
            validation_report: Result from validate_content_with_comparison

        Returns:
            Dictionary with specific update recommendations
        """
        recommendations = {
            "files_to_update": [],
            "files_to_preserve": [],
            "priority_updates": [],
            "citation_updates": [],
            "data_updates": []
        }

        for file_name, comparison in validation_report["comparisons"].items():
            if "overall_similarity" not in comparison:
                continue

            should_preserve = validation_report["preserve_original"].get(file_name, False)

            if should_preserve:
                recommendations["files_to_preserve"].append({
                    "file": file_name,
                    "reason": "High quality existing content with minimal meaningful changes"
                })
            else:
                recommendations["files_to_update"].append({
                    "file": file_name,
                    "similarity": comparison["overall_similarity"],
                    "key_changes": len(comparison["changes"]["modifications"])
                })

            # Check for data updates
            if comparison.get("statistical_changes"):
                recommendations["data_updates"].append({
                    "file": file_name,
                    "changes": comparison["statistical_changes"]
                })

            # Check for citation updates
            if comparison.get("new_citations"):
                recommendations["citation_updates"].append({
                    "file": file_name,
                    "new_citations": comparison["new_citations"]
                })

        return recommendations
