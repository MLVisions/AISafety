"""
Integration tests for action automation workflow
Tests the complete end-to-end automation pipeline
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.agents.utils.validation_enhancer_factory import ValidationEnhancerFactory
from src.agents.utils.content_update_applier import ContentUpdateApplier
from src.agents.utils.infrastructure_bridges import PageAutomationBridge


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

        base_validation = {
            'success': True,
            'quality_score': 0.7,
            'issues': []
        }

        enhanced = enhancer.validate_content(action_content)

        # Verify enhancement worked
        assert 'action_quality_score' in enhanced
        assert 'strategy_feasibility' in enhanced
        assert 'resource_accessibility' in enhanced
        assert 'clarity_score' in enhanced
        assert 'actionability_score' in enhanced

        # Action content should score well on actionability
        assert enhanced['actionability_score'] > 0.5
        assert enhanced['clarity_score'] > 0.5

    def test_content_update_applier_parsing(self):
        """Test content update applier parsing capabilities"""
        applier = ContentUpdateApplier()

        # Test research findings parsing
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
        assert 'statistics' in categories or 'recommendations' in categories

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

    @patch('src.agents.utils.infrastructure_bridges.ActionAutomationBridge._rebuild_website')
    @patch('src.agents.utils.infrastructure_bridges.ActionAutomationBridge._apply_content_updates')
    def test_action_automation_workflow_logic(self, mock_apply_updates, mock_rebuild):
        """Test the automation workflow logic without actual file operations"""

        # Mock successful operations
        mock_apply_updates.return_value = {
            "step": "content_update_application",
            "success": True,
            "updates_applied": 5,
            "validation_score": 0.8,
            "backup_created": True
        }

        mock_rebuild.return_value = {
            "step": "website_rebuild",
            "success": True,
            "build_time": 1.5,
            "pages_built": 8,
            "plots_generated": 15
        }

        bridge = ActionAutomationBridge()

        # Create test automation output
        automation_dir = Path("automation_outputs")
        automation_dir.mkdir(exist_ok=True)

        test_research = automation_dir / "social_research_workflow_test.md"
        test_research.write_text("""
        # Social Research Findings
        
        ## Key Developments
        Recent research shows increased importance of community building.
        AI displacement affecting 85 million jobs by 2027.
        
        ## Recommendations
        Update statistics and emphasize practical strategies.
        """)

        try:
            # Test workflow steps individually
            research_result = bridge._process_social_research()
            assert research_result["success"] == True
            assert research_result["files_processed"] > 0

            # Test validation step
            validation_result = bridge._validate_action_content(research_result["research_data"])
            assert validation_result["success"] == True
            assert "enhanced_score" in validation_result

        finally:
            # Clean up
            if test_research.exists():
                test_research.unlink()
            if automation_dir.exists() and not any(automation_dir.iterdir()):
                automation_dir.rmdir()

    def test_action_content_validation_integration(self):
        """Test integration between content validation and action enhancement"""
        from src.agents.utils.content_validation_utils import ContentValidationUtils

        validator = ContentValidationUtils()
        enhancer = ActionValidationEnhancer()

        # Test with actual action.md file
        base_validation = validator.validate_content_direct(
            content_files=['action.md'],
            check_links=False
        )

        # Verify validation worked
        assert 'files_results' in base_validation
        assert 'action.md' in base_validation['files_results']

        file_result = base_validation['files_results']['action.md']
        assert file_result['status'] != 'error'

        # Read action content for enhancement
        action_file = Path('src/content/action.md')
        if action_file.exists():
            with open(action_file, encoding='utf-8') as f:
                action_content = f.read()

            # Create formatted validation result
            base_formatted = {
                'success': file_result.get('status') != 'error',
                'quality_score': file_result.get('quality_score', 50) / 100.0,
                'issues': file_result.get('issues', []),
                'word_count': file_result.get('word_count', 0)
            }

            # Test enhancement integration
            enhanced = enhancer.enhance_validation(action_content, base_formatted)

            # Verify integration worked
            assert enhanced['quality_score'] >= 0
            assert enhanced['quality_score'] <= 1
            assert 'action_quality_score' in enhanced

    def test_workflow_summary_generation(self):
        """Test workflow summary generation"""
        bridge = ActionAutomationBridge()

        # Test with sample workflow steps
        workflow_steps = [
            {"step": "research", "success": True, "files_processed": 2},
            {"step": "validation", "success": True, "enhanced_score": 0.85},
            {"step": "update", "success": True, "updates_applied": 5},
            {"step": "build", "success": False, "error": "Test error"}
        ]

        summary = bridge._generate_workflow_summary(workflow_steps)

        # Verify summary metrics
        assert summary["total_steps"] == 4
        assert summary["successful_steps"] == 3
        assert summary["success_rate"] == 0.75
        assert summary["research_files_processed"] == 2
        assert summary["content_updates_applied"] == 5
        assert summary["final_validation_score"] == 0.85


@pytest.mark.integration
class TestActionAutomationFullIntegration:
    """Full integration tests requiring all components"""

    def test_action_automation_pipeline_integration(self):
        """Test the complete action automation pipeline"""
        # This test verifies that all components work together
        # but doesn't actually modify files

        bridge = ActionAutomationBridge()

        # Verify all required components initialize
        assert bridge.content_updater is not None
        assert bridge.content_validator is not None
        assert bridge.build_orchestrator is not None
        assert bridge.action_validator is not None

        # Verify automation outputs directory handling
        automation_dir = Path("automation_outputs")
        if not automation_dir.exists():
            automation_dir.mkdir()

        # Test research file detection
        files = bridge._find_research_files(["social", "action"])
        assert isinstance(files, list)  # Should return list even if empty

        # Clean up if we created the directory
        if automation_dir.exists() and not any(automation_dir.iterdir()):
            automation_dir.rmdir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
