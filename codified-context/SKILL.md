---
name: codified-context
description: Apply three-tier codified context architecture (constitution + specialist skills + subsystem specs with MCP retrieval) to any codebase. Based on arxiv.org/abs/2602.20478.
---

# Codified Context Infrastructure

## When to Use
When setting up or auditing AI-assisted development infrastructure for a codebase. Applies the three-tier architecture from "Codified Context: Infrastructure for AI Agents in a Complex Codebase" (arxiv.org/abs/2602.20478).

The paper demonstrates that structured project knowledge -- constitution, specialist agents, and subsystem specs -- substantially improves AI-generated code consistency across sessions. The approach works for any codebase above ~20K lines where multiple AI sessions touch the same code.

## The Three Tiers

### Tier 1: Constitution (CLAUDE.md / project instructions)
Hot memory loaded every session. Must stay under ~200 lines. Contains:
- **Orchestration trigger table**: file pattern -> skill -> spec mapping
- **Layer/architecture reference**: dependency hierarchy and rules
- **Operation checklists**: common task recipes (3-5 steps each)
- **Critical gotchas**: mistakes that recur across sessions

The constitution answers "where do I look?" -- not "how does it work?"

### Tier 2: Specialist Skills
Domain expert agents loaded on demand via slash commands or automatic triggers. Each covers one logical subsystem. Key ratio: >50% domain knowledge, <50% behavioral instructions.

Structure for each skill:
1. **Scope** -- which packages/files this covers
2. **Key Interfaces** -- methods, parameters, return types
3. **Architecture** -- data flow with code patterns
4. **Common Mistakes** -- domain-specific gotchas (superset of constitution)
5. **Testing Patterns** -- in-memory strategies, fixtures, what to assert
6. **Related Specs** -- which cold-memory specs to retrieve for deep context

### Tier 3: Subsystem Specs + MCP Retrieval
Cold memory retrieved via MCP tools when agents need deep context. Each spec covers one subsystem.
- Written for AI consumption: explicit file paths, code patterns, interface signatures
- NOT prose for humans -- structured data an agent can act on
- Retrieved via keyword search (the paper found simple substring matching sufficient)

## Process

### Step 1: Audit Existing Context
Read the current state of codified knowledge.

**Actions:**
- Read CLAUDE.md / project instructions and measure line count
- Inventory existing docs/, plans/, design decisions
- List any existing skills or agent configurations
- Count: how many lines of codified context vs lines of source code?

**Output:** A table like:

| Tier | Current state | Gap |
|------|--------------|-----|
| 1. Constitution | X-line CLAUDE.md, no orchestration | Need trigger table, checklists |
| 2. Skills | N generic skills, no domain skills | Need M domain skills |
| 3. Specs | N plan docs (session artifacts) | Need reusable specs + retrieval |

### Step 2: Analyze Codebase Structure
Identify the natural domain boundaries that will become skills and specs.

**Actions:**
- Map the package/module directory structure
- Identify layer hierarchy and dependency rules (which modules can import which)
- Group packages into logical subsystems (typically 5-10 domains)
- Count lines of code per subsystem to gauge complexity

**Heuristics for grouping:**
- Packages that share interfaces or data types belong together
- Packages that are always modified together belong together
- A subsystem should be large enough to justify a skill (~1K+ lines) but small enough to fit in one spec (~500 lines of documentation)

### Step 3: Identify Knowledge to Codify
Mine existing documentation for enduring architectural knowledge.

**Actions:**
- Read each existing design doc / plan / ADR
- Separate session artifacts (one-time implementation plans) from reusable knowledge (interface contracts, data flow patterns, gotchas)
- Catalog recurring mistakes from git history, bug reports, or existing gotcha lists
- Identify testing patterns: what in-memory substitutes exist, what fixtures are standard

**Key distinction:** Plans describe what was done and why. Specs describe how the system works now. Mine the former to create the latter.

### Step 4: Expand Constitution (Tier 1)
Grow the project instructions to serve as an orchestration hub.

**Add these sections:**

**4a. Orchestration Trigger Table**
Map file patterns to skills and specs so any session knows where to find domain knowledge:
```markdown
## Orchestration
| File pattern | Specialist skill | Cold memory spec |
|---|---|---|
| src/auth/*, src/middleware/auth* | project:auth | docs/specs/authentication.md |
| src/api/*, src/routes/* | project:api | docs/specs/api-layer.md |
```

**4b. Architecture / Layer Reference**
One-line-per-layer summary with dependency rules:
```markdown
## Layers
Layer 0 (Foundation): core, utils, types
Layer 1 (Data): models, storage, cache
Layer 2 (Services): auth, payments, notifications
Layer 3 (API): routes, controllers, serializers
Rule: packages import only from their layer or lower.
```

**4c. Operation Checklists**
3-5 step recipes for tasks that recur across sessions:
```markdown
## Common Operations
- **Adding a model**: define schema, create migration, add storage class, register in container, add API routes
- **Adding middleware**: implement interface, add discovery attribute, register in pipeline
```

