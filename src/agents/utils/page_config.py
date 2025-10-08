"""
Page configuration system for generalized automation
Defines page-specific metadata WITHOUT hardcoded update logic
AI agents handle intelligent updates based on system instructions
"""



class PageConfig:
    """
    Configuration for a specific page's automation behavior
    Contains ONLY metadata and thresholds - NO update logic
    """

    def __init__(
        self,
        page_name: str,
        content_file: str,
        research_agents: list[str],
        research_focus: list[str],
        validation_thresholds: dict[str, float],
        system_instructions_key: str
    ):
        """
        Args:
            page_name: Name of the page (e.g., "action", "technology")
            content_file: Markdown file name (e.g., "action.md")
            research_agents: List of agent names for research
            research_focus: Focus areas for research (e.g., ["employment", "skills"])
            validation_thresholds: Quality thresholds for validation
            system_instructions_key: Key for agent system instructions
        """
        self.page_name = page_name
        self.content_file = content_file
        self.research_agents = research_agents
        self.research_focus = research_focus
        self.validation_thresholds = validation_thresholds
        self.system_instructions_key = system_instructions_key


# Page configurations - metadata only, no update logic
PAGE_CONFIGS = {
    "action": PageConfig(
        page_name="action",
        content_file="action.md",
        research_agents=["social_researcher"],
        research_focus=["employment", "skills", "community", "resilience"],
        validation_thresholds={
            "strategy_feasibility": 0.7,
            "resource_accessibility": 0.6,
            "clarity": 0.6,
            "actionability": 0.7
        },
        system_instructions_key="action_updates"
    ),

    "technology": PageConfig(
        page_name="technology",
        content_file="technology.md",
        research_agents=["technology_researcher"],
        research_focus=["ai_models", "capabilities", "benchmarks", "releases"],
        validation_thresholds={
            "technical_accuracy": 0.8,
            "model_claims": 0.7,
            "benchmark_accuracy": 0.8,
            "release_dates": 0.6
        },
        system_instructions_key="technology_updates"
    ),

    "llm": PageConfig(
        page_name="llm",
        content_file="llm.md",
        research_agents=["technology_researcher"],
        research_focus=["llm_models", "training", "capabilities", "limitations"],
        validation_thresholds={
            "technical_accuracy": 0.8,
            "model_claims": 0.8,
            "benchmark_accuracy": 0.9,
            "release_dates": 0.7
        },
        system_instructions_key="llm_updates"
    ),

    "economy": PageConfig(
        page_name="economy",
        content_file="economy.md",
        research_agents=["market_researcher", "policy_researcher"],
        research_focus=["market_trends", "economic_indicators", "policy_impacts"],
        validation_thresholds={
            "data_accuracy": 0.9,
            "source_reliability": 0.8,
            "recency": 0.7
        },
        system_instructions_key="economy_updates"
    ),

    "society": PageConfig(
        page_name="society",
        content_file="society.md",
        research_agents=["social_researcher", "policy_researcher"],
        research_focus=["social_impact", "equity", "mental_health", "community"],
        validation_thresholds={
            "social_accuracy": 0.7,
            "impact_assessment": 0.7,
            "inclusivity": 0.8
        },
        system_instructions_key="society_updates"
    ),

    "privacy": PageConfig(
        page_name="privacy",
        content_file="privacy.md",
        research_agents=["policy_researcher", "technology_researcher"],
        research_focus=["privacy_tech", "regulations", "data_protection", "surveillance"],
        validation_thresholds={
            "technical_accuracy": 0.8,
            "legal_accuracy": 0.9,
            "practical_guidance": 0.7
        },
        system_instructions_key="privacy_updates"
    )
}


def get_page_config(page_name: str) -> PageConfig:
    """Get configuration for a specific page"""
    if page_name not in PAGE_CONFIGS:
        raise ValueError(f"Unknown page: {page_name}. Available: {list(PAGE_CONFIGS.keys())}")
    return PAGE_CONFIGS[page_name]
