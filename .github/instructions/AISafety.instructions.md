---
applyTo: '**/*.{py,ts,md}'
---

The goal is to develop and maintain a self‑updating website that aggregates economic, policy, technological and social data through a network of AI agents. Its intention is to help people prepare for the upcoming changes related to AI and automation, drastic economic changes (debt crisis, crypto, geopolitics, etc). The goal is to provide rich, evidence‑based content while allowing new information to be added via weekly batch updates.

## Project Architecture

The project follows a clean separation of concerns:

- **`src/content/`** - Markdown files with YAML frontmatter for all page content
- **`src/templates/`** - Jinja2 HTML templates that preserve the glass-morphism design
- **`src/builders/`** - Python modules for markdown processing, plot generation, and site building
- **`src/static/`** - CSS, JavaScript, and image assets
- **`src/agents/`** - AI agents for automated content updates (CrewAI-based). May involve data or fine-tuning.
- **`docs/`** - Generated website output for GitHub Pages deployment
- ** `tests/`** - Unit tests for core functionality

## Development Guidelines

### Dependencies and Environment
- Use `uv` and `pyproject.toml` for all dependency management
- Configure matplotlib with `matplotlib.use('Agg')` to prevent GUI popups during plot generation
- Use `uv run` for all command execution instead of manual virtual environment activation

### Build System
- **Single build command**: `uv run python build.py` handles everything
- **Plot generation**: Use website color scheme and save directly to output directory
- **Template rendering**: Preserve exact current styling and responsive design
- **Asset copying**: Maintain all current images, CSS, and JavaScript functionality

### Content Management
- **Markdown files** should use YAML frontmatter for metadata (title, tagline, description)
- **Custom shortcodes** are supported for tabs, image wrapping, and interactive content
- **Plot references** should use standard markdown image syntax pointing to generated plots

### Code Quality
- Run `uv run ruff check` and `uv run mypy .` for linting and type checking
- Write tests for core functionality only - focus on business logic, not simple integrations
- Design for extensibility: new agents, data sources, and content types should be easy to add
- Keep functions modular and reusable across different build steps

### Deployment Workflow
- **GitHub Pages hosting**: Build output goes to `docs/` folder
- **Push-to-deploy**: Pushing to main branch automatically triggers build and deployment via GitHub Actions
- **Local testing**: Use `uv run python -m http.server 8000 -d docs` for local preview

### AI Agent Integration
- **Agents location**: `src/agents/` with data in `src/agents/local_data/`
- **Weekly updates**: Agents should update markdown content and data files, then trigger rebuild
- **Content validation**: Agents should verify factual accuracy and maintain citation links
- **Deployment automation**: Agents can commit changes that trigger automatic deployment

### Design Preservation
- **Glass-morphism styling**: Maintain translucent elements and current visual design
- **Interactive features**: Preserve tab switching, smooth animations, and responsive behavior
- **Navigation structure**: Keep current page hierarchy and navigation patterns
- **Professional typography**: Maintain current font choices and text styling

### Error Handling
- **Graceful failure**: Build should end if individual plots fail
- **Clear error messages**: Provide actionable feedback for build failures
- **Non-blocking warnings**: matplotlib backend warnings are acceptable if plots generate correctly

