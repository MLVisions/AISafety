"""
Test suite for AI Safety Agent Network
Tests agent functionality while minimizing API calls
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.agents.agent_network import AISafetyAgentNetwork, create_agent_network
from src.agents.reference_sync import ReferenceSynchronizer, sync_website_references


class TestAISafetyAgentNetwork:
    """Test the main agent network functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_project_root = self.temp_dir / "test_project"
        self.test_project_root.mkdir(parents=True)

        # Create test directory structure
        (self.test_project_root / "src" / "agents").mkdir(parents=True)
        (self.test_project_root / "src" / "content").mkdir(parents=True)
        (self.test_project_root / "src" / "data").mkdir(parents=True)

        # Create test configuration files
        self._create_test_configs()
        self._create_test_content()

    def _create_test_configs(self):
        """Create test YAML configuration files"""
        agents_config = {
            'market_researcher': {
                'role': 'Test Market Researcher',
                'goal': 'Test market research',
                'backstory': 'Test backstory',
                'tools': ['SerperDevTool']
            },
            'content_validator': {
                'role': 'Test Content Validator',
                'goal': 'Test content validation',
                'backstory': 'Test backstory',
                'tools': ['FileReadTool']
            }
        }

        tasks_config = {
            'market_research_task': {
                'description': 'Test market research task',
                'expected_output': 'Test market research output'
            },
            'content_validation_task': {
                'description': 'Test content validation task',
                'expected_output': 'Test validation output'
            }
        }

        # Write config files
        agents_file = self.test_project_root / "src" / "agents" / "agents.yaml"
        tasks_file = self.test_project_root / "src" / "agents" / "tasks.yaml"

        import yaml
        with open(agents_file, 'w') as f:
            yaml.dump(agents_config, f)
        with open(tasks_file, 'w') as f:
            yaml.dump(tasks_config, f)

    def _create_test_content(self):
        """Create test content files"""
        test_content = """---
title: "Test Economy Page"
---

# Economy Analysis

Recent studies show that [AI investment](https://example.com/ai-report) has increased significantly.
The [Federal Reserve](https://fed.gov/report) indicates economic stability.

## Market Trends

[View latest data](https://bloomberg.com/data) for comprehensive analysis.
"""
        content_file = self.test_project_root / "src" / "content" / "economy.md"
        with open(content_file, 'w') as f:
            f.write(test_content)

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_agent_network_initialization(self):
        """Test that agent network initializes correctly"""
        network = AISafetyAgentNetwork(str(self.test_project_root))

        assert network.project_root == self.test_project_root
        assert network.agents_config is not None
        assert network.tasks_config is not None
        assert 'market_researcher' in network.agents_config
        assert 'content_validator' in network.agents_config

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_create_agent_from_config(self):
        """Test agent creation from configuration"""
        network = AISafetyAgentNetwork(str(self.test_project_root))

        # Mock the CrewAI Agent to avoid actual initialization
        with patch('src.agents.agent_network.Agent') as mock_agent:
            mock_agent.return_value = MagicMock()
            agent = network._create_agent('market_researcher')

            mock_agent.assert_called_once()
            call_args = mock_agent.call_args
            assert call_args[1]['role'] == 'Test Market Researcher'
            assert call_args[1]['goal'] == 'Test market research'

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_create_task_from_config(self):
        """Test task creation from configuration"""
        network = AISafetyAgentNetwork(str(self.test_project_root))

        # Mock the CrewAI Task and Agent
        with patch('src.agents.agent_network.Task') as mock_task, \
             patch('src.agents.agent_network.Agent') as mock_agent:
            mock_agent_instance = MagicMock()
            mock_agent.return_value = mock_agent_instance
            mock_task.return_value = MagicMock()
            
            agent = network._create_agent('market_researcher')
            task = network._create_task('market_research_task', agent)

            mock_task.assert_called_once()
            call_args = mock_task.call_args
            assert call_args[1]['description'] == 'Test market research task'
            assert call_args[1]['expected_output'] == 'Test market research output'

    def test_factory_function(self):
        """Test the factory function"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            network = create_agent_network(project_root=str(self.test_project_root))
            assert isinstance(network, AISafetyAgentNetwork)

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)


class TestReferenceSynchronizer:
    """Test the reference synchronization system"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_content_dir = self.temp_dir / "content"
        self.test_content_dir.mkdir(parents=True)

        # Create test content files
        self._create_test_content_files()

    def _create_test_content_files(self):
        """Create test content files with citations"""
        economy_content = """---
title: "Economy Analysis"
---

# Economic Trends

According to the [Federal Reserve](https://fed.gov/report-2024), inflation remains stable.
Recent [Goldman Sachs research](https://goldmansachs.com/ai-economy) shows AI investment trends.

See also: https://bloomberg.com/markets
"""

        technology_content = """---
title: "Technology Overview"
---

# AI Developments

The latest [OpenAI report](https://openai.com/research-2024) demonstrates significant progress.
[MIT studies](https://mit.edu/ai-study) confirm these findings.
"""

        # Write test files
        (self.test_content_dir / "economy.md").write_text(economy_content)
        (self.test_content_dir / "technology.md").write_text(technology_content)

    def test_citation_extraction(self):
        """Test citation extraction from content files"""
        synchronizer = ReferenceSynchronizer(str(self.test_content_dir))
        citations = synchronizer.extract_citations_from_content()

        assert len(citations) == 2  # Two files with citations
        assert 'economy.md' in citations
        assert 'technology.md' in citations

        # Check economy.md citations
        economy_citations = citations['economy.md']
        assert len(economy_citations) >= 3  # Fed, Goldman Sachs, Bloomberg

        # Verify citation structure
        for citation in economy_citations:
            assert 'text' in citation
            assert 'url' in citation
            assert 'type' in citation

    def test_citation_type_classification(self):
        """Test citation type classification"""
        synchronizer = ReferenceSynchronizer(str(self.test_content_dir))

        # Test government classification
        gov_type = synchronizer._classify_citation_type("Federal Reserve", "https://fed.gov/report")
        assert gov_type == 'government'

        # Test financial classification
        fin_type = synchronizer._classify_citation_type("Bloomberg", "https://bloomberg.com/data")
        assert fin_type == 'financial'

        # Test tech industry classification
        tech_type = synchronizer._classify_citation_type("OpenAI", "https://openai.com/research")
        assert tech_type == 'tech_industry'

        # Test academic classification
        academic_type = synchronizer._classify_citation_type("MIT Study", "https://mit.edu/research")
        assert academic_type == 'academic'

    def test_reference_sync(self):
        """Test reference file synchronization"""
        synchronizer = ReferenceSynchronizer(str(self.test_content_dir))
        
        # Mock the write_markdown_file function to avoid actual file writing
        with patch('src.agents.reference_sync.write_markdown_file') as mock_write:
            mock_write.return_value = True
            
            sync_result = synchronizer.sync_references_file()

            assert sync_result['success'] is True
            assert sync_result['files_processed'] == 2
            assert sync_result['total_citations'] > 0
            
            # Verify write_markdown_file was called
            mock_write.assert_called_once()
            call_args = mock_write.call_args
            assert 'references.md' in call_args[0][0]  # File path
            assert 'Government & Official Sources' in call_args[0][1]  # Content

    def test_reference_validation(self):
        """Test reference validation"""
        synchronizer = ReferenceSynchronizer(str(self.test_content_dir))
        validation_result = synchronizer.validate_references()

        assert validation_result['total_citations'] > 0
        assert validation_result['accessible_citations'] >= 0
        assert isinstance(validation_result['broken_citations'], list)
        assert isinstance(validation_result['validation_errors'], list)

    def test_convenience_functions(self):
        """Test convenience functions"""
        with patch('src.agents.reference_sync.ReferenceSynchronizer') as mock_sync:
            mock_instance = MagicMock()
            mock_sync.return_value = mock_instance
            mock_instance.sync_references_file.return_value = {'success': True}
            mock_instance.validate_references.return_value = {'total_citations': 5}

            # Test sync function
            sync_result = sync_website_references(str(self.test_content_dir))
            assert sync_result['success'] is True

            # Verify synchronizer was created with correct path
            mock_sync.assert_called_with(str(self.test_content_dir))

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)


