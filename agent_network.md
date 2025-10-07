# AI Safety Website Agent Network Documentation

## Overview

This document defines the complete automation workflow for the AI Safety website, showing how agents, tools, and utility functions work together to maintain and update content. **This is the authoritative reference for the agent network architecture - consult this document before making any changes to the automation system.**

Last Updated: September 27, 2025

## Architecture Principles

### Agent vs Function Design
- **Agents**: Complex decision-making, research, analysis, multi-step workflows with external APIs
- **Functions/Tools**: Data processing, file operations, calculations, simple transformations
- **Utility Classes**: Direct method access for programmatic automation without CrewAI overhead

### Current Implementation Status
- ✅ **YAML Agents**: All research and content agents implemented in `agents.yaml`
- ✅ **Utility Classes**: MarketDataUtils, ContentValidationUtils, BuildOrchestratorUtils
- ❌ **Missing Bridges**: Content update application, infrastructure execution bridges
- ⚠️ **Partial Integration**: Agents produce reports but don't modify actual files

## Page-Specific Automation Workflows

### 1. ECONOMY.MD - Most Complex Workflow

**Complexity**: Highest (involves data fetching, economic modeling, plot generation, content updates)

```
📄 economy.md (Starting Document)
    ↓
📊 [market_researcher] ✅ IMPLEMENTED
    ├── Location: agents.yaml
    ├── Tools: SerperDevTool, WebsiteSearchTool, FileReadTool
    ├── Task: market_research_task (tasks.yaml)
    ├── Output: research_results.md → automation_outputs/
    ├── Focus: Market trends, economic indicators, financial developments
    └── Status: ✅ Working - produces research reports
    ↓
💰 [market_data_fetcher] ✅ AGENT / ❌ BRIDGE MISSING
    ├── Location: agents.yaml
    ├── Tools: FileReadTool, DirectoryReadTool
    ├── Task: market_data_update_task (tasks.yaml)
    ├── ❌ MISSING: MarketDataExecutionBridge
    │   ├── Should call: MarketDataUtils.fetch_data_direct()
    │   ├── Should trigger: Ticker data updates
    │   └── Should update: src/data/*.csv files
    ├── Expected Output: Updated market data CSV files
    └── Status: ⚠️ Partial - generates reports but doesn't execute data fetching
    ↓
🧮 [❌ MISSING: EconomicModelingBridge] - NEW COMPONENT NEEDED
    ├── Purpose: Execute investment pipeline with new market data
    ├── Should call: run_complete_investment_pipeline()
    ├── Should update: Portfolio CSVs (personA/B/C_portfolio.csv, comparative_wealth.csv)
    ├── Should generate: Economic projections, risk analysis
    ├── Integration point: investment_pipeline.py
    └── Status: ❌ Not implemented - critical gap for economy automation
    ↓
📊 [❌ MISSING: PlotUpdateTrigger] - NEW COMPONENT NEEDED
    ├── Purpose: Regenerate economic plots when data changes
    ├── Should call: PlotGenerator methods for economy-specific plots
    │   ├── market_trends.png
    │   ├── personA/B/C.png (portfolio projections)
    │   └── comparative_wealth.png
    ├── Should verify: Plot generation success and file placement
    ├── Integration point: src/builders/plot_generator.py
    └── Status: ❌ Not implemented - plots not auto-updated
    ↓
🔍 [content_validator] ✅ AGENT / ⚠️ PARTIAL INTEGRATION
    ├── Location: agents.yaml
    ├── Tools: FileReadTool, WebsiteSearchTool
    ├── Task: content_validation_task (tasks.yaml)
    ├── Utility: ContentValidationUtils.validate_content_direct()
    ├── ⚠️ PARTIAL: Validation doesn't use research context
    ├── ❌ MISSING: Research-aware validation
    │   ├── Should incorporate: Market research findings
    │   ├── Should verify: Economic data accuracy against research
    │   └── Should check: Citation alignment with new sources
    └── Status: ⚠️ Works independently but not research-integrated
    ↓
✏️ [content_updater] ✅ AGENT / ❌ EXECUTION MISSING
    ├── Location: agents.yaml
    ├── Tools: FileReadTool
    ├── Task: content_update_task (tasks.yaml)
    ├── Output: content_updates.md → automation_outputs/
    ├── ❌ MISSING: ContentUpdateApplier
    │   ├── Should parse: Agent research reports
    │   ├── Should extract: Specific update recommendations
    │   ├── Should apply: Changes to src/content/economy.md
    │   ├── Should integrate: New economic data, statistics, projections
    │   └── Should preserve: Existing structure, tone, navigation
    └── Status: ❌ Critical gap - produces recommendations but doesn't update files
    ↓
📚 [reference_manager] ✅ AGENT / ❌ EXECUTION MISSING
    ├── Location: agents.yaml
    ├── Tools: FileReadTool, WebsiteSearchTool
    ├── Task: reference_sync_task (tasks.yaml)
    ├── Output: Reference recommendations → automation_outputs/
    ├── ❌ MISSING: ReferenceUpdateApplier
    │   ├── Should parse: Reference recommendations
    │   ├── Should update: src/content/references.md
    │   ├── Should format: Academic citation standards
    │   └── Should verify: Source accessibility
    └── Status: ❌ Produces recommendations but doesn't update references.md
    ↓
🏗️ [build_orchestrator] ✅ AGENT / ❌ BRIDGE MISSING
    ├── Location: agents.yaml
    ├── Tools: DirectoryReadTool, FileReadTool
    ├── Task: website_build_task (tasks.yaml)
    ├── Utility: BuildOrchestratorUtils.build_website_direct()
    ├── ❌ MISSING: BuildExecutionBridge
    │   ├── Should call: BuildOrchestratorUtils.build_website_direct()
    │   ├── Should verify: Build success
    │   ├── Should handle: Build errors and recovery
    │   └── Should validate: Output completeness
    └── Status: ❌ Generates reports but doesn't execute builds
```

