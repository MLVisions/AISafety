"""
Page configuration - single source of truth for all page metadata.

Used by: template_engine (navigation), orchestrator (automation),
content_validation, build verification, and reference management.
"""

from dataclasses import dataclass, field


@dataclass
class SectionAgentConfig:
    """Maps a content section to its research agent and task.

    Each entry pairs a markdown H2 heading with the agent persona
    (from agents.yaml) and the task key (from tasks.yaml) responsible
    for keeping that section current.
    """

    section: str  # H2 heading text (without ##)
    agent: str  # Agent persona key from agents.yaml
    task: str  # Task key from tasks.yaml


@dataclass
class PageConfig:
    """Configuration for a website page."""

    page_name: str
    content_file: str
    title: str
    tagline: str = ""
    description: str = ""

    # Navigation
    nav_order: int = 0  # 0 = not in main nav
    nav_icon: str = ""
    nav_style: str = "nav-button"  # "nav-button" or "cta-button"
    show_in_nav: bool = True

    # Automation – each section has its own (agent, task) pair
    section_agents: list[SectionAgentConfig] = field(default_factory=list)
    has_plots: bool = False
    has_data_fetching: bool = False

    # Validation thresholds
    validation_thresholds: dict[str, float] = field(default_factory=dict)

    @property
    def url(self) -> str:
        return f"{self.page_name}.html"


# ---------------------------------------------------------------------
# All pages - single source of truth
# ---------------------------------------------------------------------

PAGE_CONFIGS: dict[str, PageConfig] = {
    "index": PageConfig(
        page_name="index",
        content_file="index.md",
        title="Home",
        tagline="Preparing for disruption, divergence and resilience",
        description="Navigate the AI tidal shift with comprehensive insights.",
        nav_order=1,
        nav_icon="home_icon.png",
    ),
    "economy": PageConfig(
        page_name="economy",
        content_file="economy.md",
        title="Economy & Policy",
        tagline="From market cycles to legislative actions",
        description="Macroeconomic analysis, geopolitical risks, policy, and financial system evolution.",
        nav_order=2,
        nav_icon="economy_icon.png",
        section_agents=[
            SectionAgentConfig("Macroeconomic Landscape", "market_researcher", "economy_macro_task"),
            SectionAgentConfig("Geopolitical & Market Risks", "geopolitics_researcher", "economy_geopolitics_task"),
            SectionAgentConfig("Policy & Regulation", "policy_researcher", "economy_policy_task"),
            SectionAgentConfig("Financial System Evolution", "digital_assets_researcher", "economy_financial_infra_task"),
            SectionAgentConfig("Strategic Recommendations", "market_researcher", "economy_strategy_task"),
        ],
        has_plots=True,
        has_data_fetching=True,
        validation_thresholds={"data_accuracy": 0.9, "source_reliability": 0.8, "recency": 0.7},
    ),
    "technology": PageConfig(
        page_name="technology",
        content_file="technology.md",
        title="AI & Technology",
        tagline="Capabilities, trends and what comes next",
        description="AI developments, capabilities, and future trends.",
        nav_order=3,
        nav_icon="ai_icon.png",
        section_agents=[
            SectionAgentConfig("AI Capabilities Today", "technology_researcher", "technology_capabilities_task"),
            SectionAgentConfig("Investment & Economic Impact", "technology_researcher", "technology_investment_task"),
            SectionAgentConfig("Agentic AI & Swarm Architecture", "technology_researcher", "technology_agents_task"),
            SectionAgentConfig("Future Trends & Opportunities", "technology_researcher", "technology_trends_task"),
        ],
        validation_thresholds={"technical_accuracy": 0.8, "model_claims": 0.7},
    ),
    "society": PageConfig(
        page_name="society",
        content_file="society.md",
        title="Society & Mental Health",
        tagline="Understanding the human impact of AI transformation",
        description="Social impact analysis including employment and mental health.",
        nav_order=4,
        nav_icon="society_icon.png",
        section_agents=[
            SectionAgentConfig("Mental Health & Labour Disruption", "social_researcher", "society_mental_health_task"),
            SectionAgentConfig("Economic Uncertainty & Resilience", "social_researcher", "society_resilience_task"),
            SectionAgentConfig("AI Misinformation & Reality Distortion", "social_researcher", "society_misinformation_task"),
            SectionAgentConfig("Community & Support", "social_researcher", "society_community_task"),
        ],
        validation_thresholds={"social_accuracy": 0.7, "impact_assessment": 0.7},
    ),
    "privacy": PageConfig(
        page_name="privacy",
        content_file="privacy.md",
        title="Privacy & Security",
        tagline="Protecting yourself in the AI era",
        description="Privacy threats, security practices, and data ethics.",
        nav_order=5,
        nav_icon="privacy_icon.png",
        section_agents=[
            SectionAgentConfig("Threats & Misinformation", "policy_researcher", "privacy_threats_task"),
            SectionAgentConfig("Security Best Practices", "technology_researcher", "privacy_security_task"),
            SectionAgentConfig("Data Privacy & Ethics", "policy_researcher", "privacy_ethics_task"),
        ],
        validation_thresholds={"technical_accuracy": 0.8, "legal_accuracy": 0.9},
    ),
    "llm": PageConfig(
        page_name="llm",
        content_file="llm.md",
        title="How LLMs Work",
        tagline="Understanding the technology behind the transformation",
        description="How large language models and agent architectures work.",
        nav_order=0,
        show_in_nav=False,
        section_agents=[
            SectionAgentConfig("How Large Language Models Work", "technology_researcher", "llm_foundations_task"),
            SectionAgentConfig("AI Agent Architectures: From Monolithic to Distributed Systems", "technology_researcher", "llm_agents_task"),
        ],
        validation_thresholds={"technical_accuracy": 0.8, "model_claims": 0.8},
    ),
    "action": PageConfig(
        page_name="action",
        content_file="action.md",
        title="What We Can Do Now",
        tagline="Practical steps for preparation and resilience",
        description="Actionable steps to prepare for AI-driven changes.",
        nav_order=100,
        nav_icon="action_icon.png",
        nav_style="cta-button",
        section_agents=[
            SectionAgentConfig("Take Practical Steps", "social_researcher", "action_steps_task"),
        ],
        validation_thresholds={"strategy_feasibility": 0.7, "clarity": 0.6},
    ),
    "references": PageConfig(
        page_name="references",
        content_file="references.md",
        title="References & Sources",
        tagline="Research citations and data sources",
        description="Sources supporting our analysis and recommendations.",
        nav_order=0,
        show_in_nav=False,
    ),
}


