"""
Research Network Crew - Complex Agent System for Comprehensive Research
Uses multiple specialized research agents to gather information across domains
"""

from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, SerperDevTool, WebsiteSearchTool

from ...utils import get_openai_api_key, safe_write_file


class ResearchNetworkCrew:
    """Research Network crew for comprehensive domain research"""

    def __init__(self, **kwargs: Any) -> None:
        # Load configuration files
        config_dir = Path(__file__).parent / "config"

        with open(config_dir / "agents.yaml") as f:
            self.agents_config = yaml.safe_load(f)

        with open(config_dir / "tasks.yaml") as f:
            self.tasks_config = yaml.safe_load(f)

        # Ensure OpenAI API key is available
        try:
            get_openai_api_key()
        except ValueError as e:
            print(f"Warning: {e}")

    def create_agents(self) -> dict[str, Agent]:
        """Create all research agents"""
        agents = {}

        # Market researcher
        config = self.agents_config['market_researcher']
        agents['market_researcher'] = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[SerperDevTool(), WebsiteSearchTool(), FileReadTool()],
            verbose=True,
            max_iter=15,
            respect_context_window=True
        )

        # Technology researcher
        config = self.agents_config['technology_researcher']
        agents['technology_researcher'] = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[SerperDevTool(), WebsiteSearchTool(), FileReadTool()],
            verbose=True,
            max_iter=15,
            respect_context_window=True
        )

        # Policy researcher
        config = self.agents_config['policy_researcher']
        agents['policy_researcher'] = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[SerperDevTool(), WebsiteSearchTool(), FileReadTool()],
            verbose=True,
            max_iter=15,
            respect_context_window=True
        )

        # Social researcher
        config = self.agents_config['social_researcher']
        agents['social_researcher'] = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[SerperDevTool(), WebsiteSearchTool(), FileReadTool()],
            verbose=True,
            max_iter=15,
            respect_context_window=True
        )

        return agents

    def create_tasks(self, agents: dict[str, Agent]) -> list[Task]:
        """Create all research tasks"""
        tasks = []

        # Market research task
        config = self.tasks_config['market_research_task']
        market_task = Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=agents['market_researcher']
        )
        tasks.append(market_task)

        # Technology research task
        config = self.tasks_config['technology_research_task']
        tech_task = Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=agents['technology_researcher']
        )
        tasks.append(tech_task)

        # Policy research task
        config = self.tasks_config['policy_research_task']
        policy_task = Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=agents['policy_researcher']
        )
        tasks.append(policy_task)

        # Social research task
        config = self.tasks_config['social_research_task']
        social_task = Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=agents['social_researcher']
        )
        tasks.append(social_task)

        # Synthesis task
        config = self.tasks_config['synthesis_task']
        synthesis_task = Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=agents['market_researcher'],  # Use market researcher for synthesis
            context=[market_task, tech_task, policy_task, social_task]
        )
        tasks.append(synthesis_task)

        return tasks

    def create_crew(self) -> Crew:
        """Create the research crew"""
        agents = self.create_agents()
        tasks = self.create_tasks(agents)

        return Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )


def create_research_network_crew(**kwargs: Any) -> ResearchNetworkCrew:
    """Factory function to create a ResearchNetworkCrew"""
    return ResearchNetworkCrew(**kwargs)


