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
            # Convention: agent name "xxx_researcher" maps to "xxx_research" output directory
            # This makes it easy to add new agents without code changes
            if agent_name.endswith("_researcher"):
                output_dir = agent_name.replace("_researcher", "_research")
            else:
                output_dir = agent_name

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
        SIMPLIFIED: Reads structured JSON output from agents and applies updates
        """
        import json

        content_path = Path(f"src/content/{self.page_config.content_file}")

        if not content_path.exists():
            raise FileNotFoundError(f"Content file not found: {content_path}")

        # Look for structured update output from content_updater agent
        automation_output_dir = Path("automation_outputs")
        update_file = automation_output_dir / f"{self.page_name}_updates.json"

        if not update_file.exists():
            # Fall back to looking in research results for JSON
            logger.warning(f"No structured update file found at {update_file}")
            logger.info("Attempting to parse JSON from research results...")

            structured_updates = []
            for result in research_results:
                content = result.get("content", "")
                # Try to extract JSON from markdown code blocks
                json_match = self._extract_json_from_markdown(content)
                if json_match:
                    try:
                        update_data = json.loads(json_match)
                        if "updates" in update_data and update_data.get("page") == self.page_name:
                            structured_updates.extend(update_data["updates"])
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON from research: {e}")

            if not structured_updates:
                logger.warning("No structured updates found in research results")
                return {
                    "success": True,
                    "updates_applied": 0,
                    "message": "No structured updates found - agents may not have produced JSON output yet"
                }
        else:
            # Read structured update file
            try:
                with open(update_file) as f:
                    update_data = json.load(f)
                structured_updates = update_data.get("updates", [])
                logger.info(f"Loaded {len(structured_updates)} structured updates from {update_file}")
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load update file {update_file}: {e}")
                return {
                    "success": False,
                    "error": f"Failed to parse update file: {e}",
                    "updates_applied": 0
                }

        # Apply the structured updates using ContentUpdateApplier
        if structured_updates:
            result = self.content_applier.apply_updates(
                str(content_path),
                structured_updates
            )
            logger.info(f"Applied {result.get('updates_applied', 0)} updates to {content_path}")
            return result
        else:
            return {
                "success": True,
                "updates_applied": 0,
                "message": "No updates to apply"
            }

    def _extract_json_from_markdown(self, content: str) -> str | None:
        """Extract JSON from markdown code blocks"""
        import re

        # Look for JSON code blocks
        json_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        matches: list[Any] = re.findall(json_pattern, content)

        if matches:
            return str(matches[0])

        # Try to find JSON without code blocks
        json_pattern2 = r'(\{[\s\S]*?"updates"[\s\S]*?\})'
        matches2: list[Any] = re.findall(json_pattern2, content)

        if matches2:
            return str(matches2[0])

        return None

    def _validate_content(self) -> dict[str, Any]:
        """Validate page content quality"""
        content_path = Path(f"src/content/{self.page_config.content_file}")

        if not content_path.exists():
            return {"score": 0.0, "errors": ["Content file not found"]}

        content = content_path.read_text()
        result: dict[str, Any] = self.validation_enhancer.validate_content(content)
        return result

    def _build_site(self) -> dict[str, Any]:
        """Build the complete site"""
        result: dict[str, Any] = self.automation_controller.build_site()
        return result


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
