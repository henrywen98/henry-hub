# Plan Reflection Skill — Design Document

> Date: 2026-04-07
> Status: Draft — awaiting implementation plan
> Target plugin: `plugins/plan-reflection/` (new)

## Problem

When producing a plan for a non-trivial task, the author (human or AI) often
misses issues that a fresh reviewer would catch: internal contradictions,
missing edge cases, unrealistic steps, scope creep. Having a single agent
self-review its own plan rarely works — the reviewer and the author share the
same assumptions.

This skill implements a **multi-agent reflection loop**: an independent
Reviewer agent critiques the plan, a separate Corrector agent fixes the
blocking issues, and the loop repeats until the plan passes or hits a safety
limit. The user gets back a refined plan plus a full audit trail.

## Scope

### In Scope

- General-purpose review loop for any plan held in `~/.claude/plans/`
- Domain-adaptive review dimensions (technical, product, devops,
  architecture, general)
- Blocking-issue-driven termination (not score-driven)
- Hard cap of 3 rounds with convergence protection
- Returns a final audit report — user decides what to do next

### Out of Scope

- Reviewing plans stored outside `~/.claude/plans/`
- Reviewing arbitrary markdown files (use a different workflow)
- Auto-executing the plan after review passes
- Modifying files other than the plan itself
- Generating new plans from scratch (use `superpowers:writing-plans`)

## Architecture

### Execution Model: Dual-Agent Adversarial

Two specialized agents with strict role separation:

- **Reviewer Agent** — read-only. Produces a structured audit report with
  blocking issues and suggestions. Gives directional feedback only, not
  concrete rewrites.
- **Corrector Agent** — read + edit on the plan file only. Reads the plan
  and the reviewer's report, applies minimum-scope fixes to blocking issues,
  produces a correction report.

The skill's main process (the orchestrator) dispatches both agents but does
not read plan content into its own context. It only parses structured report
fields (verdict, issue counts) to drive the loop.

### Loop Flow

```
1. Read plan file metadata (path, mtime)
2. Detect plan domain from first 500 chars (orchestrator, no agent)
3. round := 1, max_rounds := 3

4. LOOP:
   a. Dispatch Reviewer Agent (background)
      inputs: plan path, domain, round number
      output: structured review report
   b. Parse report
      - if verdict = PASS → exit loop
      - if round >= max_rounds → exit loop
      - if round > 1 and current blocking count >= previous blocking count
        → exit loop (stalled — no progress)
   c. Dispatch Corrector Agent (background)
      inputs: plan path, review report, round number
      output: structured correction report
   d. round += 1
   e. goto a

5. Summarize all rounds, present final report to user
```

### Domain Detection (Orchestrator, In-Process)

The orchestrator reads the first 500 characters of the plan and classifies
it into one of five domains:

- `technical` — technical solution, architecture, code changes
- `product` — PRD, product requirements
- `devops` — deployment, operations, release
- `architecture` — system architecture, design documents
- `general` — fallback

This is a one-shot classification done without dispatching an agent
(input is small, output is a single label). The detected domain is reused
across all rounds.

## Component Design

### Reviewer Agent

**Role**: independent critic, read-only.

**Inputs**:
- Plan file path
- Detected domain
- Current round number

**Process**:
1. Read the plan file
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/plan-reflection/references/review-dimensions.md`
3. Apply domain-specific dimensions plus universal baseline checks
4. Output a report following the template in `report-templates.md`

**Universal Baseline Checks** (all domains):
1. Internal contradiction — do sections contradict each other?
2. Gaps — TBD, TODO, undefined critical details
3. Executability — are steps concrete enough to follow directly?
4. Scope creep — is there content beyond the stated goal?

**Domain-Specific Dimensions**:

| Domain | Core | Weighted |
|--------|------|----------|
| technical | Architecture soundness, edge cases, interface consistency | Performance, security |
| product | User value, acceptance criteria, priority | Feasibility, metrics |
| devops | Risk, rollback, monitoring | Dependencies, sequencing |
| architecture | Separation of concerns, extensibility, dependency direction | Complexity, consistency |
| general | Completeness, internal consistency, feasibility | Clarity, risk |

**Issue Classification**:
- **Blocking** — if not fixed, the plan cannot execute as intended, or will
  produce wrong results.
- **Suggestion** — improvement, but the plan still works without it.

**Hard Constraints**:
- No file modifications
- No concrete rewrites in the report (directional feedback only — that's
  corrector's job)
- Every issue must cite a specific location in the plan (section, paragraph,
  or quoted line)
- No vague praise or general commentary

### Corrector Agent

**Role**: minimal-scope fixer, read + edit on plan file only.

**Inputs**:
- Plan file path
- Full review report from the previous step
- Current round number

**Process**:
1. Read the plan file
2. For each blocking issue in the report:
   a. Locate the corresponding section/line in the plan
   b. Apply the minimum edit to resolve the issue
   c. Record `[FIXED]` or `[DEFERRED]` in the correction report
3. Output a correction report per `report-templates.md`

**Hard Constraints**:
- Only fixes blocking issues; suggestions are ignored
- Only edits the plan file; no other file modifications
- Minimum-scope edits only — no incidental refactoring
- If an issue requires substantial rewrite, mark it `[DEFERRED]` instead of
  acting on it
- One-to-one mapping: every blocking issue in the report must have a
  corresponding `[FIXED]` or `[DEFERRED]` entry

### Orchestrator (Main Skill Process)

**Role**: pure scheduler, no semantic judgment.

**Behavior**:
- Does not read plan content into its own context (only path + mtime)
- Dispatches both agents in the background (`run_in_background: true`)
- Parses structured fields from agent output only (verdict, counts)
- Does not modify any file
- Tracks round history for the final summary

## Report Templates

### Review Report

```markdown
## Review Report (Round N/3)