def get_page_config(page_name: str) -> PageConfig:
    """Get configuration for a specific page."""
    if page_name not in PAGE_CONFIGS:
        raise ValueError(f"Unknown page: {page_name}. Available: {list(PAGE_CONFIGS.keys())}")
    return PAGE_CONFIGS[page_name]


def get_content_pages() -> list[str]:
    """Get names of pages that have automatable content (excludes index, references)."""
    return [
        name for name, cfg in PAGE_CONFIGS.items()
        if cfg.section_agents and name not in ("index", "references")
    ]


def get_nav_pages() -> list[dict[str, str]]:
    """Get ordered list of pages for the main navigation bar."""
    nav_items = []
    for cfg in sorted(PAGE_CONFIGS.values(), key=lambda c: c.nav_order):
        if cfg.show_in_nav and cfg.nav_style == "nav-button" and cfg.nav_order > 0:
            nav_items.append({
                "name": cfg.page_name,
                "url": cfg.url,
                "title": cfg.title,
                "icon": cfg.nav_icon,
            })
    return nav_items


def get_cta_page() -> dict[str, str] | None:
    """Get the call-to-action page config (for the separate CTA button)."""
    for cfg in PAGE_CONFIGS.values():
        if cfg.nav_style == "cta-button" and cfg.show_in_nav:
            return {
                "name": cfg.page_name,
                "url": cfg.url,
                "title": cfg.title,
                "icon": cfg.nav_icon,
            }
    return None