def run_research_network_test(
    output_dir: str = "research_output",
    focus_areas: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Run the research network crew and save outputs

    Args:
        output_dir: Directory to save research outputs
        focus_areas: Optional dictionary to focus research on specific areas

    Returns:
        Dictionary with research results and metadata
    """
    print("🔬 Starting Research Network Crew...")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize crew
    research_crew = create_research_network_crew()

    # Prepare inputs
    inputs = focus_areas or {
        "research_timeframe": "last 6 months",
        "priority_areas": [
            "AI market developments",
            "policy and regulatory changes",
            "technology breakthroughs",
            "societal impact studies"
        ]
    }

    try:
        # Run the crew
        crew = research_crew.create_crew()
        result = crew.kickoff(inputs=inputs)

        # Save main result
        result_file = output_path / "research_synthesis.md"
        safe_write_file(str(result_file), result.raw)

        # Save individual task outputs if available
        tasks_output = {}
        if hasattr(result, 'tasks_output'):
            for i, task_output in enumerate(result.tasks_output):
                task_name = [
                    "market_research",
                    "technology_research",
                    "policy_research",
                    "social_research",
                    "synthesis"
                ][i] if i < 5 else f"task_{i}"

                task_file = output_path / f"{task_name}_report.md"
                safe_write_file(str(task_file), task_output.raw)
                tasks_output[task_name] = task_output.raw

        print(f"✅ Research Network completed. Results saved to {output_path}")

        return {
            "success": True,
            "main_result": result.raw,
            "individual_reports": tasks_output,
            "output_directory": str(output_path),
            "metadata": {
                "inputs": inputs,
                "execution_time": "calculated_externally"  # Would need timing logic
            }
        }

    except Exception as e:
        error_msg = f"Research Network failed: {str(e)}"
        print(f"❌ {error_msg}")

        # Save error report
        error_file = output_path / "research_error.txt"
        safe_write_file(str(error_file), f"Research Network Error: {error_msg}")

        return {
            "success": False,
            "error": error_msg,
            "output_directory": str(output_path)
        }


def run_research_network(
    output_dir: str = "research_output",
    focus_areas: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Run the research network crew and save outputs

    Args:
        output_dir: Directory to save research outputs
        focus_areas: Optional dictionary to focus research on specific areas

    Returns:
        Dictionary with research results and metadata
    """
    print("🔬 Starting Research Network Crew...")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize crew
    research_crew = create_research_network_crew()

    # Prepare inputs
    inputs = focus_areas or {
        "research_timeframe": "last 6 months",
        "priority_areas": [
            "AI market developments",
            "policy and regulatory changes",
            "technology breakthroughs",
            "societal impact studies"
        ]
    }

    try:
        # Run the crew
        crew = research_crew.create_crew()
        result = crew.kickoff(inputs=inputs)

        # Save main result
        result_file = output_path / "research_synthesis.md"
        safe_write_file(str(result_file), result.raw)

        # Save individual task outputs if available
        tasks_output = {}
        if hasattr(result, 'tasks_output'):
            for i, task_output in enumerate(result.tasks_output):
                task_name = [
                    "market_research",
                    "technology_research",
                    "policy_research",
                    "social_research",
                    "synthesis"
                ][i] if i < 5 else f"task_{i}"

                task_file = output_path / f"{task_name}_report.md"
                safe_write_file(str(task_file), task_output.raw)
                tasks_output[task_name] = task_output.raw

        print(f"✅ Research Network completed. Results saved to {output_path}")

        return {
            "success": True,
            "main_result": result.raw,
            "individual_reports": tasks_output,
            "output_directory": str(output_path),
            "metadata": {
                "inputs": inputs,
                "execution_time": "calculated_externally"  # Would need timing logic
            }
        }

    except Exception as e:
        error_msg = f"Research Network failed: {str(e)}"
        print(f"❌ {error_msg}")

        # Save error report
        error_file = output_path / "research_error.txt"
        safe_write_file(str(error_file), f"Research Network Error: {error_msg}")

        return {
            "success": False,
            "error": error_msg,
            "output_directory": str(output_path)
        }


if __name__ == "__main__":
    # Test the research network
    result = run_research_network(
        output_dir="test_research_output",
        focus_areas={
            "research_timeframe": "last 3 months",
            "priority_areas": [
                "AI investment trends",
                "Privacy regulation updates"
            ]
        }
    )

    if result["success"]:
        print("Research completed successfully!")
        print(f"Main result preview: {result['main_result'][:200]}...")
    else:
        print(f"Research failed: {result['error']}")


if __name__ == "__main__":
    # Test the research network
    result = run_research_network(
        output_dir="test_research_output",
        focus_areas={
            "research_timeframe": "last 3 months",
            "priority_areas": [
                "AI investment trends",
                "Privacy regulation updates"
            ]
        }
    )

    if result["success"]:
        print("Research completed successfully!")
        print(f"Main result preview: {result['main_result'][:200]}...")
    else:
        print(f"Research failed: {result['error']}")