**4d. Drift Warning**
Add to gotchas section:
```markdown
- When refactoring a subsystem, update the relevant docs/specs/ file. Stale specs cause agents to generate code conflicting with recent changes.
```

**Target:** ~150-200 lines total. If over 250, move content down to skills.

### Step 5: Create Domain Skills (Tier 2)
Write one skill per identified subsystem.

**For each subsystem, create `skills/<domain>/SKILL.md` with:**

```markdown
---
name: project:<domain>
description: <one sentence: when this skill triggers>
---
# <Domain> Specialist

## Scope
Packages: <list>
Key files: <list of entry points>

## Key Interfaces
<Interface/class name>
- <method signature with parameter types and return type>
- <behavioral contract: what callers must know>

## Architecture
<Data flow description with inline code patterns>
Example: "Request -> Middleware -> Controller -> Serializer. The controller
calls $storage->load($id) which returns Entity|null. Null triggers 404."

## Common Mistakes
- <Mistake>: <why it happens> -> <correct pattern>
- <Mistake>: <why it happens> -> <correct pattern>

## Testing Patterns
- <In-memory substitute>: use <class> instead of <real class>
- <Fixture pattern>: <how to set up test data>
- <What to assert>: <key assertions for this domain>

## Related Specs
- docs/specs/<spec>.md -- <what it covers>
```

**Quality check:** Read each skill and verify >50% of its lines are domain knowledge (interface signatures, code patterns, data flow) rather than instructions ("you should", "make sure to").

### Step 6: Write Subsystem Specs (Tier 3)
Write specs that encode deep implementation knowledge for MCP retrieval.

**For each subsystem, create `docs/specs/<subsystem>.md` with:**

```markdown
# <Subsystem> Specification

## File Map
| File | Purpose |
|------|---------|
| src/path/to/File.php | <one-line purpose> |

## Interface Signatures
<Full method signatures with types, grouped by interface>

## Data Flow
<Step-by-step flow for primary operations: create, read, update, delete>
<Include actual code patterns, not pseudocode>

## Storage / Schema
<Database tables, JSON structures, file formats>

## Configuration
<Config keys, environment variables, defaults>

## Edge Cases
<Boundary conditions, error handling, race conditions>
```

**Mining process:** For each existing design doc:
1. Extract interface signatures (these rarely change)
2. Extract data flow descriptions (update to match current implementation)
3. Extract gotchas and edge cases
4. Discard implementation timelines, phase breakdowns, task lists

### Step 7: Build MCP Retrieval Server
Scaffold a lightweight MCP server that exposes specs as searchable cold memory.

**Location:** `tools/spec-retrieval/` (standalone, not part of the main application)

**Three tools to implement:**

| Tool | Parameters | Returns |
|------|-----------|---------|
| `{project}_list_specs` | none | Markdown table of specs |
| `{project}_get_spec` | `name: string` | Full markdown content |
| `{project}_search_specs` | `query: string`, `max_results?: number` | Matching sections with context |

**Tool design principles** (AI selects tools based on descriptions, not names):

1. **Namespace tool names** with project prefix (e.g. `minoo_get_spec`, not `get_spec`) to avoid collisions with other MCP servers.

2. **Write actionable descriptions** that tell the AI when and why to use each tool:
   - Bad: "List specs"
   - Good: "List all subsystem specification documents. Use this to discover which specs are available before retrieving one."

3. **Describe parameters with examples**: `"Spec name without .md extension, e.g. 'entity-model', 'api-layer'"` — the AI needs format guidance to construct correct values.

4. **Return markdown, not JSON**: The AI reasons better about structured text (tables, headings) than nested JSON objects. Use markdown tables for listings, fenced code blocks for context snippets.

5. **Limit search results**: Cap matches per spec (default ~10) to prevent flooding the context window. Accept an optional `max_results` parameter.

6. **Return helpful errors**: On not-found, list available options so the AI can self-correct without a second tool call.

**Implementation:** ~100 lines in Node.js using `@modelcontextprotocol/sdk` with stdio transport. Reads markdown files from `docs/specs/`. Keyword substring matching is sufficient -- the paper found this outperformed more complex retrieval for structured specs.

**Configuration:** Add to `.claude/settings.json`:
```json
{
  "mcpServers": {
    "project-specs": {
      "command": "node",
      "args": ["tools/spec-retrieval/server.js"],
      "cwd": "."
    }
  }
}
```

### Step 8: GitHub Workflow Governance
Wire GitHub issue and milestone tracking into codified context so drift is caught at session start.

**8a. Drift-check script**
Create `bin/check-milestones` (bash, executable) that:
- Lists open issues with no milestone assigned (incomplete triage)
- Lists open milestones with zero open issues (possibly stale)
- Exits 0 always — output is a warning surface for Claude, not a CI gate

Uses `gh api` for queries. Hardcode the repo slug (e.g. `owner/repo`).

