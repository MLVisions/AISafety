# AI Safety Website Agent Network Documentation

## Overview

This document defines the complete automation workflow for the AI Safety website, showing how agents, tools, and utility functions work together to maintain and update content. **This is the authoritative reference for the agent network architecture - consult this document before making any changes to the automation system.**

Last Updated: March 2026

## Architecture Principles

### Section-Level Agent Design
Every page section (H2 heading) that requires research has its own dedicated `(agent, task)` pair defined in `page_config.py`. The **agent** (from `agents.yaml`) provides domain expertise; the **task** (from `tasks.yaml`) provides section-specific research instructions. This ensures each section gets focused, domain-appropriate updates instead of one generic agent trying to cover everything.

### AI vs Programmatic Boundary
AI (LLM) is used for exactly two things:
1. **Research** — LLM agents gather findings per-section using web search and existing content as context
2. **Validation** — LLM compares old vs new markdown to verify updates improve accuracy/detail

Everything else is **programmatic** (no LLM):
- Content update application (structured JSON → markdown edits)
- Reference syncing (extract citations from markdown → rebuild references.md)
- Market data fetching (yfinance API → CSV)
- Economic modeling (Monte Carlo simulations)
- Plot generation (matplotlib/seaborn)
- Site building (markdown → HTML via Jinja2)

### Content Pipeline
Content flows from `src/content/*.md` (source of truth) through Jinja2 templates to `docs/*.html` (deployment output). All content edits target the markdown files; the build system regenerates HTML.

### Reference Pipeline
Research agents return a `references` list alongside their `updates`. The orchestrator tags each reference with `originating_page` and `originating_section` so the reference manager can organize `references.md` by page and section. Citation extraction also scans content files line-by-line, tracking which H2 section each inline link belongs to. The resulting `references.md` is a generated file (never manually edited) and is rebuilt on every automation cycle.

### Backup Strategy
All file backups are written to the project-level `backups/` directory, never alongside source files in `src/content/`. The `references.md` file is generated (not authored) so it is not backed up.

### Centralized Constants
Shared color palettes and plot styling live in `src/agents/utils/constants.py`. Market-specific display names, ticker descriptions, and category metadata live in `src/market/ticker_constants.py`. No module should duplicate these values.

### Writing Style
All writing agents incorporate rules from `src/agents/writing_guidelines.yaml` into their prompts. Key rules: no em dashes, Oxford comma always, professional tone, every claim needs citation.

### LLM Configuration
LLM access is provider-agnostic via `litellm`. Default model: `openai/gpt-5-mini`. Configuration managed through `src/agents/utils/llm_config.py` with environment variable overrides. The `config` CLI command provides both interactive setup and non-interactive flags (`--show`, `--model`, `--set-key`) for scripting and future Shiny app integration.

### Local Data Integration
Research agents can receive local reference files (PDF, PNG) alongside web search results. Files live in `src/agents/local_data/` and are assigned to tasks via the `local_files` list in `tasks.yaml`. The `LocalDataLoader` (`src/agents/utils/local_data_loader.py`) base64-encodes files and passes them to the LLM as multimodal content blocks. Unsupported formats (DOCX, PPTX) are logged as warnings and skipped.

## Current Implementation Status

### Working Components
- **YAML Agent Network**: Research agents in `agents.yaml`, section-specific tasks in `tasks.yaml`
- **Section-Level Config**: `page_config.py` maps each H2 section to an `(agent, task)` pair via `SectionAgentConfig`
- **Orchestrator**: `src/agents/orchestrator.py` coordinates section-level research, content updates, and full-cycle workflows
- **Research Agents**: `src/agents/research_agents.py` performs section-targeted research with writing guidelines
- **Reference Manager**: `src/agents/utils/reference_manager.py` manages citation synchronization
- **Investment Pipeline**: `src/market/investment_pipeline.py` fetches data, runs models, generates plots
- **Content Update Applier**: `src/agents/utils/content_update_applier.py` applies structured updates to markdown
- **Content Validation**: `src/agents/utils/content_validation_utils.py` validates content quality
- **Build System**: `src/agents/cli.py` + `src/builders/` generates full site from markdown to HTML
- **Plot Generation**: Market trends, portfolio projections, raw ticker charts, category comparisons
- **Centralized Constants**: `src/agents/utils/constants.py` for shared colors/palettes; `src/market/ticker_constants.py` for market-specific display names, colors, descriptions

### Gaps
- Agents produce research reports but do not yet auto-apply all updates to content files
- Domain-specific validation enhancers (tech, policy) not yet implemented
- Homepage synthesis from cross-page research not yet implemented

## Page-Specific Automation Workflows

### 1. ECONOMY.MD - Most Complex Workflow

**Complexity**: Highest (section-level research, data fetching, economic modeling, plot generation)

Section agents (each targets one H2 heading):

