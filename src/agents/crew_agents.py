"""
crew_agents.py

This module defines a set of CrewAI agents and tasks that collectively
implement the self‑updating workflow for the Swarm website.  The
implementation here serves as a template: you can expand the tools
available to each agent, adjust prompts, and integrate your own
knowledge base.  See the CrewAI documentation for detailed examples of
defining agents, tasks and crews.

Agents defined:
  * SummarizerAgent – extracts and summarises new content from uploaded files.
  * ResearcherAgent – verifies facts and fetches additional context from the web.
  * EvaluatorAgent – compares verified facts with existing site content to decide
     whether updates are warranted.
  * DeveloperAgent – drafts new or updated content sections in Markdown.
  * ValidatorAgent – checks for bias, ensures citations and maintains the site’s focus.
  * DeployerAgent – applies approved changes in a development branch and
     triggers the deployment process.

A helper function build_crew() constructs a Crew object with a default
process flow.  You can adjust the order of tasks or add additional
conditional logic as needed.
"""

from __future__ import annotations

# Import CrewAI classes.  If you haven't installed crewai yet, run
# `pip install crewai` in your environment.  These imports are kept
# inside a try/except so that the module can be imported without
# errors during local development.  Replace them with actual imports
# when deploying.
try:
     from crewai import Agent, Crew, Task
except ImportError:
     # Define dummy classes for type checking and to prevent runtime errors
     class Agent:  # type: ignore
         def __init__(self, *args, **kwargs):
             pass

     class Task:  # type: ignore
         def __init__(self, *args, **kwargs):
             pass

     class Crew:  # type: ignore
         def __init__(self, *args, **kwargs):
             pass


