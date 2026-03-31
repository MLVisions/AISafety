"""
Content Validation Utilities.
Direct content validation functions for checking link quality, citations, etc.
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .file_operations import read_markdown_file
from .page_config import PAGE_CONFIGS
from .patterns import extract_external_citations, extract_markdown_links


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
        Validate content files for link quality, citations, and claims

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

        validation_results: dict[str, Any] = {
            'validation_timestamp': datetime.now(tz=timezone.utc).isoformat(),
            'files_validated': len(content_files),
            'files_results': {},
            'overall_issues': {
                'broken_links': [],
                'citation_issues': [],
                'unsupported_claims': [],
                'formatting_issues': []
            }
        }

        # Use typed references to avoid mypy indexed-assignment errors
        files_results: dict[str, Any] = validation_results['files_results']
        overall_issues: dict[str, list[Any]] = validation_results['overall_issues']

        for file_name in content_files:
            file_result = self.validate_single_file(Path(file_name))
            files_results[file_name] = file_result

            # Aggregate issues
            overall_issues['broken_links'].extend(
                file_result.get('broken_links', [])
            )
            overall_issues['citation_issues'].extend(
                file_result.get('citation_issues', [])
            )

        return validation_results

    def validate_single_file(self, file_path_or_name: str | Path) -> dict[str, Any]:
        """Validate a single markdown file"""
        file_path = Path(file_path_or_name)
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
            citations = extract_external_citations(content)
            links = [url for _, url in extract_markdown_links(content)]

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
            required_frontmatter = ['title']
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
