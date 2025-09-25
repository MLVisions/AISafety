"""
Content Validator Agent - Simple Agent for validating website content
Checks citations, fact-checks content, and ensures quality standards
"""

import json
import re
from pathlib import Path
from typing import Any

from crewai import Agent, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool

from ..utils import read_markdown_file


class ContentValidatorAgent:
    """Agent responsible for validating and fact-checking website content"""

    def __init__(self, content_dir: str = "src/content"):
        self.content_dir = Path(content_dir)

        # Initialize CrewAI agent
        self.agent = Agent(
            role="Content Quality Assurance Specialist",
            goal=(
                "Verify the accuracy, completeness, and quality of website content. "
                "Ensure all claims are properly cited, facts are current and accurate, "
                "and content maintains editorial standards."
            ),
            backstory=(
                "You are a meticulous fact-checker and content editor with expertise "
                "in financial markets, AI technology, and research methodology. You "
                "have a keen eye for detecting misinformation, incomplete citations, "
                "and content that needs improvement."
            ),
            tools=[SerperDevTool(), WebsiteSearchTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=15
        )

    def create_validation_task(self, content_files: list[str] | None = None) -> Task:
        """
        Create a task to validate content files

        Args:
            content_files: List of markdown files to validate (all if None)

        Returns:
            CrewAI Task for content validation
        """
        if content_files is None:
            content_files = [f.name for f in self.content_dir.glob("*.md")]

        description = f"""
        Validate the following content files for accuracy and quality: {', '.join(content_files)}

        Validation checks to perform:
        1. Citation verification - ensure all claims have proper sources
        2. Fact-checking - verify key statistics and statements using web search
        3. Link validation - check that all external links are working
        4. Content consistency - ensure information aligns across pages
        5. Editorial quality - check for clarity, grammar, and style

        For each file:
        - Read the markdown content from {self.content_dir}
        - Identify any unsupported claims or questionable statements
        - Verify key facts using web search
        - Check all external links for accessibility
        - Document any issues found

        Create a validation report with:
        - Summary of issues found per file
        - Specific recommendations for improvement
        - Priority level for each issue (high/medium/low)
        - Suggested corrections or additional sources
        """

        return Task(
            description=description,
            agent=self.agent,
            expected_output=(
                "A comprehensive validation report in JSON format containing "
                "issues found, fact-check results, and improvement recommendations "
                "for each content file."
            )
        )

    def validate_content_direct(
        self,
        content_files: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Direct method to validate content without CrewAI task orchestration

        Args:
            content_files: List of markdown files to validate

        Returns:
            Validation report dictionary
        """
        if content_files is None:
            content_files = [f.name for f in self.content_dir.glob("*.md")]

        print(f"📋 Validating {len(content_files)} content files...")

        validation_report: dict[str, Any] = {
            "validation_timestamp": "2025-01-27T12:00:00Z",  # Current date
            "files_validated": len(content_files),
            "files": {}
        }

        for file_name in content_files:
            print(f"   🔍 Validating {file_name}...")
            file_path = self.content_dir / file_name

            try:
                file_report = self._validate_single_file(file_path)
                validation_report["files"][file_name] = file_report
                print(f"   ✅ {file_name}: {len(file_report.get('issues', []))} issues found")
            except Exception as e:
                validation_report["files"][file_name] = {
                    "error": f"Failed to validate: {str(e)}"
                }
                print(f"   ❌ {file_name}: Validation failed - {e}")

        # Save validation report
        report_file = self.content_dir.parent / "validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(validation_report, f, indent=2)

        print(f"📊 Content validation complete. Report saved to {report_file}")
        return validation_report

    def _validate_single_file(self, file_path: Path) -> dict[str, Any]:
        """Validate a single markdown file"""
        frontmatter, content = read_markdown_file(file_path)

        file_report = {
            "frontmatter": frontmatter,
            "word_count": len(content.split()),
            "issues": [],
            "citations": self._extract_citations(content),
            "external_links": self._extract_links(content),
            "quality_score": 0.0
        }

        # Check for basic content issues
        issues = []

        # Check for missing citations on claims
        claims = self._identify_claims(content)
        for claim in claims:
            if not self._has_nearby_citation(content, claim):
                issues.append({
                    "type": "missing_citation",
                    "severity": "medium",
                    "description": f"Statistical claim may need citation: {claim[:100]}...",
                    "suggestion": "Add source citation for this claim"
                })

        # Check for outdated content indicators
        outdated_indicators = ['2020', '2021', '2022', 'last year', 'recently']
        for indicator in outdated_indicators:
            if indicator in content.lower():
                issues.append({
                    "type": "potential_outdated",
                    "severity": "low",
                    "description": f"Content may reference outdated information: '{indicator}'",
                    "suggestion": "Review and update date-specific references"
                })

        # Check frontmatter completeness
        required_frontmatter = ['title', 'description']
        for field in required_frontmatter:
            if field not in frontmatter:
                issues.append({
                    "type": "missing_frontmatter",
                    "severity": "high",
                    "description": f"Missing required frontmatter field: {field}",
                    "suggestion": f"Add {field} to file frontmatter"
                })

        file_report["issues"] = issues

        # Calculate quality score (simple heuristic)
        quality_score = 100.0
        for issue in issues:
            if issue["severity"] == "high":
                quality_score -= 20
            elif issue["severity"] == "medium":
                quality_score -= 10
            else:
                quality_score -= 5

        file_report["quality_score"] = max(0.0, quality_score)

        return file_report

    def _extract_citations(self, content: str) -> list[str]:
        """Extract citations from markdown content"""
        # Look for markdown links and footnotes
        citations = []

        # Markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        citations.extend(re.findall(link_pattern, content))

        # Footnotes: [^footnote]
        footnote_pattern = r'\[\^([^\]]+)\]'
        footnotes = re.findall(footnote_pattern, content)
        citations.extend([(f"footnote:{fn}", "") for fn in footnotes])

        return citations

    def _extract_links(self, content: str) -> list[str]:
        """Extract external links from content"""
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)

        # Filter for external links (http/https)
        external_links = []
        for _text, url in matches:
            if url.startswith(('http://', 'https://')):
                external_links.append(url)

        return external_links

    def _identify_claims(self, content: str) -> list[str]:
        """Identify statistical claims that likely need citations"""
        # Simple pattern matching for claims with numbers/percentages
        claim_patterns = [
            r'[^.!?]*\d+%[^.!?]*[.!?]',  # Sentences with percentages
            r'[^.!?]*\$[\d,]+[^.!?]*[.!?]',  # Sentences with dollar amounts
            r'[^.!?]*\d{4}[^.!?]*[.!?]',  # Sentences with years
            r'[^.!?]*\d+(\.\d+)?\s*(million|billion|trillion)[^.!?]*[.!?]'  # Large numbers
        ]

        claims = []
        for pattern in claim_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            claims.extend(matches)

        return claims[:10]  # Limit to avoid too many

    def _has_nearby_citation(self, content: str, claim: str) -> bool:
        """Check if a claim has a citation nearby in the text"""
        # Find claim position
        claim_pos = content.find(claim)
        if claim_pos == -1:
            return False

        # Check for citations in nearby text (within 200 characters)
        nearby_text = content[max(0, claim_pos-100):claim_pos+len(claim)+100]

        # Look for citation patterns
        citation_patterns = [
            r'\[([^\]]+)\]\([^)]+\)',  # Markdown links
            r'\[\^[^\]]+\]',          # Footnotes
            r'\([^)]*https?://[^)]*\)'  # Inline URLs
        ]

        for pattern in citation_patterns:
            if re.search(pattern, nearby_text):
                return True

        return False


def create_content_validator_agent(content_dir: str = "src/content") -> ContentValidatorAgent:
    """Factory function to create a ContentValidatorAgent"""
    return ContentValidatorAgent(content_dir=content_dir)


if __name__ == "__main__":
    # Test the agent
    agent = create_content_validator_agent()

    # Test direct validation
    report = agent.validate_content_direct()

    print(f"Validation complete. {report['files_validated']} files processed.")
    for filename, file_report in report['files'].items():
        if 'issues' in file_report:
            print(f"  {filename}: {len(file_report['issues'])} issues, "
                  f"quality score: {file_report.get('quality_score', 0):.1f}")
        else:
            print(f"  {filename}: Error - {file_report.get('error', 'Unknown')}")