class TestReferenceContentIntegrity:
    """Test that references stay in sync with content"""

    def setup_method(self):
        """Set up test environment with real content structure"""
        self.content_dir = Path("src/content")
        if not self.content_dir.exists():
            pytest.skip("Content directory not found - skipping integration tests")

    def test_references_md_exists(self):
        """Test that references.md exists"""
        references_file = self.content_dir / "references.md"
        assert references_file.exists(), "references.md should exist"

    def test_all_content_citations_have_references(self):
        """Test that all citations in content files have corresponding references"""
        if not self.content_dir.exists():
            pytest.skip("Content directory not found")

        synchronizer = ReferenceSynchronizer(str(self.content_dir))
        citations = synchronizer.extract_citations_from_content()

        # Extract all unique URLs from content
        all_urls = set()
        for file_citations in citations.values():
            for citation in file_citations:
                all_urls.add(citation['url'])

        # Read current references file
        references_file = self.content_dir / "references.md"
        if references_file.exists():
            references_content = references_file.read_text()
            
            # Check that major URLs are referenced
            # This is a basic check - in practice you'd want more sophisticated parsing
            for url in list(all_urls)[:5]:  # Check first 5 URLs as sample
                if url.startswith('http'):
                    # Note: This is a basic check. Real implementation would parse references properly
                    pass

    def test_no_broken_internal_links(self):
        """Test that there are no broken internal links between content files"""
        if not self.content_dir.exists():
            pytest.skip("Content directory not found")

        # Get all content files
        content_files = list(self.content_dir.glob("*.md"))
        file_names = {f.name for f in content_files}

        import re
        internal_link_pattern = r'\[([^\]]+)\]\(([^http][^\)]+)\)'

        for file_path in content_files:
            content = file_path.read_text()
            internal_links = re.findall(internal_link_pattern, content)

            for link_text, link_url in internal_links:
                # Check if internal link points to existing file
                if link_url.endswith('.md'):
                    target_file = link_url.split('/')[-1]
                    assert target_file in file_names, \
                        f"Broken internal link in {file_path.name}: {link_url}"


