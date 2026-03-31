# AI Safety

The goal is to develop and maintain a self‑updating website that aggregates economic, policy, technological and social data through a network of AI agents. Its intention is to help people prepare for the upcoming changes related to AI and automation, drastic economic changes (debt crisis, crypto, geopolitics, etc). The goal is to provide rich, evidence‑based content while allowing new information to be added via weekly batch updates.




# AI Safety Website

A modern, self-updating website that aggregates economic, policy, technological and social data to help people prepare for AI-driven changes. Built with a clean markdown-based content management system and automated plot generation.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/MLVisions/AISafety.git
cd AISafety

# Install dependencies with uv
uv sync

# Build the website
uv run aisafety build

# Start local development server
uv run python -m http.server 8000 -d docs

# Open http://localhost:8000 in your browser
```

## 📁 Project Structure

```
AISafety/
├── src/
│   ├── content/           # Markdown files with YAML frontmatter
│   │   ├── index.md       # Homepage content
│   │   ├── economy.md     # Economic analysis
│   │   ├── technology.md  # AI & Technology insights
│   │   ├── society.md     # Social impact analysis
│   │   ├── privacy.md     # Privacy & Security
│   │   ├── action.md      # Actionable recommendations
│   │   ├── llm.md         # LLM-specific content
│   │   └── references.md  # Research citations and sources
│   ├── agents/            # AI agent network and CLI
│   │   ├── cli.py         # CLI entry point
│   │   ├── build.py       # CLI parser definition
│   │   ├── orchestrator.py # Workflow orchestrator
│   │   ├── research_agents.py # LLM-powered research
│   │   ├── agents.yaml    # Agent configurations
│   │   ├── tasks.yaml     # Task definitions
│   │   └── utils/         # Shared utilities and constants
│   ├── market/            # Market data and economic modeling
│   │   ├── investment_pipeline.py # Market data pipeline
│   │   ├── data_sources.py       # Ticker data fetching
│   │   ├── economic_models.py    # Monte Carlo simulations
│   │   └── plot_functions.py     # Market-specific plots
│   ├── builders/          # Python build system
│   │   ├── site_builder.py       # Main build orchestration
│   │   ├── markdown_processor.py # Markdown to HTML conversion
│   │   └── template_engine.py    # Jinja2 template rendering
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── base.html      # Base template with navigation
│   │   └── page.html      # Standard page template
│   └── static/            # CSS, JavaScript, and images
│       ├── style.css      # Website styling
│       └── script.js      # Interactive functionality
├── docs/                  # Generated website (GitHub Pages)
├── .github/              
│   └── workflows/
│       └── deploy.yml     # Automated deployment
├── pyproject.toml        # Dependencies and project config
└── README.md
```

## 🛠️ Build System

The website uses a modern Python-based build system with these key features:

- **Markdown Content**: All pages written in Markdown with YAML frontmatter
- **Template Engine**: Jinja2 templates preserve the glass-morphism design
- **Plot Generation**: Matplotlib/Seaborn plots with website color scheme
- **Icon Generation**: Custom navigation icons created programmatically
- **Single Command Build**: `uv run aisafety build` handles everything

### Content Management

Create or edit Markdown files in `src/content/` with YAML frontmatter:

```markdown
---
title: "Page Title"
tagline: "Subtitle text"
description: "SEO description"
---

# Your Content Here

Use standard Markdown syntax...
```

### Adding Data Visualizations

Add new plots via `src/market/plot_functions.py`:

```python
def create_your_plot():
    setup_plot_style()  # Uses website colors
    # Your matplotlib code here
    plt.savefig('docs/images/your_plot.png', dpi=300, bbox_inches='tight')
```

## 🤖 AI Agent Network

The project includes a sophisticated CrewAI agent network for automated content updates and investment analysis:

### Current Status: Unified Agent Network (Complete)
✅ **Basic Framework**: Unified YAML-based configuration system operational  
✅ **Reference Synchronization**: Automated citation management working  
✅ **Core Research Agents**: Market, technology, policy, and social research functional  
✅ **Build Integration**: Agent → content → build → deploy pipeline complete

### Completed: Advanced Investment Strategy Pipeline
✅ **Investment Analysis**: Complex multi-agent system for portfolio strategies operational  
✅ **Economic Modeling**: Monte Carlo simulation with Geometric Brownian Motion implemented  
✅ **Historical Data**: 100+ year analysis across 65+ assets (S&P 500 back to 1927, Bitcoin to 2014)  
✅ **Portfolio Simulation**: AI-driven investment strategy backtesting with confidence intervals  
✅ **Data Integration**: Automated CSV generation and website plot updates

### In Development: Enhanced Features  
🚧 **Page-Specific Networks**: Specialized agent teams for each website section  
🚧 **Interactive Dropdowns**: Website evidence charts with historical data selection  
🚧 **Multiple Economic Models**: CAPM, Fama-French integration for model comparison

### Agent Architecture

**Current Research Agents:**
- **Market Researcher**: Economic indicators, AI investment trends, market data
- **Technology Researcher**: AI developments, capabilities, industry adoption  
- **Policy Researcher**: Government regulations, legislative changes, policy impacts
- **Social Researcher**: Employment effects, mental health, social equity issues

**Current Content Agents:**
- **Content Validator**: Fact-checking, citation verification, link validation
- **Content Updater**: Integrates research findings, maintains editorial quality
- **Reference Manager**: Synchronizes references.md with content citations

**Current Infrastructure Agents:**
- **Market Data Fetcher**: Updates financial data for visualizations
- **Build Orchestrator**: Coordinates website builds and deployment

**Planned Investment Strategy Agents:**
- **Historical Data Analyst**: Fetches 100+ years of market data across all asset classes
- **Trend Visualization Agent**: Creates interactive charts with dropdown evidence
- **Economic Model Agent**: Implements well-documented financial models (CAPM, Black-Scholes, etc.)
- **Portfolio Simulation Agent**: Generates PersonA/B/C investment scenarios using combined analysis
- **Strategy Validation Agent**: Backtests and validates investment recommendations

### Investment Strategy Pipeline (Under Development)

The most complex part of the system is the investment strategy analysis for the three investor personas (PersonA, PersonB, PersonC). This requires:

1. **Comprehensive Data Collection**:
   - Stocks, crypto, bonds, REITs, commodities
   - Historical data: 100+ years for gold, back to 2011 for Bitcoin, maximum available for each asset
   - International markets and indices for diversification

2. **Multi-Modal Analysis**:
   - **Visual Analysis**: Plot all tickers over time, store in website dropdowns as evidence
   - **Economic Modeling**: Research and implement established models (Monte Carlo, CAPM, Fama-French)
   - **Trend Analysis**: AI agents analyze individual assets and overall market patterns

3. **Portfolio Simulation**:
   - Takes trend analysis + economic model outputs + investment allocation splits
   - Simulates portfolio performance over model-appropriate timeframes (3-10+ years)
   - Generates CSV data in current format (PersonA/B/C columns with confidence intervals)
   - Connects to existing plot generation system for seamless website integration

4. **Interactive Features**:
   - Website dropdowns for different economic models (if multiple viable)
   - Evidence charts showing historical data supporting recommendations
   - Dynamic portfolio allocation testing

### Running Agent Updates

```bash
# Run full website update workflow
uv run python -c "from src.agents.agent_network import run_website_update; run_website_update()"

