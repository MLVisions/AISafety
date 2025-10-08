#!/usr/bin/env python3
"""
Automation Controller
Central orchestrator for automated website updates and maintenance
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .agent_network import AISafetyAgentNetwork
from .investment_pipeline import run_complete_investment_pipeline
from .reference_sync import ReferenceSynchronizer
from .utils import (
    BuildOrchestratorUtils,
    ContentValidationUtils,
    MarketDataUtils,
)
from .utils.infrastructure_bridges import PageAutomationBridge


class AutomationController:
    """Central controller for all automated website maintenance tasks"""

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.setup_logging()

        # Initialize agent systems
        self.agent_network = AISafetyAgentNetwork(self.project_root)
        self.market_data_utils = MarketDataUtils()
        self.content_validator = ContentValidationUtils()
        self.build_orchestrator = BuildOrchestratorUtils(str(self.project_root))
        self.reference_sync = ReferenceSynchronizer(self.project_root / "src" / "content")

        # Initialize page-specific automation bridges
        self.action_bridge = PageAutomationBridge("action", self)
        self.technology_bridge = PageAutomationBridge("technology", self)
        self.society_bridge = PageAutomationBridge("society", self)
        self.privacy_bridge = PageAutomationBridge("privacy", self)

    def setup_logging(self) -> None:
        """Setup logging for automation runs"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)

    def run_full_automation_cycle(
        self,
        update_market_data: bool = True,
        run_content_research: bool = True,
        validate_content: bool = True,
        sync_references: bool = True,
        rebuild_website: bool = True
    ) -> dict[str, Any]:
        """
        Run complete automation cycle

        Args:
            update_market_data: Whether to fetch latest market data
            run_content_research: Whether to run content research and updates
            validate_content: Whether to validate content quality
            sync_references: Whether to synchronize references
            rebuild_website: Whether to rebuild the website

        Returns:
            Dictionary with automation results
        """
        cycle_start = datetime.now()
        self.logger.info("Starting full automation cycle")

        results: dict[str, Any] = {
            'cycle_start': cycle_start.isoformat(),
            'stages': {},
            'success': False,
            'errors': []
        }

        try:
            # Stage 1: Market Data Update
            if update_market_data:
                self.logger.info("Stage 1: Updating market data and investment analysis")
                market_results = self._update_market_data()
                results['stages']['market_data'] = market_results

            # Stage 2: Content Research & Updates
            if run_content_research:
                self.logger.info("Stage 2: Running content research and updates")
                content_results = self._run_content_updates()
                results['stages']['content_updates'] = content_results

            # Stage 3: Content Validation
            if validate_content:
                self.logger.info("Stage 3: Validating content quality")
                validation_results = self._validate_content()
                results['stages']['content_validation'] = validation_results

            # Stage 4: Reference Synchronization
            if sync_references:
                self.logger.info("Stage 4: Synchronizing references")
                ref_results = self._sync_references()
                results['stages']['reference_sync'] = ref_results

            # Stage 5: Website Rebuild
            if rebuild_website:
                self.logger.info("Stage 5: Rebuilding website")
                build_results = self._rebuild_website()
                results['stages']['website_build'] = build_results

            results['success'] = True
            results['cycle_end'] = datetime.now().isoformat()
            results['total_duration'] = str(datetime.now() - cycle_start)

            self.logger.info(f"Automation cycle completed successfully in {results['total_duration']}")

        except Exception as e:
            error_msg = f"Automation cycle failed: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            results['cycle_end'] = datetime.now().isoformat()

        return results

    def _update_market_data(self) -> dict[str, Any]:
        """Update market data and run investment pipeline"""
        try:
            # Run the complete investment pipeline
            pipeline_results = run_complete_investment_pipeline(
                output_dir="src/data",
                generate_visualizations=True,
                update_plots=True,
                time_horizons=[3, 5, 10]
            )

            return {
                'status': 'completed',
                'pipeline_results': pipeline_results
            }

        except Exception as e:
            self.logger.error(f"Market data update failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _run_content_updates(self) -> dict[str, Any]:
        """Run content research and updates using agent network"""
        try:
            # Run the agent network workflow
            workflow_results = self.agent_network.run_full_update_workflow("automation_outputs")

            return {
                'status': 'completed',
                'workflow_results': workflow_results
            }

        except Exception as e:
            self.logger.error(f"Content updates failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _validate_content(self) -> dict[str, Any]:
        """Validate content quality"""
        try:
            # Run content validation directly
            validation_result = self.content_validator.validate_content_direct()

            return {
                'status': 'completed',
                'validation_result': validation_result
            }

        except Exception as e:
            self.logger.error(f"Content validation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _sync_references(self) -> dict[str, Any]:
        """Synchronize references across content files"""
        try:
            sync_results = self.reference_sync.sync_references_file()

            return {
                'status': 'completed',
                'sync_results': sync_results
            }

        except Exception as e:
            self.logger.error(f"Reference synchronization failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _rebuild_website(self) -> dict[str, Any]:
        """Rebuild the website"""
        try:
            # Build website directly
            build_result = self.build_orchestrator.build_website_direct(
                regenerate_plots=False,  # Already done in market data stage
                validate_content=False,  # Already validated
                clean_output=False
            )

            return {
                'status': 'completed',
                'build_result': build_result
            }

        except Exception as e:
            self.logger.error(f"Website rebuild failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def run_market_data_only(self) -> dict[str, Any]:
        """Run only market data updates (for frequent updates)"""
        self.logger.info("Running market data update only")
        return self._update_market_data()

    def run_content_research_only(self) -> dict[str, Any]:
        """Run only content research and updates"""
        self.logger.info("Running content research only")
        return self._run_content_updates()

    def run_action_automation(self) -> dict[str, Any]:
        """Run complete action.md automation workflow"""
        self.logger.info("Running action.md automation workflow")
        try:
            results = self.action_bridge.execute_automation()

            if results['success']:
                self.logger.info("Action automation completed successfully")
                self.logger.info(f"Summary: {results.get('summary', {})}")
            else:
                self.logger.error("Action automation failed")
                for error in results.get('errors', []):
                    self.logger.error(f"  - {error}")

            return results

        except Exception as e:
            self.logger.error(f"Action automation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def run_technology_automation(self) -> dict[str, Any]:
        """Run complete technology.md automation workflow"""
        self.logger.info("Running technology.md automation workflow")
        try:
            results = self.technology_bridge.execute_automation()

            if results['success']:
                self.logger.info("Technology automation completed successfully")
                self.logger.info(f"Summary: {results.get('summary', {})}")
            else:
                self.logger.error("Technology automation failed")
                for error in results.get('errors', []):
                    self.logger.error(f"  - {error}")

            return results

        except Exception as e:
            self.logger.error(f"Technology automation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def run_society_automation(self) -> dict[str, Any]:
        """Run complete society.md automation workflow"""
        self.logger.info("Running society.md automation workflow")
        try:
            results = self.society_bridge.execute_automation()

            if results['success']:
                self.logger.info("Society automation completed successfully")
                self.logger.info(f"Summary: {results.get('summary', {})}")
            else:
                self.logger.error("Society automation failed")
                for error in results.get('errors', []):
                    self.logger.error(f"  - {error}")

            return results

        except Exception as e:
            self.logger.error(f"Society automation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def run_privacy_automation(self) -> dict[str, Any]:
        """Run complete privacy.md automation workflow"""
        self.logger.info("Running privacy.md automation workflow")
        try:
            results = self.privacy_bridge.execute_automation()

            if results['success']:
                self.logger.info("Privacy automation completed successfully")
                self.logger.info(f"Summary: {results.get('summary', {})}")
            else:
                self.logger.error("Privacy automation failed")
                for error in results.get('errors', []):
                    self.logger.error(f"  - {error}")

            return results

        except Exception as e:
            self.logger.error(f"Privacy automation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def build_site(self) -> dict[str, Any]:
        """
        Public method to build the website
        """
        return self._rebuild_website()


def main() -> None:
    """Main entry point for automation controller"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Safety Website Automation Controller")
    parser.add_argument("--mode", 
                       choices=["full", "market-data", "content", "action", "technology", "society", "privacy"], 
                       default="full",
                       help="Automation mode to run")
    parser.add_argument("--no-market-data", action="store_true",
                       help="Skip market data updates")
    parser.add_argument("--no-content", action="store_true",
                       help="Skip content research")
    parser.add_argument("--no-validation", action="store_true",
                       help="Skip content validation")
    parser.add_argument("--no-references", action="store_true",
                       help="Skip reference synchronization")
    parser.add_argument("--no-rebuild", action="store_true",
                       help="Skip website rebuild")

    args = parser.parse_args()

    controller = AutomationController()

    if args.mode == "market-data":
        results = controller.run_market_data_only()
    elif args.mode == "content":
        results = controller.run_content_research_only()
    elif args.mode == "action":
        results = controller.run_action_automation()
    elif args.mode == "technology":
        results = controller.run_technology_automation()
    elif args.mode == "society":
        results = controller.run_society_automation()
    elif args.mode == "privacy":
        results = controller.run_privacy_automation()
    else:
        # Full automation cycle
        results = controller.run_full_automation_cycle(
            update_market_data=not args.no_market_data,
            run_content_research=not args.no_content,
            validate_content=not args.no_validation,
            sync_references=not args.no_references,
            rebuild_website=not args.no_rebuild
        )

    if results['success']:
        print("✅ Automation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Automation failed:")
        for error in results.get('errors', []):
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
