"""
Infrastructure bridges connecting agents with utility systems
Provides orchestration layer for complex automation workflows
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass
from .content_update_applier import ContentUpdateApplier
from .page_config import get_page_config
from .validation_enhancer_factory import ValidationEnhancerFactory

logger = logging.getLogger(__name__)


class PageAutomationBridge:
    """
    Generalized bridge connecting agents with page automation infrastructure
    SIMPLIFIED: Removed hardcoded strategies, AI agents provide structured updates
    """

    def __init__(self, page_name: str, automation_controller: Any | None = None):
        self.page_name = page_name
        if automation_controller is not None:
            self.automation_controller = automation_controller
        else:
            # Import here to avoid circular import
            from ..automation_controller import AutomationController
            self.automation_controller = AutomationController()
        self.content_applier = ContentUpdateApplier()

        # Get page-specific configuration (metadata only, no update logic)
        self.page_config = get_page_config(page_name)
        self.validation_enhancer = ValidationEnhancerFactory.create_enhancer(page_name)

    def execute_automation(self) -> dict[str, Any]:
        """Execute complete page automation workflow"""
        logger.info(f"Starting {self.page_name}.md automation workflow")

        try:
            # Step 1: Process research
            logger.info(f"Processing {self.page_name} research")
            research_results = self._process_research()

            # Step 2: Apply content updates
            logger.info("Applying content updates")
            update_results = self._apply_content_updates(research_results)

            # Step 3: Validate content
            logger.info("Validating updated content")
            validation_results = self._validate_content()

            # Step 4: Build site
            logger.info("Building site")
            build_results = self._build_site()

            return {
                "success": True,
                "page": self.page_name,
                "research_processed": len(research_results),
                "updates_applied": update_results.get("updates_applied", 0),
                "validation_score": validation_results.get("score", 0.0),
                "build_time": build_results.get("build_time", 0.0),
                "workflow_stages": [
                    f"{self.page_name}_research",
                    "content_updates",
                    "validation",
                    "build"
                ]
            }

        except Exception as e:
            logger.error(f"{self.page_name} automation workflow failed: {e}")
            return {
                "success": False,
                "page": self.page_name,
                "error": str(e),
                "workflow_stages": []
            }

    def _process_research(self) -> list[dict[str, Any]]:
        """Process research for page content using configured agents"""
        research_files = []

        for agent_name in self.page_config.research_agents:
            # Map agent names to output directories
            agent_dir_map = {
                "social_researcher": "social_research",
                "technology_researcher": "technology_research",
                "market_researcher": "market_research",
                "policy_researcher": "policy_research"
            }

            output_dir = agent_dir_map.get(agent_name, agent_name)
            research_path = Path(f"src/agents/outputs/{output_dir}")

            if research_path.exists():
                for file_path in research_path.glob("*.md"):
                    research_files.append({
                        "file": str(file_path),
                        "content": file_path.read_text(),
                        "agent": agent_name
                    })

        return research_files

    def _apply_content_updates(self, research_results: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Apply research findings to page content
        SIMPLIFIED: AI agents will provide structured updates, no keyword matching
        TODO: Update to read structured output format from agents
        """
        content_path = Path(f"src/content/{self.page_config.content_file}")

        if not content_path.exists():
            raise FileNotFoundError(f"Content file not found: {content_path}")

        # TEMPORARY: Just log that updates would be applied
        # Will be replaced with structured update application
        logger.info(f"Would apply {len(research_results)} research results to {content_path}")
        logger.info("TODO: Implement structured update application from agent outputs")

        return {
            "success": True,
            "updates_applied": 0,
            "message": "Update application pending - agents need to output structured format"
        }

    def _validate_content(self) -> dict[str, Any]:
        """Validate page content quality"""
        content_path = Path(f"src/content/{self.page_config.content_file}")

        if not content_path.exists():
            return {"score": 0.0, "errors": ["Content file not found"]}

        content = content_path.read_text()
        return self.validation_enhancer.validate_content(content)

    def _build_site(self) -> dict[str, Any]:
        """Build the complete site"""
        return self.automation_controller.build_site()


# Legacy wrapper for backward compatibility - WILL BE REMOVED
class ActionAutomationBridge(PageAutomationBridge):
    """
    DEPRECATED: Legacy wrapper for ActionAutomationBridge
    Use PageAutomationBridge directly with page_name="action"
    This class will be removed in the next cleanup
    """

    def __init__(self, automation_controller: Any | None = None):
        logger.warning("ActionAutomationBridge is deprecated. Use PageAutomationBridge('action') instead.")
        super().__init__("action", automation_controller)

    def execute_action_automation(self) -> dict[str, Any]:
        """Legacy method - delegates to execute_automation"""
        logger.warning("execute_action_automation is deprecated. Use execute_automation() instead.")
        return self.execute_automation()