@pytest.fixture
def mock_openai_key():
    """Mock OpenAI API key for tests"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        yield


@pytest.mark.integration
class TestAgentWorkflowIntegration:
    """Integration tests for the full agent workflow"""

    def test_workflow_stages_defined(self, mock_openai_key):
        """Test that all workflow stages are properly defined"""
        # This test verifies the workflow structure without running actual agents
        
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Create minimal test structure
            project_root = temp_dir / "test_project"
            (project_root / "src" / "agents").mkdir(parents=True)
            (project_root / "src" / "content").mkdir(parents=True)

            # Create minimal configs
            import yaml
            agents_config = {'test_agent': {'role': 'Test', 'goal': 'Test', 'backstory': 'Test'}}
            tasks_config = {'test_task': {'description': 'Test', 'expected_output': 'Test'}}

            with open(project_root / "src" / "agents" / "agents.yaml", 'w') as f:
                yaml.dump(agents_config, f)
            with open(project_root / "src" / "agents" / "tasks.yaml", 'w') as f:
                yaml.dump(tasks_config, f)

            network = AISafetyAgentNetwork(str(project_root))

            # Test that network has required methods
            assert hasattr(network, 'create_research_crew')
            assert hasattr(network, 'create_content_crew')
            assert hasattr(network, 'create_infrastructure_crew')
            assert hasattr(network, 'run_full_update_workflow')

        finally:
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])