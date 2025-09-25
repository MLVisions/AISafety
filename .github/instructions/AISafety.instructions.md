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
- **Function documentation**: Document all core business logic with clear docstrings
- **pyproject.toml**: Maintain accurate dependencies and project metadata
- **Tests**: Update test expectations when functionality changes

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
- **Agents location**: `src/agents/` with data in `src/agents/local_data/`
- **Weekly updates**: Agents update markdown content and data files, trigger rebuilds
- **Content validation**: Verify factual accuracy and maintain citation links
- **Deployment automation**: Agents commit changes that trigger automatic deployment

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