| Section | Agent | Task |
|---------|-------|------|
| Macroeconomic Landscape | market_researcher | economy_macro_task |
| Geopolitical & Market Risks | geopolitics_researcher | economy_geopolitics_task |
| Policy & Regulation | policy_researcher | economy_policy_task |
| Financial System Evolution | digital_assets_researcher | economy_financial_infra_task |
| Strategic Recommendations | market_researcher | economy_strategy_task |
| Portfolio & Simulations | *(data pipeline, no LLM agent)* | |
| Portfolio Projections: Persons A, B & C | *(data pipeline, no LLM agent)* | |

```
src/content/economy.md
    |
[section-level research agents]  (5 agents in parallel)
    market_researcher       -> economy_macro_task
    geopolitics_researcher  -> economy_geopolitics_task
    policy_researcher       -> economy_policy_task
    digital_assets_researcher -> economy_financial_infra_task
    market_researcher       -> economy_strategy_task
    |
[content_updater] - content_update_applier.py
    Apply section-specific structured updates to economy.md
    |
[content_validator] - content_validation_utils.py
    |
[market_data_fetcher] - investment_pipeline.py
    Fetch ticker data via yfinance, update src/data/*.csv
    Tickers: 70+ across equity, international, crypto, commodities, real_estate, bonds
    |
[economic_modeling] - economic_models.py
    Monte Carlo simulations for portfolio projections
    |
[plot_generation] - plot_functions.py
    |
[reference_manager] - reference_manager.py
    |
[build] - cli.py -> site_builder.py -> docs/economy.html
```

### 2. TECHNOLOGY.MD & LLM.MD - Tech Research Workflow

**Complexity**: Medium (research-heavy, technical validation)

Technology section agents:

| Section | Agent | Task |
|---------|-------|------|
| AI Capabilities Today | technology_researcher | technology_capabilities_task |
| Investment & Economic Impact | technology_researcher | technology_investment_task |
| Agentic AI & Swarm Architecture | technology_researcher | technology_agents_task |
| Future Trends & Opportunities | technology_researcher | technology_trends_task |

LLM section agents:

| Section | Agent | Task |
|---------|-------|------|
| How Large Language Models Work | technology_researcher | llm_foundations_task |
| AI Agent Architectures: From Monolithic to Distributed Systems | technology_researcher | llm_agents_task |

```
src/content/technology.md / llm.md
    |
[section-level research agents]
    technology_researcher -> technology_*_task / llm_*_task
    |
[content_updater] -> apply section updates
    |
[content_validator]
    |
[reference_manager] -> references.md
    |
[build] -> docs/technology.html, docs/llm.html
```

### 3. SOCIETY.MD & PRIVACY.MD - Social/Policy Workflow

**Complexity**: Medium (multi-domain research, policy accuracy critical)

Society section agents:

| Section | Agent | Task |
|---------|-------|------|
| Mental Health & Labour Disruption | social_researcher | society_mental_health_task |
| Economic Uncertainty & Resilience | social_researcher | society_resilience_task |
| AI Misinformation & Reality Distortion | social_researcher | society_misinformation_task |
| Community & Support | social_researcher | society_community_task |

Privacy section agents:

| Section | Agent | Task |
|---------|-------|------|
| Threats & Misinformation | policy_researcher | privacy_threats_task |
| Security Best Practices | technology_researcher | privacy_security_task |
| Data Privacy & Ethics | policy_researcher | privacy_ethics_task |

```
src/content/society.md / privacy.md
    |
[section-level research agents]
    social_researcher   -> society_*_task
    policy_researcher   -> privacy_threats_task, privacy_ethics_task
    technology_researcher -> privacy_security_task
    |
[content_updater] -> apply section updates
    |
[content_validator]
    |
[reference_manager] -> references.md
    |
[build] -> docs/society.html, docs/privacy.html
```

### 4. ACTION.MD - Action-Oriented Workflow

**Complexity**: Low-Medium (strategy-focused, practicality validation)

| Section | Agent | Task |
|---------|-------|------|
| Take Practical Steps (+ all H3 subsections) | social_researcher | action_steps_task |

```
src/content/action.md
    |
[social_researcher] -> action_steps_task
    |
[content_updater] -> apply section updates
    |
[content_validator]
    |
[reference_manager] -> references.md
    |
[build] -> docs/action.html
```

### 5. INDEX.MD - Homepage

**Complexity**: Low (manually curated overview; future: cross-page synthesis)

```
src/content/index.md
    |
[build] -> docs/index.html
```

### 6. REFERENCES.MD - Citation Database

**Complexity**: Low (managed by reference_manager across all workflows)

Organized by originating page and section (not by URL type). Each citation
is tracked back to the content section it supports.

```
src/content/references.md
    |
[reference_manager] - reference_manager.py
    1. Extract citations from all content files (tracking H2 section)
    2. Merge agent-provided references (tagged with originating_section)
    3. Deduplicate by URL
    4. Write references.md organized by page -> section
    |
[build] -> docs/references.html
```

## Orchestrator Workflows

The `Orchestrator` class (`src/agents/orchestrator.py`) provides these entry points:

1. **`run_update(pages, build)`** - Research → validate → update content → (optionally) build site. Scoped to specific pages when `pages` is provided.
2. **`run_market(plots_only)`** - Fetch market data and update CSVs. When `plots_only=True`, regenerates plots from existing data without re-fetching.

