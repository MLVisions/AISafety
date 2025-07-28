# Swarm Economic Insights – Developer Guide

This repository contains a proof‑of‑concept for a self‑updating website that aggregates economic, policy, technological and social data through a network of AI agents.  The goal is to provide rich, evidence‑based content while allowing new information to be added via weekly batch updates.  This guide explains how to set up the environment, customise the agents and run the update workflow.

## Project Structure

```
├── website/              # Static site files (HTML, CSS, JS and images)
│   ├── index.html        # Landing page with high‑level categories
│   ├── economy.html      # Economy & policy page with graphs and Bitcoin buyers
│   ├── technology.html   # AI & technology page
│   ├── society.html      # Society & mental health page
│   ├── privacy.html      # Privacy & security page
│   ├── action.html       # What you can do now – practical steps
│   ├── llm.html          # How LLMs & agents work
│   ├── images/           # Icons and charts used on the site
│   ├── style.css         # Shared stylesheet
│   └── script.js         # Tab logic for portfolio charts
├── agents/               # CrewAI agent definitions
│   └── crew_agents.py    # Build agents and tasks for the update pipeline
├── run_full_update.py    # Script to execute the full update cycle
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Prerequisites

- **Python 3.9+** – The agent pipeline is written in Python.  You can install dependencies via `pip` or [uv](https://github.com/astral-sh/uv).  The `crewai` library has its own requirements, so using a virtual environment is recommended.
- **Node.js 16+** – Only necessary if you intend to build or extend the front‑end with additional tooling.  The current site uses plain HTML, CSS and JavaScript, so no build step is required.
- **OpenAI API key** – The agents use OpenAI models via the `openai` package.  Export your key as an environment variable before running updates (see below).

## Setup

1. **Clone the repository** and navigate to its root directory.

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies** using `pip` or `uv`:

   ```bash
   # using pip
   pip install -r requirements.txt

   # or using uv (fast alternative)
   uv pip install -r requirements.txt
   ```

4. **Configure your OpenAI API key** by exporting it as an environment variable.  The crew agents read this key from `OPENAI_API_KEY`:

   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

   You can also create a `.env` file in the project root with the line `OPENAI_API_KEY=sk-your-key-here` and install [`python-dotenv`](https://pypi.org/project/python-dotenv/) to load it automatically.

## Running the Full Update

Uploaded documents (e.g., PDF, DOCX, PPTX) should be placed in a designated directory (you can modify `run_full_update.py` to specify the path).  To run the full update pipeline:

```bash
python run_full_update.py
```

The script performs the following high‑level steps:

1. **Summarise** newly uploaded files with the `SummarizerAgent`, storing both raw text and concise summaries in a knowledge base.
2. **Research** external sources for each fact via the `ResearcherAgent`, returning authoritative URLs for citations.
3. **Fetch market data** (optional) using `DataFetcherAgent` for specified tickers and date ranges.  Historical price data is saved for later analysis.
4. **Forecast** future prices with the `ForecastAgent`, producing projections and uncertainty ribbons based on macro context.
5. **Evaluate** whether the new information warrants updates to existing web pages.
6. **Develop** draft Markdown files for any sections that need modification, embedding clickable citations.
7. **Validate** the drafts for accuracy, bias and alignment with the site’s mission.
8. **Deploy** the approved changes by integrating them into the `website/` directory and committing them to version control.

The update process is designed to run manually for the proof‑of‑concept but can easily be scheduled (e.g., via `cron`) to execute weekly.

## Customising Agents

The file `agents/crew_agents.py` contains definitions for eight agents (summariser, researcher, evaluator, developer, validator, deployer, data fetcher and forecaster).  You can adjust the agents’ goals, backstories and allowed tools to suit your needs.  When adding new categories or tasks, extend the `build_agents()` and `build_tasks()` functions accordingly.

Agents share context through a simple knowledge base (not implemented here).  For production use, integrate a vector store (e.g., Chroma, Pinecone) to persist embeddings and retrieval results.  Ensure that sensitive API keys and tokens are never hard‑coded in the repository.

## Citation Handling

All factual statements on the website should link to authoritative sources.  The summariser and researcher agents are instructed to capture full URLs for each fact and include them as Markdown hyperlinks in their outputs.  The developer agent then embeds those links directly into the site content.  This mechanism helps visitors verify claims and explore deeper context.

## Updating or Extending the Site

- To add a new page, create an HTML file in `website/` and link it from the navigation bar.
- To modify styling, edit `website/style.css`.  Avoid using em‑dashes in text; instead substitute hyphens or break the sentence into two.  Icons are stored in `website/images/` and can be replaced or expanded as needed.
- To regenerate or add new graphs, update the images in `website/images/` or implement additional Python scripts that generate charts from the data fetcher’s outputs.

## License

This project is provided as a demonstration and does not constitute financial advice.  Use it as a starting point for your own informational website or research portal.