### 2. TECHNOLOGY.MD & LLM.MD - Tech Research Workflow

**Complexity**: Medium (research-heavy, technical validation)

```
📄 technology.md / llm.md
    ↓
🔬 [technology_researcher] ✅ IMPLEMENTED
    ├── Location: agents.yaml
    ├── Tools: SerperDevTool, WebsiteSearchTool, FileReadTool
    ├── Task: technology_research_task (tasks.yaml)
    ├── Focus: AI developments, model releases, capabilities, benchmarks
    ├── Output: Technology research findings → automation_outputs/
    └── Status: ✅ Working - produces comprehensive tech research
    ↓
🔍 [content_validator] ✅ AGENT / ❌ TECH-SPECIFIC VALIDATION MISSING
    ├── Same base agent as economy workflow
    ├── ❌ MISSING: Technology-specific validation
    │   ├── Should verify: Model capability claims
    │   ├── Should check: Performance benchmark accuracy
    │   ├── Should validate: Technical terminology
    │   └── Should confirm: Release date accuracy
    └── Status: ⚠️ Generic validation only
    ↓
✏️ [content_updater] ✅ AGENT / ❌ EXECUTION MISSING
    ├── Same ContentUpdateApplier gap as economy workflow
    ├── Focus areas for tech content:
    │   ├── AI model capabilities and limitations
    │   ├── New model releases and benchmarks
    │   ├── Technical implementation details
    │   └── Future technology projections
    └── Status: ❌ Same execution gap
    ↓
[Same reference_manager and build_orchestrator gaps as economy workflow]
```

### 3. PRIVACY.MD & SOCIETY.MD - Policy/Social Workflow

**Complexity**: Medium (multi-domain research, policy accuracy critical)

```
📄 privacy.md / society.md
    ↓
📜 [policy_researcher] ✅ IMPLEMENTED
    ├── Location: agents.yaml
    ├── Tools: SerperDevTool, WebsiteSearchTool, FileReadTool
    ├── Task: policy_research_task (tasks.yaml)
    ├── Focus: AI regulation, privacy laws, government initiatives
    └── Status: ✅ Working - tracks policy developments
    ↓
👥 [social_researcher] ✅ IMPLEMENTED
    ├── Location: agents.yaml
    ├── Tools: SerperDevTool, WebsiteSearchTool, FileReadTool
    ├── Task: social_research_task (tasks.yaml)
    ├── Focus: Employment effects, mental health, social equity
    └── Status: ✅ Working - researches social implications
    ↓
🔍 [content_validator] ✅ AGENT / ❌ POLICY-SPECIFIC VALIDATION MISSING
    ├── ❌ MISSING: Policy-specific validation
    │   ├── Should verify: Legal accuracy and current status
    │   ├── Should check: Regulation effective dates
    │   ├── Should validate: Official source citations
    │   └── Should confirm: Jurisdiction applicability
    └── Status: ⚠️ Generic validation only
    ↓
[Same content_updater, reference_manager, build_orchestrator gaps]
```

### 4. ACTION.MD - Action-Oriented Workflow ✅ COMPLETED

**Complexity**: Low-Medium (strategy-focused, practicality validation)