def build_agents() -> list[Agent]:
     """Create and return the list of agents used in the crew.

     Each agent is defined with a name, a role, a goal and (optionally)
     associated tools and memory.  Tools can include web search,
     document loaders or code execution depending on your setup.  See
     CrewAI examples for details on tool integration.
     """
     # Summarizer agent: ingests uploaded documents and produces concise summaries.
     summarizer = Agent(
         name="SummarizerAgent",
         role="A diligent summariser that extracts key points from uploaded files",
         goal=(
             "Read uploaded documents, presentations or URLs and create "
            "concise summaries with citations.  Whenever possible, identify the "
            "original source (e.g., news article, report, blog) associated with a fact "
            "and include the full URL.  Citations should be rendered as clickable "
            "links in the Markdown output.  Store both raw text and summaries in the "
            "knowledge base."
         ),
         backstory=(
             "You have access to a document loader and vector store.  Your task "
             "is to parse supported file formats (PDF, DOCX, PPTX) and generate "
             "clear, structured summaries.  Each summary should note important "
             "facts such as market movements, legislative changes and AI trends."
         ),
         allow_delegation=False,
     )

     # Researcher agent: verifies facts and enriches context using web search.
     researcher = Agent(
         name="ResearcherAgent",
         role="A fact‑checker and context gatherer",
        goal=(
            "Search the web for authoritative sources to corroborate or update "
            "the information in the summaries.  Retrieve recent articles, "
            "official documents and data related to market trends, crypto "
            "adoption, policy changes, AI investment and societal impacts.  "
            "For each fact, provide at least one credible URL to support it.  "
            "Your notes should include clickable hyperlinks (Markdown style) so "
            "the developer can embed them directly into the website."
        ),
         backstory=(
             "You are an experienced researcher who knows how to construct "
             "effective queries.  When verifying facts, prioritise primary "
             "sources such as government websites, credible news outlets, "
             "and academic publications.  Avoid speculation and clearly "
             "identify unverified claims."
         ),
         allow_delegation=False,
     )

     # Evaluator agent: decides whether new information warrants a site update.
     evaluator = Agent(
         name="EvaluatorAgent",
         role="A critical evaluator comparing new knowledge to existing content",
         goal=(
             "Assess the significance of verified information relative to the "
             "current website content.  For each category (market & macro, policy & "
             "crypto, technology, society, threats), decide if the new information "
             "is novel or contradicts existing material.  Only recommend "
             "updates when the content substantially improves accuracy or adds "
             "valuable context."
         ),
         backstory=(
             "You are conservative in your recommendations, preferring to avoid "
             "unnecessary churn.  Use semantic similarity (e.g., cosine distance "
             "over embeddings) and threshold logic to determine novelty."
         ),
         allow_delegation=False,
     )

     # Developer agent: drafts site updates in markdown.
     developer = Agent(
         name="DeveloperAgent",
         role="A content developer generating markdown for the website",
        goal=(
            "For each section flagged by the evaluator, produce new or revised "
            "Markdown content.  Maintain the site’s narrative style and include "
            "citations as clickable links to the sources provided by the researcher. "
            "Use Markdown footnotes or inline hyperlinks to ensure readers can "
            "navigate to the original sources.  Save the output in a staging "
            "directory (e.g., `website/content_updates/`)."
        ),
         backstory=(
             "You have experience writing accessible economic analysis and "
             "technical explanations.  Follow the existing tone and structure "
             "of the site.  Use markdown syntax for headings, lists and links."
         ),
         allow_delegation=False,
     )

     # Validator agent: checks updated content for bias and alignment with goals.
     validator = Agent(
         name="ValidatorAgent",
         role="A careful editor ensuring updates align with the site’s mission",
         goal=(
             "Review the proposed content updates for factual accuracy, proper "
             "citation and consistency with the original vision (protecting "
             "against misinformation and undue bias).  If content diverges "
             "from the site’s goals or appears one‑sided, modify or reject it."
         ),
         backstory=(
             "You serve as the final checkpoint before deployment.  Cross‑reference "
             "the original documents (Economic Trends & Analysis and the AI Prep "
             "slides) to ensure the core narrative remains intact.  Pay special "
             "attention to tone and bias."
         ),
         allow_delegation=False,
     )

     # Deployer agent: merges validated updates and triggers deployment.
     deployer = Agent(
         name="DeployerAgent",
         role="An operator that applies approved changes and redeploys the site",
         goal=(
             "Apply the validated markdown updates to the website repository, run "
             "the static site generator (e.g., Next.js build), and deploy the new "
             "version.  Generate a summary of the changes and notify the site owner."
         ),
         backstory=(
             "You manage the technical side of deployment.  Use version control "
             "(e.g., Git) to commit changes and open a pull request if needed.  "
             "Ensure the build passes before pushing to production."
         ),
         allow_delegation=False,
     )

     # DataFetcher agent: retrieves historical price data for a list of tickers.
     data_fetcher = Agent(
         name="DataFetcherAgent",
         role="A data retriever for market prices",
         goal=(
             "Given a list of stock or crypto tickers and a date range, fetch historical "
            "price data (time, price) for each asset.  Prefer daily or monthly close prices. "
            "Use a reliable API such as Yahoo Finance or Alpha Vantage via a Python library "
            "like yfinance.  Output should be a structured table or DataFrame that downstream "
            "agents can consume."
        ),
        backstory=(
            "You have access to Python and the internet to call data APIs.  Ensure API keys "
            "are managed securely (e.g., via environment variables).  Validate ticker symbols "
            "and handle missing data gracefully.  Your output will be passed to the forecasting agent."
        ),
        allow_delegation=False,
     )

     # Forecast agent: generates future projections using price data and macro context.
     forecast = Agent(
         name="ForecastAgent",
         role="A forecaster that projects prices and uncertainty bands",
         goal=(
             "Given historical price data and contextual information (inflation, policy, AI investment, etc.), "
            "predict price trajectories for the next five years.  Use statistical models (e.g., ARIMA, "
            "exponential smoothing or regression) and incorporate macro indicators as features.  "
            "Generate a plot with confidence ribbons to illustrate uncertainty and save it for inclusion "
            "on the website."
        ),
        backstory=(
            "You are a data scientist experienced in time‑series forecasting.  When making predictions, "
            "consider macroeconomic assumptions such as inflation rates, investment trends and policy changes "
            "provided by the research agent.  Communicate uncertainty clearly through confidence intervals."
        ),
        allow_delegation=False,
     )

     return [
         summarizer,
         researcher,
         evaluator,
         developer,
         validator,
         deployer,
         data_fetcher,
         forecast,
     ]


