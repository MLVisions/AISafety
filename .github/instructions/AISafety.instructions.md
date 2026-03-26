---
applyTo: '**/*.{py,ts,md}'
---

# AI Safety Website Development Guidelines

## Vision & Purpose

This project develops and maintains a self-updating website that aggregates economic, policy, technological and social data through AI agents to help people prepare for AI-driven societal changes. See the main README.md for complete project details, setup instructions, and deployment information. In the long run, the economic page will be a larger portion, and hopefully be able to help with financial planning and things. References and verified economic models are key to improving trust, as well as disclaimers where necessary. The goal is to have a website that becomes more detailed and accurate over time through AI-driven updates, but the original content should be used as a starting point, and sections/pages shouldn't change. Organization should be preserved, but details should be updated and expanded. The goal should be to help educate and inform people about a wide variety of topics related to AI safety, and to provide actionable insights and resources for navigating the complex landscape of AI-driven societal changes. The website should be a trusted resource that evolves with the rapidly changing AI landscape, providing up-to-date information and analysis to help people make informed decisions about their future in an AI-driven world.



## Development Standards

Re-use code, centralize logic, and maintain a single source of truth for all content and styling. The build system should allow for targeted updates to specific pages or sections without requiring a full site rebuild, while still providing the option for a complete rebuild when necessary. 
 - DO NOT support backwards compatibility, "fallback logic", or otherwise support older versions of how this repo works. When refactoring or making changes, update everything to only support the new methodology. The goal is to have a clean, maintainable codebase that evolves with the project without accumulating technical debt or legacy code. 
 - Avoid redundancies in logic or code. If you find places where this exists, consider creating helper functions to consolidate logic and improve maintainability. The most efficient and minimal code solutions are preferred, though flexibility is also important where helpful.
 - Identify areas where more modularity may help with the re-use of helper functions and reduce redundancies in code/logic. Consider refactoring existing functions (e.g., adding a new argument) to make them more flexible and reusable across different agents or parts of the codebase, rather than creating new functions with similar logic.
 - Centralization: import functions, data, styling, content, and other resources from a single source of truth. For example, if there are specific colors or styling elements used across the site, centralize those in a single CSS file or a Python module that generates styles. If there are common content elements or data sources, centralize those in a single markdown file or Python module that can be imported and used across different pages or agents. This reduces the risk of inconsistencies and makes it easier to update and maintain the codebase as the project evolves. It can also help to reduce the amount of code we need to maintain. 
 - Verify arguments and supported functionality for libraries used. Write functions as efficiently (minimal code) as possible using supported functionality.
 - Only add support for needed functionality. Good modularity is important, but avoid adding unecessary flexibility or support if they arent needed.
 - Avoid overcomplicating logic with unecessary conditionals or try/except blocks. Engineer clean, modular solutions that are easy to read and maintain and follow docs from libraries used.
- __init__.py scripts should generally be empty. Import functions from submodules and follow best coding pratices.
- Imports should be at the top of all scripts
- Aim to simplify and reduce code/complexity if found during development. If you find a more efficient way to do something, consider refactoring existing code to use that method, even if it means changing multiple files. Ask the user before making changes like this unless they are simple.
- Be sure there are no unused imports, variables, or functions in the codebase. If you find any during development, remove them to keep the code clean and maintainable.
- Be sure to understand enough surrounding code (upstream and downstream logic) before making changes, to ensure you dont break any functionality.
- Check behavior in the termianl (uv run python) before/after making changes to ensure proper understanding of behavior.


### Environment & Dependencies
- **ALWAYS use `uv`** for all dependency management and command execution
- Use `uv run` prefix for ALL terminal commands (pytest, ruff, mypy, python scripts)
- Manage dependencies exclusively through `pyproject.toml`
- Configure matplotlib with `matplotlib.use('Agg')` to prevent GUI popups

### Code Quality & Testing
- **Linting**: `uv run ruff check` - must pass with zero issues
- **Type checking**: `uv run mypy .` - address all type annotation requirements
- **Testing**: `uv run pytest` - maintain comprehensive test coverage for business logic
- **Build verification**: `uv run aisafety build` - ensure functionality remains intact

### Development Practices
- **Context-aware development**: Always consider upstream and downstream logic when making changes
- **Avoid unnecessary conditionals**: Engineer clean, modular solutions over complex branching
- **Modular design**: Keep functions focused, reusable, and easily testable
- **Scalable architecture**: Design for extensibility - new agents, data sources, and content types should integrate seamlessly


### How site updating works

The goal is for the research agents to start with the existing contentn as a foundation, but look to expand upon, update, or even correct information during the research period. It should track any references (per section), and use this to update the markdown files and references.md file during the update stage. The validation stage should then check that the updated content is accurate, relevant, and well-written. The goal is to allow for significant changes to the content if necessary, as long as those changes are improvements. The original content should be used as a starting point, but the AI agents should have the freedom to make significant updates if they find new information or insights that warrant it. The key is that any changes made should be improvements in terms of accuracy, relevance, and detail, rather than just rewording or minor edits. The HTML files should then be programatically updated from those markdown files, and any plots should be regenerated if needed. The overall structure and organization of the content should be preserved, but the details can be updated and expanded as needed to ensure the information remains current and accurate.

### Build & Content System
- **Single build command**: CLI for updating content, generating plots, and the overall website. We should be able to update certain pages or sections without rebuilding the entire site, but the option for a full rebuild should always be available.
- **Plot generation**: Use website color scheme, save directly to output directory
- **Template rendering**: Preserve exact current styling and responsive design
- **Asset management**: Maintain all current images, CSS, and JavaScript functionality
- **Markdown processing**: YAML frontmatter for metadata, custom shortcodes for interactive content

### Testing Strategy
- **Business logic focus**: Test core functionality, not simple integrations
- **Test-driven changes**: Update tests when modifying functionality
- **Integration validation**: Ensure changes don't break existing workflows

### AI Agent Integration
- **Always consult and update `agent_network.md`** before making ANY changes to the agent system
- **Architecture**: YAML-based agents (`agents.yaml`, `tasks.yaml`) with utility classes for direct access
- **Utility Classes**: MarketDataUtils, ContentValidationUtils, BuildOrchestratorUtils for programmatic access
- **Error handling**: Graceful failures with output to designated directories
- **Data sources**: Local files in `src/agents/local_data/`, utilities in `src/agents/utils/`


### Content Update Philosophy
- **Goal**: Website becomes more detailed and accurate over time through AI-driven updates
- **AI-Driven**: Let AI make intelligent updates based on new data and trends, but always validate changes for accuracy and relevance. The original content should be uses as a starting point, and sections/pages shouldnt change. Organization should be preserved, but details should be updated and expanded.
- **Validation**: Ensure updates only improve accuracy/detail, not unnecessary rewording
- **References**: Build up trusted reference collection with each automation run
- **Generalization**: Most logic should work for all pages; only system instructions differ per-page (economic page and pages involving plots and things will involve more steps outside of AI content updates, but the overall structure should be preserved and generalized as much as possible)


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