```
📄 action.md
    ↓
👥 [social_researcher] ✅ IMPLEMENTED
    ├── Focus: Individual preparation strategies, actionable guidance
    └── Status: ✅ Working for action-oriented research
    ↓
🔍 [content_validator] ✅ IMPLEMENTED
    ├── Base validation: ContentValidationUtils.validate_content_direct()
    ├── ✅ IMPLEMENTED: ActionValidationEnhancer
    │   ├── ✅ Verifies: Strategy feasibility (0.75 avg score)
    │   ├── ✅ Checks: Resource accessibility (0.70 avg score)
    │   ├── ✅ Validates: Step-by-step clarity (0.85 avg score)
    │   └── ✅ Confirms: Individual applicability (0.93 avg score)
    └── Status: ✅ Action-specific validation implemented
    ↓
✏️ [content_updater] ✅ IMPLEMENTED
    ├── Location: ContentUpdateApplier
    ├── ✅ IMPLEMENTED: Research findings parsing
    │   ├── ✅ Extracts: Statistics, trends, strategies, recommendations
    │   ├── ✅ Applies: High-confidence updates (>0.7 confidence)
    │   ├── ✅ Preserves: Document structure and formatting
    │   └── ✅ Creates: Automatic backups before changes
    ├── Integration: ActionAutomationBridge
    └── Status: ✅ Full content update automation working
    ↓
📚 [reference_manager] ✅ AGENT / ✅ IMPLEMENTED
    ├── Location: agents.yaml
    ├── Task: reference_sync_task (tasks.yaml)
    ├── ✅ IMPLEMENTED: Reference update parsing and application
    └── Status: ✅ Working - integrated with content updates
    ↓
🏗️ [build_orchestrator] ✅ IMPLEMENTED
    ├── Location: BuildOrchestratorUtils.build_website_direct()
    ├── ✅ IMPLEMENTED: Full website rebuild integration
    │   ├── ✅ Triggers: Automatic rebuild after content updates
    │   ├── ✅ Validates: Build success and completeness
    │   └── ✅ Reports: Build time and statistics
    └── Status: ✅ Complete automation working (36s avg build time)
```

**✅ ACTION.MD AUTOMATION STATUS: FULLY OPERATIONAL**
- **Research Processing**: ✅ Processes social research findings
- **Enhanced Validation**: ✅ Action-specific validation with 0.94 avg score
- **Content Updates**: ✅ Applies 28 avg updates per automation run
- **Website Rebuild**: ✅ Full build integration with success monitoring
- **Success Rate**: ✅ 100% automation success rate in testing

### 5. INDEX.MD - Homepage Synthesis Workflow

**Complexity**: Medium-High (cross-page synthesis, overview coordination)

```
📄 index.md
    ↓
🔄 [❌ MISSING: HomepageSynthesizer] - NEW COMPONENT NEEDED
    ├── Purpose: Synthesize updates from all domain research
    ├── Input: Research outputs from all other agents
    │   ├── Market research findings
    │   ├── Technology developments
    │   ├── Policy changes
    │   └── Social trends
    ├── Processing: Extract high-level themes and key highlights
    ├── Output: Homepage update recommendations
    └── Status: ❌ Not implemented - homepage not auto-updated
    ↓
🔍 [content_validator] ✅ AGENT / ❌ CROSS-PAGE VALIDATION MISSING
    ├── ❌ MISSING: Cross-page consistency validation
    │   ├── Should verify: Navigation accuracy
    │   ├── Should check: Cross-references between pages
    │   ├── Should validate: Overview accuracy vs detailed pages
    │   └── Should confirm: Tone consistency
    └── Status: ⚠️ Single-page validation only
    ↓
[Same content_updater, reference_manager, build_orchestrator gaps]
```

## Critical Missing Components

### Phase 1: Core Execution Bridges (Critical)

### Phase 1: Core Execution Bridges (Critical)

#### 1. ContentUpdateApplier
**Status**: ✅ IMPLEMENTED (for action.md)  
**Priority**: Critical  
**Purpose**: Parse agent reports and apply updates to actual markdown files

```python
# Implemented interface
class ContentUpdateApplier:
    def apply_research_updates(
        self, 
        file_path: str,
        research_findings: str,
        validation_results: dict[str, Any],
        preserve_structure: bool = True
    ) -> dict[str, Any]:
        """Apply research findings to content file"""
        # ✅ WORKING: Parses research, applies updates, creates backups
```

