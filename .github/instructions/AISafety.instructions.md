---
applyTo: '**/*.{py,ts,md}'
---

# AI Safety Website Development Guidelines

## Vision & Purpose

This project develops and maintains a self-updating website that aggregates economic, policy, technological and social data through AI agents to help people prepare for AI-driven societal changes. See the main README.md for complete project details, setup instructions, and deployment information.

## Project Architecture

The project follows a clean separation of concerns with modular, scalable design:

- **`src/content/`** - Markdown files with YAML frontmatter for all page content
- **`src/templates/`** - Jinja2 HTML templates that preserve the glass-morphism design
- **`src/builders/`** - Python modules for markdown processing, plot generation, and site building
- **`src/static/`** - CSS, JavaScript, and image assets
- **`src/agents/`** - AI agents for automated content updates (CrewAI-based).
- **`src/agents/local_data/`** - Local data sources for AI agents
- **`src/agents/utils/`** - *Generalized* utility functions for AI agents
- **`src/agents/mcp_server.py`** - *Generalized* CrewAI server interface for AI agents. 
  - Should be usable by `copilot` and `continue`. Refer to online documentation for development details.
- **`docs/`** - Generated website output for GitHub Pages deployment
- **`tests/`** - Comprehensive unit tests for all core functionality

## Development Standards

### Environment & Dependencies
- **ALWAYS use `uv`** for all dependency management and command execution
- Use `uv run` prefix for ALL terminal commands (pytest, ruff, mypy, python scripts)
- Manage dependencies exclusively through `pyproject.toml`
- Configure matplotlib with `matplotlib.use('Agg')` to prevent GUI popups

### Code Quality & Testing
- **Linting**: `uv run ruff check` - must pass with zero issues
- **Type checking**: `uv run mypy .` - address all type annotation requirements
- **Testing**: `uv run pytest` - maintain comprehensive test coverage for business logic
- **Build verification**: `uv run python build.py` - ensure functionality remains intact

### Development Practices
- **Context-aware development**: Always consider upstream and downstream logic when making changes
- **Avoid unnecessary conditionals**: Engineer clean, modular solutions over complex branching
- **Modular design**: Keep functions focused, reusable, and easily testable
- **Scalable architecture**: Design for extensibility - new agents, data sources, and content types should integrate seamlessly

### Documentation Requirements
- **README.md**: Keep project overview, setup, and usage instructions current
- **agent_network.md**: **CRITICAL** - Update this when modifying agents, workflows, or automation
- **Function documentation**: Document all core business logic with clear docstrings
- **pyproject.toml**: Maintain accurate dependencies and project metadata
- **Tests**: Update test expectations when functionality changes
- **Workflow changes**: Always update `agent_network.md` when adding/modifying automation components

### Build & Content System
- **Single build command**: `uv run python build.py` handles complete site generation
- **Plot generation**: Use website color scheme, save directly to output directory
- **Template rendering**: Preserve exact current styling and responsive design
- **Asset management**: Maintain all current images, CSS, and JavaScript functionality
- **Markdown processing**: YAML frontmatter for metadata, custom shortcodes for interactive content

### Testing Strategy
- **Business logic focus**: Test core functionality, not simple integrations
- **Test-driven changes**: Update tests when modifying functionality
- **Integration validation**: Ensure changes don't break existing workflows
- **Build verification**: Always verify `uv run python build.py` succeeds after changes

### AI Agent Integration
- **Always consult `agent_network.md`** before making ANY changes to the agent system
- **Architecture**: YAML-based agents (`agents.yaml`, `tasks.yaml`) with utility classes for direct access
- **Agent Network Reference**: `agent_network.md` contains complete workflow documentation, missing components, and integration points
- **CrewAI patterns**: Use Agent/Task/Crew classes with proper tool integration - consult online docs
- **Tools**: SerperDevTool, WebsiteSearchTool, FileReadTool, DirectoryReadTool - install via `crewai-tools`
- **Utility Classes**: MarketDataUtils, ContentValidationUtils, BuildOrchestratorUtils for programmatic access
- **Error handling**: Graceful failures with output to designated directories
- **Data sources**: Local files in `src/agents/local_data/`, utilities in `src/agents/utils/`


### Content Update Philosophy
- **Goal**: Website becomes more detailed and accurate over time through AI-driven updates
- **AI-Driven**: Let AI make intelligent updates; avoid hardcoded regex patterns
- **Validation**: Ensure updates only improve accuracy/detail, not unnecessary rewording
- **References**: Build up trusted reference collection with each automation run
- **Generalization**: Most logic should work for all pages; only system instructions differ per-page


### Design Preservation
- **Glass-morphism styling**: Maintain translucent elements and current visual design
- **Interactive features**: Preserve tab switching, smooth animations, and responsive behavior
- **Navigation structure**: Keep current page hierarchy and navigation patterns
- **Professional typography**: Maintain current font choices and text styling
- **Mobile responsiveness**: Ensure compatibility with iOS Safari and accessibility standards

### Deployment & Local Development
- **GitHub Pages**: Build output goes to `docs/` folder for automatic deployment
- **Local testing**: Use `uv run python -m http.server 8000 -d docs` for preview
- **CI/CD**: Pushing to main branch triggers build and deployment via GitHub Actions

### Error Handling
- **Graceful degradation**: Build should continue if individual components fail
- **Clear diagnostics**: Provide actionable feedback for build failures
- **Non-blocking warnings**: Acceptable if functionality remains intact