References are synced automatically as part of every build — no standalone references command is needed.

### Build Efficiency
- **Icons**: Static assets in `src/static/images/` -- not regenerated during build. Use `uv run python scripts/icon_generator.py` to regenerate when the design changes.
- **Data plots**: Hash-based caching via `.plot_cache.json`. Plots are skipped if CSV data has not changed.
- **Market plots**: Raw ticker and category comparison plots require live yfinance data and are only generated when explicitly requested (e.g., `uv run aisafety market`).

### CLI Commands

CLI entry point: `uv run aisafety`

| Command | Description | Key Flags |
|---------|-------------|----------|
| `build` | Generate site from markdown → HTML | `--page PAGE`, `--plots` |
| `update` | Research + validate + update content (+ build) | `--page PAGE`, `--no-build` |
| `market` | Fetch market data and generate plots | `--plots-only` |
| `config` | Manage LLM configuration | `--show`, `--model MODEL`, `--set-key PROVIDER KEY` |

Examples:
- `uv run aisafety build` — Build full site
- `uv run aisafety build --page economy --plots` — Build economy page with market plots
- `uv run aisafety update --page technology` — Research and update technology page
- `uv run aisafety update --no-build` — Research all pages without building
- `uv run aisafety market` — Fetch market data and generate all plots
- `uv run aisafety market --plots-only` — Regenerate plots from existing data
- `uv run aisafety config` — Interactive configuration setup
- `uv run aisafety config --show` — Display current config
- `uv run aisafety config --model anthropic/claude-sonnet-4` — Set model
- `uv run aisafety config --set-key openai sk-abc123` — Set API key

## File Locations Reference

### Configuration
- `agents.yaml` - Agent definitions and tool configurations
- `tasks.yaml` - Task descriptions and expected outputs
- `src/agents/writing_guidelines.yaml` - Writing style rules for all agents

### Core Modules
- `src/agents/cli.py` - CLI entry point for building and automation
- `src/agents/build.py` - CLI parser definition and helpers
- `src/agents/orchestrator.py` - Workflow orchestrator
- `src/agents/research_agents.py` - LLM-powered page research
- `src/agents/utils/reference_manager.py` - Citation management
- `src/market/investment_pipeline.py` - Market data and economic modeling
- `src/agents/base_agent.py` - Base agent class

### Utilities (`src/agents/utils/`)
- `constants.py` - Centralized colors and palettes
- `llm_config.py` - LLM provider configuration (litellm); includes `set_api_key()`, `set_model()`, `show_config()` for programmatic access
- `local_data_loader.py` - Load local PDF/PNG files as base64 attachments for LLM consumption
- `page_config.py` - Per-page automation settings
- `patterns.py` - Shared regex patterns and link extraction helpers
- `content_update_applier.py` - Structured content update application
- `content_validation_utils.py` - Content quality validation
- `reference_manager.py` - Citation management
- `file_operations.py` - File I/O helpers

### Market (`src/market/`)
- `ticker_constants.py` - Ticker display names, colors, descriptions
- `data_sources.py` - Ticker definitions and data availability
- `economic_models.py` - Monte Carlo simulation and portfolio modeling
- `historical_visualization.py` - Raw ticker and category comparison plots
- `portfolio_simulation.py` - Portfolio projection engine
- `investment_pipeline.py` - Market data and economic modeling pipeline
- `plot_functions.py` - Market-specific plot generation

### Builders (`src/builders/`)
- `site_builder.py` - Main site build orchestrator
- `markdown_processor.py` - Markdown to HTML with frontmatter and shortcodes
- `template_engine.py` - Jinja2 template rendering

### Scripts (`scripts/`)
- `icon_generator.py` - Navigation icon generation (one-time developer utility)

### Content (`src/content/`)
- `index.md`, `economy.md`, `technology.md`, `llm.md`, `society.md`, `privacy.md`, `action.md`, `references.md`

### Output (`docs/`)
- Generated HTML pages, CSS, JS, images, plot PNGs, data JSON

### Tests (`tests/`)
- `test_investment_pipeline.py` - Economic models, data sources, portfolio simulation, visualization
- `test_markdown_processor.py` - Markdown processing and frontmatter
- `test_page_config.py` - Page configuration factory
- `test_content_update_applier.py` - Content update application

## Development Guidelines

### Before Making Changes
1. Read this document to understand current architecture
2. Identify integration points between your changes and existing components
3. Consider workflow impact on all affected pages

### When Adding New Components
1. Update this document with the new workflow
2. Add tests for the new component
3. Use centralized constants from `constants.py`
4. Follow writing guidelines in `writing_guidelines.yaml`

### When Modifying Existing Agents
1. Check all affected workflows in this document
2. Verify tool configurations remain consistent
3. Run `uv run python -m pytest tests/ -v` to validate
4. Run `uv run aisafety build` to verify site generation

---

**Remember**: This document is the source of truth for the agent network architecture. Keep it updated as workflows evolve and new components are added.
