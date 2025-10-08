"""
Integration tests for action automation workflow
Tests the complete end-to-end automation pipeline
"""

from pathlib import Path
from unittest.mock import patch

from src.agents.utils.content_update_applier import ContentUpdateApplier
from src.agents.utils.infrastructure_bridges import PageAutomationBridge
from src.agents.utils.validation_enhancer_factory import ValidationEnhancerFactory


class TestActionAutomationIntegration:
    """Integration tests for action automation workflow"""

    def test_action_validation_enhancer(self):
        """Test action-specific validation enhancements"""
        enhancer = ValidationEnhancerFactory.create_enhancer("action")

        # Test with action-oriented content
        action_content = """
        ### Build community
        **Form local AI-check groups**
        
        Join or organise local groups to share knowledge and support mental health.
        These groups provide practical steps you can take today.
        """

        enhanced = enhancer.validate_content(action_content)

        # Verify enhancement worked
        assert 'score' in enhanced
        assert 'strategy_feasibility' in enhanced
        assert 'resource_accessibility' in enhanced
        assert 'clarity' in enhanced
        assert 'actionability' in enhanced

        # Action content should have validation metrics
        assert enhanced['actionability'] >= 0
        assert enhanced['clarity'] >= 0

    def test_content_update_applier_parsing(self):
        """Test content update applier parsing capabilities"""
        applier = ContentUpdateApplier()

        # Test research findings parsing (legacy method still exists)
        research_findings = """
        ## Key Developments
        
        ### Employment Trends
        Recent studies show that 85 million jobs could be affected by 2027.
        
        ### Skill Requirements  
        Data literacy is becoming increasingly valuable.
        
        ## Recommendations
        1. Update employment statistics
        2. Emphasize community building
        """

        suggestions = applier._parse_research_findings(research_findings)

        # Verify parsing extracted suggestions
        assert len(suggestions) > 0

        # Check for different types of suggestions
        categories = [s['category'] for s in suggestions]
        assert any(cat in categories for cat in ['statistics', 'recommendations', 'trends'])

    def test_page_automation_bridge_initialization(self):
        """Test PageAutomationBridge initialization"""
        # Test with action page
        bridge = PageAutomationBridge("action")

        # Verify bridge has correct configuration
        assert bridge.page_name == "action"
        assert bridge.page_config.page_name == "action"
        assert bridge.page_config.content_file == "action.md"
        assert "social_researcher" in bridge.page_config.research_agents

        # Test with technology page
        tech_bridge = PageAutomationBridge("technology")
        assert tech_bridge.page_name == "technology"
        assert tech_bridge.page_config.content_file == "technology.md"
        assert "technology_researcher" in tech_bridge.page_config.research_agents

    def test_page_automation_bridge_methods_exist(self):
        """Test that PageAutomationBridge has expected methods"""
        bridge = PageAutomationBridge("action")

        # Check that key methods exist
        assert hasattr(bridge, 'execute_automation')
        assert hasattr(bridge, '_process_research')
        assert hasattr(bridge, '_apply_content_updates')
        assert hasattr(bridge, '_validate_content')
        assert hasattr(bridge, '_build_site')

    @patch('src.agents.utils.infrastructure_bridges.Path.exists')
    @patch('src.agents.utils.infrastructure_bridges.Path.read_text')
    def test_process_research(self, mock_read_text, mock_exists):
        """Test research processing"""
        bridge = PageAutomationBridge("action")

        # Mock file system
        mock_exists.return_value = True
        mock_read_text.return_value = "Research content"

        with patch('src.agents.utils.infrastructure_bridges.Path.glob', return_value=[Path("test.md")]):
            results = bridge._process_research()

            # Should return a list of research results
            assert isinstance(results, list)

    @patch('pathlib.Path.exists')
    def test_validate_content(self, mock_exists):
        """Test content validation"""
        bridge = PageAutomationBridge("action")

        # Mock file exists
        mock_exists.return_value = True

        with patch('pathlib.Path.read_text', return_value="Test content"):
            result = bridge._validate_content()

            # Should return validation result with score
            assert isinstance(result, dict)
            assert 'score' in result

    def test_validation_enhancer_factory_creates_correct_enhancers(self):
        """Test that factory creates appropriate enhancers for each page"""
        pages = ["action", "technology", "llm", "economy", "society", "privacy"]

        for page in pages:
            enhancer = ValidationEnhancerFactory.create_enhancer(page)
            assert enhancer is not None
            assert hasattr(enhancer, 'validate_content')

            # Test that validation works
            result = enhancer.validate_content("Sample content for testing.")
            assert isinstance(result, dict)
            assert 'score' in result