def build_tasks(agents: list[Agent]) -> list[Task]:
     """Define tasks and link them to the respective agents.

     The tasks describe what each agent should accomplish in the context
     of the crew.  Dependencies ensure the order of execution.
     """
     # Unpack agents for clarity.  Note: additional agents may be appended at the end of the list.
     summarizer = agents[0]
     researcher = agents[1]
     evaluator = agents[2]
     developer = agents[3]
     validator = agents[4]
     deployer = agents[5]
     data_fetcher = agents[6] if len(agents) > 6 else None
     forecast_agent = agents[7] if len(agents) > 7 else None

     # Task 1: summarise uploaded documents
     summarise_task = Task(
         description=(
             "Summarise all newly uploaded files, produce concise bullet points "
             "and cite the original sources.  Save raw text and summaries in the "
             "knowledge base."
         ),
         agent=summarizer,
         expected_output="A list of summaries with citations and pointers to stored embeddings."
     )

     # Task 2: research and verify the content
     research_task = Task(
         description=(
             "Verify the information in the summaries using credible external sources. "
             "Gather any new context or updates relevant to the categories on the site."
         ),
         agent=researcher,
         expected_output="A report with verified facts, additional context and source links.",
         context=[summarise_task]
     )

     # Task 3: evaluate whether updates are needed
     evaluate_task = Task(
         description=(
             "Compare the verified information with the existing website content. "
             "For each category, decide whether an update is necessary and list the "
             "sections to be updated."
         ),
         agent=evaluator,
         expected_output="A decision matrix indicating which sections should be updated.",
         context=[research_task]
     )

     # Task 4: develop the new content
     develop_task = Task(
         description=(
             "Draft the updated content in Markdown for the sections flagged by "
             "the evaluator.  Follow the site’s narrative style, include headings, "
             "citations and any charts or tables described.  Save files in the staging directory."
         ),
         agent=developer,
         expected_output="A set of Markdown files containing the updated content.",
         context=[evaluate_task]
     )

     # Task 5: validate the updates
     validate_task = Task(
         description=(
             "Review the drafted updates to ensure they are unbiased, factually correct "
             "and aligned with the site’s mission.  Edit or reject content if necessary."
         ),
         agent=validator,
         expected_output="Validated Markdown files ready for deployment.",
         context=[develop_task]
     )

     # Task 6: deploy the updates
     deploy_task = Task(
         description=(
             "Merge the validated updates into the main branch, run the build and deploy "
             "process, and generate a summary of changes."
         ),
         agent=deployer,
         expected_output="Deployment logs and a summary report.",
         context=[validate_task]
     )

     # Task: fetch market price data (if the data_fetcher agent exists)
     if data_fetcher:
         data_fetch_task = Task(
             description=(
                 "Retrieve historical price data for a list of tickers between 2020 and 2025. "
                 "Produce a table of dates and closing prices for each ticker.  Use yfinance or "
                 "another API through Python.  Save the data as CSV or DataFrame in the knowledge base. "
                 "Assume tickers are provided via configuration (e.g., ['^GSPC','BTC-USD','ETH-USD','XLP'])."
             ),
             agent=data_fetcher,
             expected_output="A dictionary mapping each ticker to a DataFrame of date and price.",
             context=[research_task],
         )
     else:
         data_fetch_task = None

     # Task: forecast future prices using historical data and macro context
     if forecast_agent:
         forecast_task = Task(
             description=(
                 "Using the historical price data and macro context from the research task, "
                 "build forecasting models (e.g., ARIMA or regression).  Predict price trajectories "
                 "for 2026–2030 and include confidence intervals to reflect uncertainty.  Generate a "
                 "plot for each asset with ribbons showing the forecast range and save as an image."
             ),
             agent=forecast_agent,
             expected_output=(
                 "Forecast plots saved to the staging directory and a report describing the modelling "
                 "approach, assumptions and key insights."
             ),
             context=[research_task, data_fetch_task] if data_fetch_task else [research_task],
         )
     else:
         forecast_task = None

     # Assemble tasks in order.  Include optional data fetch and forecast tasks if defined.
     tasks = [summarise_task, research_task]
     if data_fetch_task:
         tasks.append(data_fetch_task)
     if forecast_task:
         tasks.append(forecast_task)
     tasks.extend([evaluate_task, develop_task, validate_task, deploy_task])
     return tasks


def build_crew() -> Crew:
    """Construct and return the CrewAI crew with agents and tasks."""
    agents = build_agents()
    tasks = build_tasks(agents)
    crew = Crew(
        agents=agents,
        tasks=tasks,
        # The process can be sequential or defined with more fine‑grained
        # flows.  Here we rely on the tasks' `context` to enforce order.
        verbose=True
    )
    return crew