# Run just reference synchronization  
uv run python -c "from src.agents.reference_sync import sync_website_references; sync_website_references()"

# Run investment strategy analysis (when implemented)
uv run python src/agents/investment_pipeline.py

# Run master update script
uv run python src/agents/master_update.py
```

### Agent Configuration

Agents are configured via YAML files:
- `src/agents/agents.yaml`: Agent roles, goals, backstories, and tools
- `src/agents/tasks.yaml`: Task definitions and expected outputs

The system ensures content accuracy while maintaining the website's focus on individual preparation for AI-driven changes.
- **EvaluatorAgent**: Assesses content quality
- **DeveloperAgent**: Creates Markdown drafts
- **ValidatorAgent**: Ensures accuracy
- **DeployerAgent**: Handles updates

Agents are positioned for future automation but not currently integrated into the build process.

## 🚀 Deployment

### GitHub Pages (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update website"
   git push origin main
   ```

2. **GitHub Actions automatically**:
   - Builds the website
   - Deploys to GitHub Pages
   - Updates live site

### Manual Deployment

```bash
# Build locally
uv run aisafety build

# Deploy docs/ folder to your hosting provider
```

## 🎨 Design System

The website uses a professional glass-morphism design with:

- **Color Scheme**: Blues and teals with strategic accent colors
- **Typography**: Clean, readable fonts optimized for content
- **Interactive Elements**: Smooth animations and hover effects
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: High contrast and keyboard navigation

## 🔧 Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Local Development

```bash
# Install dependencies
uv sync

# Start development server with auto-reload
uv run aisafety build && uv run python -m http.server 8000 -d docs

# Make changes to src/content/ or src/templates/
# Re-run `uv run aisafety build` to see updates
```

### Adding New Features

1. **New Page**: Add `your-page.md` to `src/content/`
2. **New Template**: Add to `src/templates/` if needed
3. **New Icons**: Run `uv run python scripts/icon_generator.py`
4. **New Plots**: Extend `src/market/plot_functions.py`

## 📊 Content Structure

### Main Sections

- **Home**: Overview and introduction
- **Economy & Policy**: Financial analysis and portfolio projections
- **AI & Technology**: Technical insights and capabilities
- **Society & Mental Health**: Social impact analysis
- **Privacy & Security**: Safety and protection strategies
- **What We Can Do Now**: Actionable recommendations

### Interactive Features

- **Portfolio Analysis Tabs**: Compare investment strategies
- **Responsive Navigation**: Clean, accessible menu system
- **Chart Integration**: Professional data visualizations

## 🔄 Update Workflow

1. **Content Updates**: Edit Markdown files in `src/content/`
2. **Build**: Run `uv run aisafety build`
3. **Test**: Start local server and verify changes
4. **Deploy**: Push to GitHub for automatic deployment

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the build process
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues or questions:
- Open a GitHub issue
- Check the build logs for error messages
- Ensure all dependencies are installed with `uv sync`

The update process is designed to run manually for the proof‑of‑concept but can easily be scheduled (e.g., via `cron`) to execute weekly.

## Customising Agents

Agent definitions live in `src/agents/agents.yaml` and task descriptions in `src/agents/tasks.yaml`. Writing-style rules are in `src/agents/writing_guidelines.yaml`. Adjust agent goals, backstories, and tool configurations to suit your needs. When adding new pages or sections, extend the page configuration in `src/agents/utils/page_config.py`.

## Citation Handling

All factual statements on the website should link to authoritative sources.  The summariser and researcher agents are instructed to capture full URLs for each fact and include them as Markdown hyperlinks in their outputs.  The developer agent then embeds those links directly into the site content.  This mechanism helps visitors verify claims and explore deeper context.

## Updating or Extending the Site

- To add a new page, create a Markdown file in `src/content/` and run `uv run aisafety build`.

## License

MIT License