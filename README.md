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
uv run python build.py

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
│   │   └── llm.md         # LLM-specific content
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── base.html      # Base template with navigation
│   │   ├── index.html     # Homepage template
│   │   └── page.html      # Standard page template
│   ├── static/            # CSS, JavaScript, and images
│   │   ├── style.css      # Website styling
│   │   └── script.js      # Interactive functionality
│   ├── builders/          # Python build system
│   │   ├── markdown_processor.py  # Markdown to HTML conversion
│   │   ├── template_engine.py     # Jinja2 template rendering
│   │   ├── plot_generator.py      # Data visualization
│   │   ├── icon_generator.py      # Navigation icon creation
│   │   └── site_builder.py       # Main build orchestration
│   └── agents/            # AI agents for content automation
│       ├── crew_agents.py # CrewAI agent definitions
│       └── local_data/    # Agent data storage
├── docs/                  # Generated website (GitHub Pages)
├── .github/              
│   └── workflows/
│       └── deploy.yml     # Automated deployment
├── build.py              # Main build script
├── pyproject.toml        # Dependencies and project config
└── README.md
```

## 🛠️ Build System

The website uses a modern Python-based build system with these key features:

- **Markdown Content**: All pages written in Markdown with YAML frontmatter
- **Template Engine**: Jinja2 templates preserve the glass-morphism design
- **Plot Generation**: Matplotlib/Seaborn plots with website color scheme
- **Icon Generation**: Custom navigation icons created programmatically
- **Single Command Build**: `uv run python build.py` handles everything

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

Add new plots by extending `src/builders/plot_generator.py`:

```python
def create_your_plot():
    setup_plot_style()  # Uses website colors
    # Your matplotlib code here
    plt.savefig('docs/images/your_plot.png', dpi=300, bbox_inches='tight')
```

## 🤖 AI Agent Integration

The project includes CrewAI agents for automated content updates:

- **SummarizerAgent**: Processes new data files
- **ResearcherAgent**: Finds authoritative sources  
- **DataFetcherAgent**: Retrieves market data
- **ForecastAgent**: Generates predictions
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
uv run python build.py

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
uv run python build.py && uv run python -m http.server 8000 -d docs

# Make changes to src/content/ or src/templates/
# Re-run build.py to see updates
```

### Adding New Features

1. **New Page**: Add `your-page.md` to `src/content/`
2. **New Template**: Add to `src/templates/` if needed
3. **New Icons**: Extend `src/builders/icon_generator.py`
4. **New Plots**: Extend `src/builders/plot_generator.py`

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
2. **Build**: Run `uv run python build.py`
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

The file `agents/crew_agents.py` contains definitions for eight agents (summariser, researcher, evaluator, developer, validator, deployer, data fetcher and forecaster).  You can adjust the agents’ goals, backstories and allowed tools to suit your needs.  When adding new categories or tasks, extend the `build_agents()` and `build_tasks()` functions accordingly.

Agents share context through a simple knowledge base (not implemented here).  For production use, integrate a vector store (e.g., Chroma, Pinecone) to persist embeddings and retrieval results.  Ensure that sensitive API keys and tokens are never hard‑coded in the repository.

## Citation Handling

All factual statements on the website should link to authoritative sources.  The summariser and researcher agents are instructed to capture full URLs for each fact and include them as Markdown hyperlinks in their outputs.  The developer agent then embeds those links directly into the site content.  This mechanism helps visitors verify claims and explore deeper context.

## Updating or Extending the Site

- To add a new page, create an HTML file in `docs/` and link it from the navigation bar.

## License

MIT License