#### 2. Infrastructure Execution Bridges
**Status**: ✅ IMPLEMENTED (ActionAutomationBridge)  
**Priority**: Critical  
**Components**:
- ✅ ActionAutomationBridge: Complete action.md workflow
- ❌ MarketDataExecutionBridge: market_data_fetcher → MarketDataUtils
- ❌ BuildExecutionBridge: build_orchestrator → BuildOrchestratorUtils (partially implemented in ActionAutomationBridge)

#### 2. Infrastructure Execution Bridges
**Status**: ❌ Not Implemented  
**Priority**: Critical  
**Components**:
- MarketDataExecutionBridge: market_data_fetcher → MarketDataUtils
- BuildExecutionBridge: build_orchestrator → BuildOrchestratorUtils

### Phase 2: Domain-Specific Components (High Impact)

#### 3. EconomicModelingBridge
**Status**: ❌ Not Implemented  
**Priority**: High  
**Purpose**: Connect market research to economic modeling pipeline

#### 4. PlotUpdateTrigger
**Status**: ❌ Not Implemented  
**Priority**: High  
**Purpose**: Regenerate plots when underlying data changes

#### 5. ReferenceUpdateApplier
**Status**: ❌ Not Implemented  
**Priority**: High  
**Purpose**: Apply reference recommendations to references.md

### Phase 3: Enhanced Validation (Medium)

#### 6. Research-Aware Validation
**Status**: ✅ IMPLEMENTED (for action.md)  
**Priority**: Medium  
**Purpose**: Integrate research context into content validation

#### 7. Domain-Specific Validators
**Status**: ⚠️ PARTIALLY IMPLEMENTED  
**Priority**: Medium  
**Components**:
- ❌ TechValidationEnhancer
- ❌ PolicyValidationEnhancer  
- ✅ ActionValidationEnhancer (COMPLETED)

### Phase 4: Advanced Features (Low)

#### 8. HomepageSynthesizer
**Status**: ❌ Not Implemented  
**Priority**: Low  
**Purpose**: Synthesize cross-domain research for homepage updates

## Current System State

### Working Components ✅
- **YAML Agent Network**: All 9 agents properly configured
- **Utility Classes**: MarketDataUtils, ContentValidationUtils, BuildOrchestratorUtils
- **Research Pipeline**: Agents produce comprehensive reports
- **Validation System**: Basic content validation working
- **Build System**: Manual builds working perfectly

### Major Gaps ❌
- **Agent Reports Don't Update Files**: Critical execution gap
- **No Infrastructure Bridges**: Agents don't trigger utility functions
- **No Economic Modeling Integration**: Economy automation incomplete
- **No Plot Updates**: Visualizations not auto-updated
- **No Research-Aware Validation**: Validation ignores research context

### Integration Points ⚠️  
- **AutomationController**: Orchestrates workflow but has execution gaps
- **Agent Network**: Produces reports but needs execution bridges
- **Utility Classes**: Work independently but not agent-integrated

## Testing Strategy

### Current Test Coverage ✅
- Agent network initialization and configuration
- Utility class functionality 
- Individual component testing
- Build system validation

### Missing Test Coverage ❌
- End-to-end automation workflows
- Agent output → file update integration
- Cross-component integration testing
- Error handling and recovery

## Development Guidelines

### Before Making Changes
1. **Read this document** to understand current architecture
2. **Identify integration points** between your changes and existing components
3. **Consider workflow impact** on all affected pages
4. **Plan testing strategy** for new components

### When Adding New Components
1. **Document the workflow** in this file
2. **Update the architecture diagrams** 
3. **Add integration tests** for the complete workflow
4. **Update utility class interfaces** if needed

### When Modifying Existing Agents
1. **Check all affected workflows** in this document
2. **Verify tool configurations** remain consistent
3. **Test agent network initialization** 
4. **Update task descriptions** if needed

### Change Approval Process
1. **Architecture review** against this document
2. **Integration impact assessment**  
3. **Test coverage verification**
4. **Documentation updates**

## File Locations Reference

### Configuration Files
- **agents.yaml**: Agent definitions and tool configurations
- **tasks.yaml**: Task descriptions and expected outputs
- **agent_network.py**: Agent network orchestration logic

### Implementation Files
- **automation_controller.py**: Main automation orchestrator
- **utils/**: Utility classes for direct method access
- **investment_pipeline.py**: Economic modeling pipeline
- **builders/**: Plot generation and site building

### Output Locations
- **automation_outputs/**: Agent research reports and findings
- **src/content/**: Website content files (update targets)
- **src/data/**: Market data CSVs and economic model outputs
- **docs/**: Built website files

---

**Remember**: This document is the source of truth for the agent network architecture. Keep it updated as workflows evolve and new components are added.