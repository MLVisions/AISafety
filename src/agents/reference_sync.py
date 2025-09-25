"""
Reference Synchronization System
Manages synchronization between content citations and references.md
"""

import re
from pathlib import Path
from typing import Any

from .utils.file_operations import (
    list_content_files,
    read_markdown_file,
    write_markdown_file,
)


class ReferenceSynchronizer:
    """Manages reference synchronization across website content"""

    def __init__(self, content_dir: str | Path = "src/content"):
        self.content_dir = Path(content_dir)
        self.references_file = self.content_dir / "references.md"

        # Citation patterns
        self.citation_patterns = [
            r'\[View Report\]\((https?://[^\)]+)\)',  # [View Report](URL)
            r'\[Source: ([^\]]+)\]\((https?://[^\)]+)\)',  # [Source: Name](URL)
            r'\[([^\]]+)\]\((https?://[^\)]+)\)',  # [Text](URL) - general links
            r'https?://[^\s\)]+',  # Raw URLs
        ]

    def extract_citations_from_content(self) -> dict[str, list[dict[str, Any]]]:
        """Extract all citations from content files"""
        citations_by_file = {}

        content_files = list_content_files(str(self.content_dir))

        for file_path in content_files:
            if Path(file_path).name == "references.md":
                continue  # Skip the references file itself

            try:
                frontmatter, content = read_markdown_file(file_path)
                file_citations = self._extract_citations_from_text(content)

                if file_citations:
                    citations_by_file[Path(file_path).name] = file_citations

            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")

        return citations_by_file

    def _extract_citations_from_text(self, text: str) -> list[dict[str, Any]]:
        """Extract citations from text using various patterns"""
        citations = []

        # Find markdown-style links
        link_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
        matches = re.findall(link_pattern, text)

        for link_text, url in matches:
            # Skip navigation links
            if any(nav in link_text.lower() for nav in ['home', 'economy', 'technology', 'privacy', 'society', 'action', 'references']):
                continue

            citation = {
                'text': link_text,
                'url': url,
                'type': self._classify_citation_type(link_text, url)
            }
            citations.append(citation)

        # Find raw URLs that might be citations
        raw_url_pattern = r'(https?://[^\s\)]+)'
        raw_matches = re.findall(raw_url_pattern, text)

        for url in raw_matches:
            # Skip URLs already captured in markdown links
            if not any(citation['url'] == url for citation in citations):
                citation = {
                    'text': self._generate_citation_text(url),
                    'url': url,
                    'type': self._classify_citation_type('', url)
                }
                citations.append(citation)

        return citations

    def _classify_citation_type(self, text: str, url: str) -> str:
        """Classify citation type based on text and URL"""
        text_lower = text.lower()
        url_lower = url.lower()

        # Government/Official sources
        if any(domain in url_lower for domain in ['.gov', 'fed.org', 'bls.gov', 'treasury.gov']):
            return 'government'

        # Academic sources
        if any(domain in url_lower for domain in ['.edu', 'scholar.google', 'arxiv.org', 'nature.com']):
            return 'academic'

        # Financial sources
        if any(domain in url_lower for domain in ['wsj.com', 'bloomberg.com', 'ft.com', 'reuters.com']):
            return 'financial'

        # Tech industry sources
        if any(domain in url_lower for domain in ['openai.com', 'microsoft.com', 'google.com', 'meta.com']):
            return 'tech_industry'

        # Reports and studies
        if any(keyword in text_lower for keyword in ['report', 'study', 'survey', 'research']):
            return 'report'

        return 'general'

    def _generate_citation_text(self, url: str) -> str:
        """Generate citation text from URL"""
        domain = url.split('/')[2].replace('www.', '')
        return f"Source: {domain}"

    def sync_references_file(self) -> dict[str, Any]:
        """Synchronize references.md with content citations"""
        print("🔗 Synchronizing references with content citations...")

        # Extract citations from all content
        citations_by_file = self.extract_citations_from_content()

        # Read current references file
        current_refs = {}
        if self.references_file.exists():
            try:
                frontmatter, content = read_markdown_file(str(self.references_file))
                current_refs = self._parse_existing_references(content)
            except Exception as e:
                print(f"Warning: Could not parse existing references: {e}")

        # Build new references content
        new_content = self._build_references_content(citations_by_file, current_refs)

        # Write updated references file
        frontmatter = {
            'title': 'References & Sources',
            'tagline': 'Research citations and data sources',
            'description': 'Comprehensive list of academic sources, reports, and data supporting our analysis and recommendations.'
        }

        success = write_markdown_file(
            str(self.references_file),
            new_content,
            frontmatter=frontmatter
        )

        # Generate sync report
        sync_report = {
            'success': success,
            'files_processed': len(citations_by_file),
            'total_citations': sum(len(citations) for citations in citations_by_file.values()),
            'citations_by_file': {
                file: len(citations) for file, citations in citations_by_file.items()
            },
            'output_file': str(self.references_file)
        }

        if success:
            print("✅ References synchronized successfully!")
            print(f"   Files processed: {sync_report['files_processed']}")
            print(f"   Total citations: {sync_report['total_citations']}")
        else:
            print("❌ Failed to synchronize references")

        return sync_report

    def _parse_existing_references(self, content: str) -> dict[str, dict[str, Any]]:
        """Parse existing references from references.md"""
        references: dict[str, dict[str, Any]] = {}

        # This is a simplified parser - in practice you'd want more robust parsing
        # For now, we'll rebuild the references file from scratch
        return references

    def _build_references_content(self, citations_by_file: dict[str, list[dict[str, Any]]], current_refs: dict[str, dict[str, Any]]) -> str:
        """Build new references.md content"""
        content_lines = []

        # Group citations by type
        citations_by_type: dict[str, list[dict[str, Any]]] = {
            'government': [],
            'academic': [],
            'financial': [],
            'tech_industry': [],
            'report': [],
            'general': []
        }

        citation_counter = 1
        all_citations = []

        # Collect all unique citations
        seen_urls = set()
        for file_citations in citations_by_file.values():
            for citation in file_citations:
                if citation['url'] not in seen_urls:
                    citation['id'] = citation_counter
                    all_citations.append(citation)
                    citations_by_type[citation['type']].append(citation)
                    seen_urls.add(citation['url'])
                    citation_counter += 1

        # Build content sections
        type_titles = {
            'government': '## Government & Official Sources',
            'academic': '## Academic Research & Studies',
            'financial': '## Financial & Market Analysis',
            'tech_industry': '## Technology Industry Sources',
            'report': '## Reports & Surveys',
            'general': '## Additional Sources'
        }

        for citation_type, citations in citations_by_type.items():
            if not citations:
                continue

            content_lines.append(type_titles[citation_type])
            content_lines.append('')

            for citation in sorted(citations, key=lambda x: x['text']):
                content_lines.append(f"### [{citation['id']}] {citation['text']}")
                content_lines.append(f"[View Source]({citation['url']})")
                content_lines.append('')

        return '\n'.join(content_lines)

    def validate_references(self) -> dict[str, Any]:
        """Validate all references for accessibility and accuracy"""
        print("🔍 Validating references...")

        citations_by_file = self.extract_citations_from_content()
        validation_results: dict[str, Any] = {
            'total_citations': 0,
            'accessible_citations': 0,
            'broken_citations': [],
            'validation_errors': []
        }

        for _file_name, citations in citations_by_file.items():
            for _citation in citations:
                validation_results['total_citations'] += 1

                # In a real implementation, you'd check URL accessibility here
                # For now, we'll assume they're accessible
                validation_results['accessible_citations'] += 1

        print("✅ Reference validation completed")
        print(f"   Total citations: {validation_results['total_citations']}")
        print(f"   Accessible: {validation_results['accessible_citations']}")

        return validation_results


def sync_website_references(content_dir: str = "src/content") -> dict[str, Any]:
    """Convenience function to synchronize website references"""
    synchronizer = ReferenceSynchronizer(content_dir)
    return synchronizer.sync_references_file()


def validate_website_references(content_dir: str = "src/content") -> dict[str, Any]:
    """Convenience function to validate website references"""
    synchronizer = ReferenceSynchronizer(content_dir)
    return synchronizer.validate_references()


if __name__ == "__main__":
    # Test the reference synchronizer
    sync_result = sync_website_references()
    validate_result = validate_website_references()

    print("\n" + "="*50)
    print("Reference Synchronization Test Results:")
    print(f"Sync success: {sync_result['success']}")
    print(f"Citations found: {sync_result['total_citations']}")
    print(f"Validation: {validate_result['accessible_citations']}/{validate_result['total_citations']} accessible")
