"""
Content Validation Utilities
Direct content validation functions without CrewAI agent overhead
"""

import re
from pathlib import Path
from typing import Any

from .file_operations import read_markdown_file
from .page_config import PAGE_CONFIGS


class ContentValidationUtils:
    """Utility class for direct content validation operations"""

    def __init__(self, content_dir: str = "src/content"):
        self.content_dir = Path(content_dir)

    def validate_content_direct(
        self,
        content_files: list[str] | None = None,
        check_links: bool = True,
        check_citations: bool = True
    ) -> dict[str, Any]:
        """
        Validate content directly without CrewAI agent

        Args:
            content_files: List of files to validate (validates all if None)
            check_links: Whether to check external links
            check_citations: Whether to validate citations

        Returns:
            Dictionary with validation results
        """
        if content_files is None:
            # Dynamically build from page configs
            content_files = [f"{page}.md" for page in PAGE_CONFIGS.keys()]

        print(f"Validating {len(content_files)} content files...")

        validation_results = {
            'validation_timestamp': str(Path.cwd()),
            'files_validated': len(content_files),
            'files_results': {},
            'overall_issues': {
                'broken_links': [],
                'citation_issues': [],
                'unsupported_claims': [],
                'formatting_issues': []
            }
        }

        for file_name in content_files:
            file_result = self._validate_single_file(Path(file_name))
            validation_results['files_results'][file_name] = file_result

            # Aggregate issues
            validation_results['overall_issues']['broken_links'].extend(
                file_result.get('broken_links', [])
            )
            validation_results['overall_issues']['citation_issues'].extend(
                file_result.get('citation_issues', [])
            )

        return validation_results

    def _validate_single_file(self, file_path: Path) -> dict[str, Any]:
        """Validate a single markdown file"""
        full_path = self.content_dir / file_path if not file_path.is_absolute() else file_path

        if not full_path.exists():
            return {
                'status': 'error',
                'error': f'File not found: {full_path}',
                'word_count': 0,
                'citation_count': 0,
                'link_count': 0,
                'broken_links': [],
                'citation_issues': [],
                'quality_indicators': {}
            }

        try:
            frontmatter, content = read_markdown_file(str(full_path))

            # Basic metrics
            word_count = len(content.split())
            citations = self._extract_citations(content)
            links = self._extract_links(content)

            # Quality analysis
            quality_indicators = {
                'has_citations': len(citations) > 0,
                'citation_density': len(citations) / max(word_count / 100, 1),  # Citations per 100 words
                'has_external_links': len(links) > 0,
                'word_count_adequate': word_count > 200,
            }

            # Identify potential issues
            claims = self._identify_claims(content)
            unsupported_claims = []

            for claim in claims:
                if not self._has_nearby_citation(content, claim):
                    unsupported_claims.append(claim)

            # Detect various content issues
            issues = []

            # Check for missing citations on claims
            for claim in unsupported_claims:
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

            # Calculate quality score
            quality_score = 100.0
            for issue in issues:
                if issue["severity"] == "high":
                    quality_score -= 20
                elif issue["severity"] == "medium":
                    quality_score -= 10
                else:
                    quality_score -= 5
            quality_score = max(0.0, quality_score)

            return {
                'status': 'success',
                'word_count': word_count,
                'citation_count': len(citations),
                'link_count': len(links),
                'citations': citations,
                'links': links,
                'quality_indicators': quality_indicators,
                'unsupported_claims': unsupported_claims[:5],  # Limit to first 5
                'issues': issues,
                'quality_score': quality_score,
                'broken_links': [],  # Would need network check
                'citation_issues': []
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'word_count': 0,
                'citation_count': 0,
                'link_count': 0
            }

    def _extract_citations(self, content: str) -> list[str]:
        """Extract markdown citations from content"""
        # Pattern for markdown links: [text](url)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)

        # Filter for citations (exclude internal links)
        citations = []
        for text, url in matches:
            if url.startswith('http') or url.startswith('https'):
                citations.append(f"[{text}]({url})")

        return citations

    def _extract_links(self, content: str) -> list[str]:
        """Extract all links from content"""
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        return [url for text, url in matches]

    def _identify_claims(self, content: str) -> list[str]:
        """Identify statistical claims that likely need citations"""
        # Enhanced patterns matching the simple_agent approach
        claim_patterns = [
            r'[^.!?]*\d+%[^.!?]*[.!?]',  # Sentences with percentages
            r'[^.!?]*\$[\d,]+[^.!?]*[.!?]',  # Sentences with dollar amounts
            r'[^.!?]*\d{4}[^.!?]*[.!?]',  # Sentences with years
            r'[^.!?]*\d+(\.\d+)?\s*(million|billion|trillion)[^.!?]*[.!?]'  # Large numbers
        ]

        claims = []
        for pattern in claim_patterns:
            # Use finditer to get match objects, then extract the full match
            for match in re.finditer(pattern, content, re.IGNORECASE):
                claims.append(match.group(0))

        return claims[:10]  # Limit to avoid too many

    def _has_nearby_citation(self, content: str, claim: str) -> bool:
        """Check if a claim has a citation nearby in the text"""
        # Find claim position
        claim_pos = content.find(claim)
        if claim_pos == -1:
            return False

        # Check for citations in nearby text (within 200 characters)
        nearby_text = content[max(0, claim_pos-100):claim_pos+len(claim)+100]

        # Look for citation patterns (enhanced from simple_agent)
        citation_patterns = [
            r'\[([^\]]+)\]\([^)]+\)',  # Markdown links
            r'\[\^[^\]]+\]',          # Footnotes
            r'\([^)]*https?://[^)]*\)'  # Inline URLs
        ]

        for pattern in citation_patterns:
            if re.search(pattern, nearby_text):
                return True

        return False
