# REFACTORING IN PROGRESS

## 🎯 Goal
Transform from hardcoded regex patterns to AI-driven content updates.
Remove ~240 lines of brittle pattern matching code, replace with intelligent agent-based updates.

## 📊 Progress Summary
- **Lines Removed**: ~240 lines of hardcoded logic
- **Files Simplified**: 3 core files (page_config.py, infrastructure_bridges.py, content_update_applier.py)
- **New Approach**: AI agents provide structured updates, Python just applies them
- **Scalability**: Adding new pages now requires ONLY metadata + agent instructions (no code changes)

## ✅ COMPLETED

### `page_config.py` - SIMPLIFIED ✅
- Removed all hardcoded regex patterns (181 lines deleted)
- Removed strategy classes entirely  
- Now contains ONLY metadata: research agents, focus areas, validation thresholds
- Added configurations for ALL pages (action, technology, llm, economy, society, privacy)
- Old file backed up as `page_config_DEPRECATED.py`

### `infrastructure_bridges.py` - SIMPLIFIED ✅
- Removed `get_update_strategy()` import
- Removed `self.update_strategy` attribute
- Removed `_extract_suggestions()` method (58 lines of keyword matching)
- Simplified `_apply_content_updates()` to placeholder
- Ready for structured agent output integration

### `content_update_applier.py` - SIMPLIFIED ✅
- Removed `ContentUpdateStrategy` import
- Changed `apply_updates()` signature to accept structured updates
- Marked `_apply_strategy_updates()` as DEPRECATED
- Ready for direct application of agent-generated structured updates
- Old methods kept temporarily for test compatibility

## What This Breaks (Expected)

### Files That Import Strategies:
1. `infrastructure_bridges.py` - Uses `get_update_strategy()` ❌
2. `content_update_applier.py` - Uses `ContentUpdateStrategy` ❌
3. `tests/test_page_config.py` - Tests strategy classes ❌
4. `tests/test_content_update_applier.py` - Tests strategies ❌
5. `tests/test_page_automation_integration.py` - Tests strategies ❌

## Next Steps

### Step 1: Simplify infrastructure_bridges.py
Remove:
- `_extract_suggestions()` method (keyword matching)
- `self.update_strategy` usage
- Strategy-based application

Replace with:
- Direct reading of agent-generated structured output
- Simple content replacement (no regex)

### Step 2: Simplify content_update_applier.py  
Remove:
- Strategy pattern entirely
- `_apply_strategy_updates()` method

Replace with:
- Direct application of structured updates from agents
- Simple text replacement based on agent instructions

### Step 3: Update/Remove Tests
- Delete tests for deleted strategy classes
- Add tests for simplified flow
- Focus on end-to-end workflow tests

## The New Flow (Target)

```
1. Agent generates structured research
   Output: {
     "updates": [
       {
         "section": "Reskill & adapt",
         "type": "statistic",
         "original_text": "83 million jobs",
         "updated_text": "85 million jobs", 
         "source": "https://...",
         "confidence": 0.9
       }
     ]
   }

2. ContentUpdateApplier reads structured output
   - No keyword matching
   - No regex patterns
   - Just apply the updates AI agent specified

3. Validation ensures quality
   - Check updates improve accuracy/detail
   - No unnecessary rewording
   - Preserve tone and structure

4. Write back to content file
```

## Philosophy

**Before**: Python code tries to be smart with regex patterns  
**After**: AI agents are smart, Python code is simple plumbing

**Before**: Hard to add new pages (need new regex)  
**After**: Easy to add pages (just add metadata + agent instructions)

**Before**: Updates limited by what regex can do  
**After**: Updates limited only by AI capability

## 🚧 What's Next (In Order)

### 1. Update Agent Output Format (agents.yaml / tasks.yaml)
Agents need to output structured data instead of free text:
```yaml
section_updates:
  - section_title: "Reskill & adapt"
    updates:
      - type: "statistic"
        original: "83 million jobs"
        replacement: "85 million jobs"
        source: "https://weforum.org/..."
        confidence: 0.95
      - type: "detail_addition"
        location: "after paragraph 2"
        content: "Recent studies show..."
        source: "https://..."
        confidence: 0.85
```

### 2. Implement Structured Update Application
Update `content_update_applier.py` to:
- Parse structured updates from agent output
- Apply text replacements intelligently
- Handle additions/deletions safely
- Preserve markdown structure

### 3. Update/Remove Tests
- Delete tests for deleted strategy classes
- Add tests for new structured update flow
- Focus on end-to-end integration tests

### 4. Wire Into Main Workflow
- Ensure `automation_controller` calls `PageAutomationBridge.execute_automation()`
- Verify full workflow: research → structure → apply → validate → build

### 5. Test on One Page (action.md)
- Run complete workflow
- Verify updates are intelligent and preserve tone
- Validate no unnecessary rewording
- Check reference additions work

### 6. Scale to All Pages
- Add system instructions for each page type
- Test on technology, llm, society, privacy, economy
- Verify generalization works across different content types

## 📝 Files to Update Next

1. **tasks.yaml** - Add structured output format to agent tasks
2. **agents.yaml** - Update agent goals to emphasize structured output
3. **content_update_applier.py** - Implement structured update parsing/application
4. **tests/** - Update/remove strategy tests, add integration tests
