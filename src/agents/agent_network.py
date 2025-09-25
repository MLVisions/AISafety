"""
AI Safety Website Agent Network
Unified CrewAI implementation for website maintenance and content updates
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, Task
from crewai_tools import FileReadTool, SerperDevTool, WebsiteSearchTool

from .utils import get_openai_api_key, safe_write_file


class AISafetyAgentNetwork:
    """Unified agent network for AI Safety website maintenance"""

    def __init__(self, project_root: str | Path = "."):
        self.project_root = Path(project_root)
        self.agents_dir = self.project_root / "src" / "agents"
        self.content_dir = self.project_root / "src" / "content"
        self.data_dir = self.project_root / "src" / "data"

        # Load configurations
        self.agents_config = self._load_yaml_config("agents.yaml")
        self.tasks_config = self._load_yaml_config("tasks.yaml")

        # Initialize tools
        self.tools = {
            'serper': SerperDevTool(),
            'website': WebsiteSearchTool(),
            'file_reader': FileReadTool()
        }

        # Ensure OpenAI API key is available
        get_openai_api_key()

    def _load_yaml_config(self, filename: str) -> dict[str, Any]:
        """Load YAML configuration file"""
        config_path = self.agents_dir / filename
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config if isinstance(config, dict) else {}

    def create_research_crew(self) -> Crew:
        """Create crew for research tasks"""
        # Research agents
        agents = {
            'market_researcher': self._create_agent('market_researcher'),
            'technology_researcher': self._create_agent('technology_researcher'),
            'policy_researcher': self._create_agent('policy_researcher'),
            'social_researcher': self._create_agent('social_researcher')
        }

        # Research tasks
        tasks = [
            self._create_task('market_research_task', agents['market_researcher']),
            self._create_task('technology_research_task', agents['technology_researcher']),
            self._create_task('policy_research_task', agents['policy_researcher']),
            self._create_task('social_research_task', agents['social_researcher'])
        ]

        return Crew(
            agents=list(agents.values()),
            tasks=tasks,
            verbose=True
        )

    def create_content_crew(self, research_results: str) -> Crew:
        """Create crew for content maintenance tasks"""
        # Content agents
        agents = {
            'content_validator': self._create_agent('content_validator'),
            'content_updater': self._create_agent('content_updater'),
            'reference_manager': self._create_agent('reference_manager')
        }

        # Content tasks
        validation_task = self._create_task('content_validation_task', agents['content_validator'])

        update_task = self._create_task('content_update_task', agents['content_updater'])
        update_task.context = [validation_task]
        update_task.description += f"\n\nResearch findings to incorporate:\n{research_results}"

        reference_task = self._create_task('reference_sync_task', agents['reference_manager'])
        reference_task.context = [update_task]

        return Crew(
            agents=list(agents.values()),
            tasks=[validation_task, update_task, reference_task],
            verbose=True
        )

    def create_infrastructure_crew(self) -> Crew:
        """Create crew for infrastructure tasks"""
        # Infrastructure agents
        agents = {
            'market_data_fetcher': self._create_agent('market_data_fetcher'),
            'build_orchestrator': self._create_agent('build_orchestrator')
        }

        # Infrastructure tasks
        data_task = self._create_task('market_data_update_task', agents['market_data_fetcher'])
        build_task = self._create_task('website_build_task', agents['build_orchestrator'])
        build_task.context = [data_task]

        return Crew(
            agents=list(agents.values()),
            tasks=[data_task, build_task],
            verbose=True
        )

    def _create_agent(self, agent_name: str) -> Agent:
        """Create an agent from configuration"""
        config = self.agents_config[agent_name]

        # Determine which tools this agent needs
        agent_tools = []
        if 'SerperDevTool' in config.get('tools', []):
            agent_tools.append(self.tools['serper'])
        if 'WebsiteSearchTool' in config.get('tools', []):
            agent_tools.append(self.tools['website'])
        if 'FileReadTool' in config.get('tools', []):
            agent_tools.append(self.tools['file_reader'])

        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=agent_tools,
            verbose=True,
            allow_delegation=False
        )

    def _create_task(self, task_name: str, agent: Agent) -> Task:
        """Create a task from configuration"""
        config = self.tasks_config[task_name]

        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=agent
        )

    def run_full_update_workflow(self, output_dir: str = "agent_outputs") -> dict[str, Any]:
        """
        Run the complete website update workflow

        Returns:
            Workflow execution report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        workflow_start = datetime.now()
        print("🚀 Starting AI Safety Website Update Workflow")
        print("=" * 60)

        workflow_report: dict[str, Any] = {
            "workflow_start": workflow_start.isoformat(),
            "stages": {},
            "success": False,
            "errors": []
        }

        try:
            # Stage 1: Research
            print("\n📊 Stage 1: Research")
            print("-" * 30)
            research_crew = self.create_research_crew()
            research_result = research_crew.kickoff()

            research_output = output_path / "research_results.md"
            safe_write_file(str(research_output), research_result.raw)

            workflow_report["stages"]["research"] = {
                "status": "completed",
                "output_file": str(research_output),
                "summary": research_result.raw[:200] + "..."
            }

            # Stage 2: Content Updates
            print("\n📝 Stage 2: Content Updates")
            print("-" * 30)
            content_crew = self.create_content_crew(research_result.raw)
            content_result = content_crew.kickoff()

            content_output = output_path / "content_updates.md"
            safe_write_file(str(content_output), content_result.raw)

            workflow_report["stages"]["content"] = {
                "status": "completed",
                "output_file": str(content_output),
                "summary": content_result.raw[:200] + "..."
            }

            # Stage 3: Infrastructure
            print("\n🔧 Stage 3: Infrastructure")
            print("-" * 30)
            infrastructure_crew = self.create_infrastructure_crew()
            infrastructure_result = infrastructure_crew.kickoff()

            infrastructure_output = output_path / "infrastructure_results.md"
            safe_write_file(str(infrastructure_output), infrastructure_result.raw)

            workflow_report["stages"]["infrastructure"] = {
                "status": "completed",
                "output_file": str(infrastructure_output),
                "summary": infrastructure_result.raw[:200] + "..."
            }

            workflow_report["success"] = True
            workflow_report["workflow_end"] = datetime.now().isoformat()
            workflow_report["total_duration"] = str(datetime.now() - workflow_start)

            print("\n✅ Workflow completed successfully!")
            print(f"Total duration: {workflow_report['total_duration']}")
            print(f"Outputs saved to: {output_path}")

        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            workflow_report["errors"].append(error_msg)
            workflow_report["workflow_end"] = datetime.now().isoformat()

            print(f"\n❌ {error_msg}")

            # Save error report
            error_output = output_path / "workflow_error.txt"
            safe_write_file(str(error_output), f"Workflow Error: {error_msg}")

        # Save workflow report
        report_output = output_path / "workflow_report.json"
        import json
        with open(report_output, 'w') as f:
            json.dump(workflow_report, f, indent=2)

        return workflow_report


def create_agent_network(**kwargs: Any) -> AISafetyAgentNetwork:
    """Factory function to create the agent network"""
    return AISafetyAgentNetwork(**kwargs)


def run_website_update(output_dir: str = "agent_outputs") -> dict[str, Any]:
    """Convenience function to run the full website update workflow"""
    network = create_agent_network()
    return network.run_full_update_workflow(output_dir)


if __name__ == "__main__":
    # Test the agent network
    result = run_website_update("test_agent_outputs")

    if result["success"]:
        print("✅ Website update completed successfully!")
    else:
        print("❌ Website update failed:")
        for error in result["errors"]:
            print(f"  - {error}")