### Domain: <detected-domain>

### Blocking Issues
1. [BLOCKING] <short title>
   - Location: <section / paragraph / quoted line>
   - Problem: <what is wrong>
   - Suggestion: <direction for fix — not concrete text>

### Suggestions (Non-blocking)
1. [SUGGESTION] <short title>
   - Location: <...>
   - Problem: <...>
   - Suggestion: <...>

### Verdict: PASS | FAIL
- Blocking issues: N
- Suggestions: N
```

### Correction Report

```markdown
## Correction Report (Round N/3)

### Changes Made
1. [FIXED] <blocking issue title>
   - What changed: <concrete description of the edit>
   - Location: <where in the plan>

2. [DEFERRED] <blocking issue title>
   - Reason: <why this cannot be fixed at plan level; needs user decision>

### Summary
- Fixed: N
- Deferred: N
```

### Final Summary (to user)

```markdown
## Plan Reflection Complete

- Total rounds: N/3
- Final verdict: PASS | FAIL | STALLED
- Total issues fixed: N
- Deferred issues (need user decision): N

### Final Review Report
<last round's reviewer output in full>

### Round History
Round 1: 5 blocking → fixed 5
Round 2: 2 blocking → fixed 1, deferred 1
Round 3: 1 blocking → deferred 1

### Next Steps
<tailored to verdict>
```

## Termination Conditions

The loop exits on any of these conditions:

1. **PASS** — reviewer's verdict is PASS (zero blocking issues)
2. **Round cap** — `round >= 3`
3. **Stalled** — from round 2 onward, current blocking count is greater
   than or equal to the previous round's (no progress)
4. **Persistent DEFERRED** — the same issue is marked DEFERRED in two
   consecutive rounds (corrector cannot resolve it at plan level)
5. **Parse failure** — reviewer's report is unparseable twice in a row
   (first failure triggers a retry with "strict template" reminder)
6. **Agent dispatch failure** — any agent dispatch errors out (no auto-retry)

All exits produce a final summary; the skill does not loop past any of these.

## File Structure

```
plugins/plan-reflection/
├── .claude-plugin/
│   └── plugin.json           # name, version, description only
├── README.md                 # Chinese documentation
└── skills/
    └── plan-reflection/
        ├── SKILL.md          # Skill definition (orchestrator logic)
        └── references/
            ├── review-dimensions.md   # Domain-to-dimensions table
            └── report-templates.md    # Report format templates
```

**Why no `agents/` directory**: henry-hub's convention (observed across all
11 existing plugins) is to dispatch agents inline via the `Agent` tool with
`subagent_type: general-purpose` and role injection via prompt. This keeps
the plugin minimal and consistent with existing marketplace patterns.

## Edge Cases

1. **No active plan** — if `~/.claude/plans/` is empty or has no recently
   modified file, the skill exits with: "No active plan detected. Create
   one with `superpowers:writing-plans` first."

2. **Multiple candidate plans** — if multiple plan files exist, prompt the
   user to choose. Use most-recently-modified as the default hint.

3. **Tiny plan** (< 100 characters) — warn "plan may be too short for
   meaningful review" and ask the user to confirm before proceeding.

4. **Reviewer report unparseable** — retry once with an explicit reminder
   to follow the template. On second failure, exit the loop and return the
   raw agent output to the user.

5. **Deferred issue across rounds** — after each corrector run, compare
   `[DEFERRED]` issue titles against the previous round's deferred set. If
   any title appears in two consecutive correction reports, terminate early
   and flag in the summary: "persistent deferred issue requires user
   decision." Issue titles are matched case-insensitively with whitespace
   normalized.

6. **External modification** — check plan file mtime before each reviewer
   dispatch. If changed externally, warn the user and continue with the
   latest version.

7. **No progress** — starting from round 2, if the new round's blocking
   count is greater than or equal to the previous round's, terminate as
   "stalled — no progress." This covers both regression (count went up)
   and stagnation (count stayed the same).

8. **Agent dispatch error** — terminate immediately with the rounds
   completed so far. No auto-retry.

## Non-Goals (Explicit)

- **No scoring** — rejected in favor of binary blocking-count gating.
  Scores are too easy for agents to inflate.
- **No self-review** — rejected single-agent designs. Independence is the
  core value proposition.
- **No auto-execution** — the skill always hands back to the user after
  the loop. Executing the plan is a separate decision.
- **No cross-file edits** — the corrector touches only the plan file.
  Anything else belongs to implementation phase.

## Open Questions

None at this stage. All design decisions are settled; ready for
implementation planning.

## References

- Reflection Pattern (Andrew Ng's four agentic design patterns)
- LangGraph `reflect/revise` nodes
- CrewAI QA agent role
- Existing henry-hub agent dispatch patterns (drawio-diagram,
  concept-design, weekly-report, test-case-generator)