**8b. SessionStart hook**
Add to `.claude/settings.json` (committed, not `.local.json`):
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bin/check-milestones",
            "show_output": true
          }
        ]
      }
    ]
  }
}
```

**8c. Workflow spec (`docs/specs/workflow.md`)**
Create a spec containing:
- Versioning model for this repo (and any sibling repos)
- Current milestone list with descriptions and statuses
- The 5 workflow rules (see below)
- Instructions for keeping the spec updated when milestones change

Add to the orchestration table: `| GitHub issues, milestones, new features, roadmap | — | docs/specs/workflow.md |`

**8d. CLAUDE.md GitHub Workflow section**
Add a "GitHub Workflow" section summarizing the 5 rules and pointing to `docs/specs/workflow.md`.

**8e. PR template (`.github/pull_request_template.md`)**
```markdown
Closes #

## Summary


## Checklist

- [ ] `Closes #N` above references the issue this PR resolves
- [ ] The issue is assigned to a milestone
- [ ] PR title includes the issue number (e.g. `feat(#42): description`)
```

**The 5 workflow rules (codify in CLAUDE.md and workflow spec):**
1. All work begins with an issue — ask for issue number before writing code, create one if missing
2. Every issue belongs to a milestone — unassigned issues are incomplete triage
3. Milestones define the roadmap — check active milestone before proposing work, don't invent new ones without discussion
4. PRs must reference issues — title format `feat(#N): description`
5. Claude reads the drift report — flag `bin/check-milestones` warnings before beginning work

### Step 9: Set Up Maintenance
Prevent the #1 failure mode: stale specs.

**8a. Drift Detection Script**
Create `tools/drift-detector.sh` that maps recent file changes to affected specs:
```
$ tools/drift-detector.sh
Files changed in last 5 commits:
  src/api/controllers/UserController.ts -> docs/specs/api-layer.md
  src/auth/middleware.ts -> docs/specs/authentication.md
Warning: 2 specs may need review.
```

Build a mapping from file path patterns to spec files (same patterns as the orchestration trigger table).

**9b. Session Discipline**
After any session that changes a subsystem's behavior:
1. Update constitution if gotchas changed
2. Update relevant `docs/specs/` file if interfaces or data flow changed
3. Run drift detector to catch anything missed

**9c. Maintenance Cadence**
- Per-session: update affected specs (~5 min when needed)
- Biweekly: run drift detector, review flagged specs (~30 min)
- Quarterly: audit coverage -- are new subsystems missing specs?

## Quality Checklist
- [ ] Constitution is under 200 lines (fits comfortably in hot memory)
- [ ] Orchestration table covers all active packages/modules
- [ ] Orchestration table has a row for `GitHub issues, milestones, new features, roadmap → docs/specs/workflow.md`
- [ ] Every skill has >50% domain knowledge content (not just instructions)
- [ ] Every spec has explicit file paths, not vague descriptions
- [ ] Every spec has full interface signatures with types
- [ ] MCP tool descriptions explain when and why to use each tool (not just what it does)
- [ ] MCP tools return markdown (tables, headings) not raw JSON
- [ ] MCP search results are capped to prevent context window flooding
- [ ] MCP error responses include available options for self-correction
- [ ] MCP tool names are namespaced with project prefix
- [ ] Drift detector maps all active packages to specs
- [ ] No circular references between tiers (constitution -> skills -> specs)
- [ ] Operation checklists cover the 4-5 most common tasks
- [ ] `bin/check-milestones` script exists and is executable
- [ ] `.claude/settings.json` has SessionStart hook running `bin/check-milestones`
- [ ] `docs/specs/workflow.md` exists with versioning model, milestone list, and 5 workflow rules
- [ ] CLAUDE.md has "GitHub Workflow" section with 5 rules and pointer to workflow spec
- [ ] `.github/pull_request_template.md` exists with issue reference checklist

## Anti-Patterns to Avoid
- **Bloated constitution**: Over 300 lines defeats the hot-memory purpose. Move detail to skills.
- **Instruction-heavy skills**: Skills that are mostly "you should" with little domain knowledge. Flip the ratio.
- **Intent-based specs**: Specs that describe what the system should do instead of how it works now. Include code patterns, not aspirations.
- **Volatile specs**: Specs for subsystems changing daily. Wait until interfaces stabilize.
- **Complex retrieval**: MCP server with embeddings, vector DBs, or external dependencies. Keyword substring search on structured specs works.
- **Orphan specs**: Specs not referenced by any skill or trigger table entry. Every spec must be reachable.
- **Generic tool descriptions**: The AI selects tools by description, not name. "List specs" tells it nothing. "List all subsystem specs to discover what's available before retrieving one" guides correct usage.
- **JSON dumps as tool output**: Return markdown tables and structured text. The AI reasons about formatted text better than deeply nested JSON.
- **Unbounded search results**: Always cap matches to prevent flooding the context window. The AI can refine its query if needed.

## Metrics
- **Knowledge-to-code ratio**: (lines of codified context / lines of source code). Target >5%.
- **Spec coverage**: percentage of packages/modules covered by at least one spec.
- **Spec staleness**: run drift detector weekly. Flag specs not updated in 30+ days if their packages changed.
- **Session quality**: agents should find correct interfaces without exploring source files. Test by starting a fresh session and asking about a subsystem.

