# Plan Reflection Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `plan-reflection` plugin in henry-hub that runs a multi-agent reflection loop on plans in `~/.claude/plans/`, dispatching independent reviewer + corrector agents until pass / round cap / convergence failure, then returns an audit report to the user.

**Architecture:** Single skill (`plan-reflection`) acts as orchestrator. Two ad-hoc agents are dispatched inline via the `Agent` tool with `subagent_type: general-purpose` and role injected through prompt — matching henry-hub's existing pattern (no `agents/` directory). Two reference files (`review-dimensions.md`, `report-templates.md`) hold the domain dimensions table and report templates the agents load at runtime.

**Tech Stack:** Pure markdown plugin — no code, no Python, no dependencies. Uses Claude Code's auto-discovery for skill registration. References resolve via `${CLAUDE_PLUGIN_ROOT}`.

**Spec:** `docs/plans/2026-04-07-plan-reflection-design.md`

---

## File Structure

Files this plan creates or modifies:

| Path | Action | Responsibility |
|------|--------|----------------|
| `plugins/plan-reflection/.claude-plugin/plugin.json` | Create | Plugin manifest (name/version/description only — no component arrays) |
| `plugins/plan-reflection/skills/plan-reflection/SKILL.md` | Create | Orchestrator instructions: discover plan, detect domain, run reflection loop, dispatch agents, summarize |
| `plugins/plan-reflection/skills/plan-reflection/references/review-dimensions.md` | Create | Domain → review-dimensions table + universal baseline checks (loaded by reviewer agent) |
| `plugins/plan-reflection/skills/plan-reflection/references/report-templates.md` | Create | Three report templates: review report, correction report, final summary |
| `plugins/plan-reflection/README.md` | Create | Chinese plugin documentation (per henry-hub convention) |
| `.claude-plugin/marketplace.json` | Modify | Append `plan-reflection` entry to plugins array |
| `README.md` | Modify | Add plugin to a category table |
| `CLAUDE.md` | Modify | Bump version line + add `plan-reflection` to categories table |

---

## Task 1: Scaffold the plugin manifest

**Files:**
- Create: `plugins/plan-reflection/.claude-plugin/plugin.json`

- [ ] **Step 1: Create the manifest file**

Write `plugins/plan-reflection/.claude-plugin/plugin.json` with this exact content:

```json
{
  "name": "plan-reflection",
  "version": "0.1.0",
  "description": "Multi-agent reflection loop for plans in ~/.claude/plans/. Independent reviewer agent finds blocking issues, separate corrector agent fixes them, loops up to 3 rounds with convergence protection."
}
```

Critical constraints (per `CLAUDE.md`):
- Only `name`, `version`, `description` — do NOT add `skills`, `commands`, `agents`, or `hooks` arrays. Auto-discovery handles those.
- Plugin name uses kebab-case.

- [ ] **Step 2: Verify the file is valid JSON**

Run:

```bash
python3 -m json.tool plugins/plan-reflection/.claude-plugin/plugin.json
```

Expected: pretty-printed JSON, no error.

- [ ] **Step 3: Verify directory structure exists**

Run:

```bash
ls -la plugins/plan-reflection/.claude-plugin/
```

Expected: shows `plugin.json`.

---

## Task 2: Write `references/review-dimensions.md`

**Files:**
- Create: `plugins/plan-reflection/skills/plan-reflection/references/review-dimensions.md`

This file is loaded by the reviewer agent at runtime. It must be self-contained and unambiguous because the reviewer is a fresh sub-agent with no project context.

- [ ] **Step 1: Create the file**

Write `plugins/plan-reflection/skills/plan-reflection/references/review-dimensions.md` with this exact content:

````markdown
# Review Dimensions

This file is loaded by the **Plan Reviewer Agent** during a `plan-reflection` run. It defines what to look for when auditing a plan.

## How to Use This File

1. The orchestrator passes you a `domain` value: one of `technical`, `product`, `devops`, `architecture`, or `general`.
2. Apply the **Universal Baseline Checks** to every plan regardless of domain.
3. Then apply the **domain-specific dimensions** for the passed domain.
4. Every issue you raise must cite a specific location in the plan (section heading, paragraph, or quoted line). Vague critiques are useless.

## Universal Baseline Checks

All plans, all domains, every round:

1. **Internal contradiction** — do different sections of the plan contradict each other? (e.g. one section says "use X", another assumes "Y is in place")
2. **Gaps** — are there any `TBD`, `TODO`, "fill in later", incomplete sections, or critical details that are referenced but never defined?
3. **Executability** — are the steps concrete enough to follow directly? "Add appropriate validation" is NOT executable. "Validate that input matches `^\d{4}-\d{2}-\d{2}$`" is.
4. **Scope creep** — does the plan include work beyond the stated goal? Stated as separate items, not buried inside other work.

## Domain-Specific Dimensions

| Domain | Core Dimensions | Weighted Dimensions |
|--------|----------------|---------------------|
| `technical` | Architecture soundness, edge cases, interface consistency | Performance impact, security implications |
| `product` | User value, acceptance criteria clarity, priority justification | Feasibility, success metrics |
| `devops` | Risk assessment, rollback plan, monitoring/alerting | Dependencies, sequencing, blast radius |
| `architecture` | Separation of concerns, extensibility, dependency direction | Complexity budget, consistency with existing patterns |
| `general` | Completeness, internal consistency, feasibility | Clarity, risk |

### Domain Dimension Details

**`technical` — code, modules, API design, refactors:**
- Architecture soundness: are the proposed structures correct? Do data flows make sense?
- Edge cases: empty input, max-size input, malformed input, concurrent access, partial failures
- Interface consistency: do function signatures, types, and naming line up between sections?
- Performance impact: anything obviously O(n²) or N+1? Any unbounded loops?
- Security implications: input validation, authentication boundaries, secret handling

**`product` — PRDs, feature specs, product requirements:**
- User value: who benefits, how, by how much? Stated in user terms not feature terms.
- Acceptance criteria clarity: can a tester verify "done"? Is each criterion checkable?
- Priority justification: if features are listed, is priority order justified by impact/effort?
- Feasibility: are estimates plausible? Are dependencies acknowledged?
- Success metrics: how will success be measured post-launch?

**`devops` — deployment, operations, releases, infra:**
- Risk assessment: what's the worst-case failure mode? Who is impacted?
- Rollback plan: is there a documented way to undo this? Tested?
- Monitoring/alerting: how will you know if it's working? Failing?
- Dependencies: order-of-operations, external service dependencies, downstream consumers
- Blast radius: if this fails, what else fails?

**`architecture` — system design, module boundaries, large refactors:**
- Separation of concerns: does each component have one clear responsibility?
- Extensibility: how does the design handle the next likely change?
- Dependency direction: are dependencies pointing the right way (no cycles)?
- Complexity budget: is the abstraction earning its complexity cost?
- Consistency with existing patterns: does it match what already exists, or break convention with justification?

**`general` — fallback, mixed-content plans:**
- Completeness: does the plan cover everything the goal requires?
- Internal consistency: do the sections agree with each other?
- Feasibility: can this plausibly be done as written?
- Clarity: would a fresh reader understand it?
- Risk: what could go wrong? Is mitigation included?

## Issue Severity

Every issue you raise must be classified as one of:

- **`[BLOCKING]`** — if not fixed, the plan cannot execute as intended OR will produce wrong results. Examples: missing critical step, contradictory specs, undefined terms used in later sections, infeasible dependencies, unsafe operations without mitigation.
- **`[SUGGESTION]`** — improvement, but the plan still works without it. Examples: clearer wording, better organization, optional extra checks, documentation polish.

When in doubt, classify as `[SUGGESTION]`. Reserve `[BLOCKING]` for issues that would actually break execution.

## Hard Constraints (Reviewer Boundaries)

These are non-negotiable:

1. **No file modifications.** You are read-only. Do not edit, create, or delete any file.
2. **No concrete rewrites.** Your suggestions are directional only — describe *what direction* the fix should go, not the literal text the corrector should write. Example: "Section 3 needs a rollback step that addresses X" — yes. "Change line 47 to read `git revert HEAD`" — no.
3. **Cite locations.** Every issue must point to a specific location in the plan (section name, paragraph, or quoted line). "Plan is unclear" with no location is rejected.
4. **No vague praise or general commentary.** Don't write "overall this looks good but..." — go directly to issues.
5. **Output strictly per the template.** The orchestrator parses your output programmatically. Deviate from the template and the parse fails. See `report-templates.md`.
````

- [ ] **Step 2: Verify the file is readable and not empty**

Run:

```bash
wc -l plugins/plan-reflection/skills/plan-reflection/references/review-dimensions.md
```

Expected: at least 60 lines.

- [ ] **Step 3: Spot-check the domain table renders**

Run:

```bash
grep -A 6 "Domain-Specific Dimensions" plugins/plan-reflection/skills/plan-reflection/references/review-dimensions.md | head -10
```

Expected: see the table header and at least 2 domain rows.

---

## Task 3: Write `references/report-templates.md`

**Files:**
- Create: `plugins/plan-reflection/skills/plan-reflection/references/report-templates.md`

This file is loaded by both the reviewer and corrector agents. It defines the exact output format the orchestrator parses. Any deviation from these templates breaks the loop.

- [ ] **Step 1: Create the file**

Write `plugins/plan-reflection/skills/plan-reflection/references/report-templates.md` with this exact content:

````markdown
# Report Templates

The orchestrator parses agent output programmatically. **Every agent MUST output exactly this format.** Any deviation breaks the reflection loop.

The orchestrator parses:
- Reviewer output: domain line, blocking issue count, suggestion count, verdict
- Corrector output: fixed count, deferred count, deferred issue titles (for cross-round comparison)

## Reviewer Report Template

When you are dispatched as the **Plan Reviewer**, output exactly this format. Replace `<placeholders>` with your content. Use the literal section headers shown.

````markdown
## Review Report (Round N/3)

### Domain: <detected-domain>

### Blocking Issues
1. [BLOCKING] <short title — under 80 characters>
   - Location: <section heading, paragraph reference, or quoted line>
   - Problem: <what is wrong, in 1-2 sentences>
   - Suggestion: <directional fix — what the corrector should aim for, NOT the literal replacement text>

2. [BLOCKING] <next blocking issue, same structure>
   ...

### Suggestions (Non-blocking)
1. [SUGGESTION] <short title>
   - Location: <...>
   - Problem: <...>
   - Suggestion: <...>

### Verdict: PASS
- Blocking issues: 0
- Suggestions: N
````

OR if there are blocking issues:

````markdown
### Verdict: FAIL
- Blocking issues: N
- Suggestions: M
````

**Reviewer rules:**

- Replace `Round N/3` with the actual round number (e.g. `Round 1/3`).
- Replace `<detected-domain>` with the exact domain string passed by the orchestrator (`technical`, `product`, `devops`, `architecture`, or `general`).
- If there are no blocking issues, write `### Blocking Issues` followed by `(none)` on the next line. Do not omit the section.
- If there are no suggestions, write `### Suggestions (Non-blocking)` followed by `(none)`. Do not omit the section.
- Verdict is `PASS` if and only if blocking count is 0. Otherwise `FAIL`.
- The two count lines under Verdict must match the actual numbers above.
- Every issue title must be unique within the same report (the orchestrator uses titles to track persistent DEFERRED across rounds — so duplicates within a single report break the bookkeeping).

## Corrector Report Template

When you are dispatched as the **Plan Corrector**, output exactly this format:

````markdown
## Correction Report (Round N/3)

### Changes Made
1. [FIXED] <blocking issue title — must match reviewer's title verbatim>
   - What changed: <concrete description of the edit you made — file location + summary of change>
   - Location: <section heading or line reference in the plan>

2. [DEFERRED] <blocking issue title — must match reviewer's title verbatim>
   - Reason: <why this cannot be resolved at the plan level — needs user decision, requires substantial rewrite, contradicts another constraint, etc.>

### Summary
- Fixed: N
- Deferred: M
````

**Corrector rules:**

- Replace `Round N/3` with the actual round number.
- Every blocking issue from the reviewer's report must appear in your Changes Made list, classified as either `[FIXED]` or `[DEFERRED]`. One-to-one mapping is mandatory.
- Issue titles must match the reviewer's titles **verbatim** (case-sensitive, exact whitespace) — the orchestrator compares them across rounds to detect persistent deferreds.
- Suggestions (non-blocking) are ignored. Do not address them.
- The Summary counts must match the lists above.
- Do not invent new issues. Do not split or merge issues from the reviewer's report.

## Final Summary Template (Orchestrator → User)

When the orchestrator finishes the loop, it shows the user this:

````markdown
## Plan Reflection Complete

- **Plan file:** `<path>`
- **Total rounds:** N/3
- **Final verdict:** PASS | FAIL | STALLED
- **Total blocking issues fixed:** N
- **Deferred issues (need user decision):** M
- **Termination reason:** <one of: PASS, round-cap, stalled-no-progress, persistent-deferred, parse-failure, dispatch-failure>

### Round History

| Round | Blocking In | Fixed | Deferred |
|-------|------------|-------|----------|
| 1 | 5 | 5 | 0 |
| 2 | 2 | 1 | 1 |
| 3 | 1 | 0 | 1 |

### Final Review Report

<verbatim copy of the last reviewer's report>

### Deferred Issues (if any)

For each deferred issue across all rounds, list:
- **Title**
- **Round first deferred**
- **Reason** (from the corrector's report)

### Next Steps

- If `PASS`: "Plan審核通過，可以開始實施。"
- If `FAIL` (round-cap reached): "Reached the 3-round cap with N blocking issues remaining. Recommend: review the deferred issues manually and decide whether to revise the plan or accept residual risk."
- If `STALLED`: "Loop stopped because the corrector did not make progress. Recommend: the plan likely has structural issues that need human revision before further review."
- If `PARSE-FAILURE` or `DISPATCH-FAILURE`: "Loop terminated due to a technical issue. Raw agent outputs are available above for inspection."
````
````

- [ ] **Step 2: Verify the file**

Run:

```bash
wc -l plugins/plan-reflection/skills/plan-reflection/references/report-templates.md
```

Expected: at least 70 lines.

- [ ] **Step 3: Verify the three template sections exist**

Run:

```bash
grep "^## " plugins/plan-reflection/skills/plan-reflection/references/report-templates.md
```

Expected output:
```
## Reviewer Report Template
## Corrector Report Template
## Final Summary Template (Orchestrator → User)
```

---

## Task 4: Write the SKILL.md (orchestrator)

**Files:**
- Create: `plugins/plan-reflection/skills/plan-reflection/SKILL.md`

This is the heaviest file. It defines how the main session acts as orchestrator: discovers the plan, detects domain, runs the loop, dispatches agents with role-injection prompts, parses reports, and presents the final summary.

- [ ] **Step 1: Create the file**

Write `plugins/plan-reflection/skills/plan-reflection/SKILL.md` with this exact content:

````markdown
---
name: plan-reflection
description: >-
  Multi-agent reflection loop for reviewing plans in ~/.claude/plans/. Use when the user says
  "审核计划", "review plan", "review my plan", "帮我审一下方案", "多轮审核", "计划评审",
  "adversarial review", "critique this plan", or wants an independent reviewer to find issues
  in a plan they've already written. Independent Reviewer agent finds blocking issues, separate
  Corrector agent fixes them, loops up to 3 rounds with convergence protection. Returns an audit
  report — does not auto-execute the plan.

  Not for: generating new plans (use superpowers:writing-plans), reviewing code (use code-reviewer
  agents), or reviewing arbitrary markdown files outside ~/.claude/plans/.
---

# Plan Reflection — Multi-Agent Plan Review Loop

Run a dual-agent reflection loop on a plan in `~/.claude/plans/`. An independent **Reviewer Agent** finds blocking issues, a separate **Corrector Agent** fixes them, repeating up to 3 rounds. Returns a final audit report — never auto-executes the plan.

**You (the main session) are the orchestrator.** Your job is to schedule agents and parse their reports. You do NOT read plan content into your own context. You do NOT make semantic judgments about the plan. You do NOT modify any files.

## Phase 0: Find the Active Plan

1. Run `ls -t ~/.claude/plans/*.md 2>/dev/null` (newest first).
2. **No files found** → tell the user: "No active plan detected in `~/.claude/plans/`. Create one with `superpowers:writing-plans` first." Stop.
3. **Exactly one file** → use it. Note its path and `mtime` (you'll re-check `mtime` before each reviewer dispatch).
4. **Multiple files** → show the user the top 5 (by mtime) and ask which to review. Use `AskUserQuestion` if available, otherwise list them and wait for a number.
5. Run `wc -c "<plan_path>"` to get byte count. If under 100 bytes, warn: "Plan is very short ({N} bytes) — review may have limited value. Continue anyway? (yes/no)" and wait for confirmation.

Once you have a confirmed `plan_path`, record:
- `plan_path` — absolute path to the plan file
- `plan_mtime_initial` — current mtime (run `stat -f "%m" "<plan_path>"` on macOS or `stat -c "%Y" "<plan_path>"` on Linux)

## Phase 1: Detect Domain

Read **only the first 500 characters** of the plan file using `head -c 500 "<plan_path>"`. Do NOT read the whole file — that pollutes your orchestrator context.

Based on the title and opening content, classify into exactly one of:

| Domain | Signals |
|--------|---------|
| `technical` | code, modules, API, refactor, function, class, type, interface, library, dependency |
| `product` | PRD, user, feature, requirement, acceptance, value, persona, market |
| `devops` | deploy, release, rollback, infra, CI/CD, monitoring, alerting, incident, ops |
| `architecture` | system, design, boundary, layer, component, separation, extensibility, dependency direction |
| `general` | (fallback) anything that doesn't clearly match the above, or a mix |

Record this as `domain`. **You will reuse this value for every round** — do not re-detect.

## Phase 2: Initialize Loop State

Initialize these orchestrator variables. You will track them across all rounds:

- `round = 1`
- `max_rounds = 3`
- `previous_blocking_count = null` (set after round 1)
- `previous_deferred_titles = []` (set of titles deferred in the previous round; starts empty)
- `round_history = []` (list of `{round, blocking_in, fixed, deferred}` records, for the final summary)
- `all_deferred = []` (accumulated deferred issues across all rounds, for the final summary)
- `last_review_report = null` (verbatim text of the most recent reviewer output)
- `termination_reason = null`

## Phase 3: Reflection Loop

Repeat until termination. Each iteration is one round.

### Step 3a: Stale-mtime Check

Before each reviewer dispatch, re-read the plan file mtime:

```bash
stat -f "%m" "<plan_path>"   # macOS
# or
stat -c "%Y" "<plan_path>"   # Linux
```

If the value differs from `plan_mtime_initial` AND this is round 1 → benign (corrector hasn't run yet, but a human edited it). Update `plan_mtime_initial` and continue.

If it differs in round ≥ 2 → check: was this our corrector's edit (expected) or external (unexpected)? You can't tell directly, but you know the corrector ran in the previous step. So: if round > 1, accept the new mtime as expected and update `plan_mtime_initial`. Add a note to the final summary: "Plan was modified during the loop (expected from corrector)."

### Step 3b: Dispatch the Reviewer Agent

Use the `Agent` tool with `subagent_type: general-purpose`. Run in background (`run_in_background: true`) so your orchestrator context stays unblocked while the agent works.

**Reviewer prompt template** (substitute placeholders):

```
You are the Plan Reviewer for round <ROUND>/3 of a multi-agent plan reflection loop.

ROLE BOUNDARIES (non-negotiable):
- READ-ONLY. You must not modify, create, or delete any file.
- DIRECTIONAL FEEDBACK ONLY. Do not write the literal replacement text — describe the direction the fix should go. The corrector will handle the actual edits.
- INDEPENDENT JUDGMENT. Do not assume the plan author had good reasons for unclear sections. If something looks wrong, flag it.

YOUR TASK:
1. Read the plan file at: <PLAN_PATH>
2. Read the review dimensions reference: ${CLAUDE_PLUGIN_ROOT}/skills/plan-reflection/references/review-dimensions.md
3. Read the report template reference: ${CLAUDE_PLUGIN_ROOT}/skills/plan-reflection/references/report-templates.md
4. Apply the universal baseline checks AND the dimensions for domain: <DOMAIN>
5. Output a Review Report following the EXACT template in report-templates.md

CRITICAL OUTPUT REQUIREMENTS:
- Use the literal section headers from the template ("## Review Report (Round N/3)", "### Domain:", "### Blocking Issues", "### Suggestions (Non-blocking)", "### Verdict: PASS|FAIL").
- Replace "Round N/3" with "Round <ROUND>/3".
- Replace "<detected-domain>" with: <DOMAIN>
- Verdict is PASS if and only if there are zero blocking issues.
- Every issue must cite a specific location in the plan (section heading, paragraph, or quoted line).
- Every issue title must be unique within this report.
- The orchestrator parses your output programmatically. Strict template adherence is mandatory.

Output the Review Report and nothing else. No preamble, no commentary outside the template.
```

Wait for the agent to complete. Capture its full output as `current_review_report`.

### Step 3c: Parse the Reviewer Report

Extract these fields from `current_review_report` and bind them to local variables for use in later steps:

1. **`verdict`** — search for the line `### Verdict: PASS` or `### Verdict: FAIL`. Capture the literal value (`"PASS"` or `"FAIL"`).
2. **`blocking_count`** — search for the line `- Blocking issues: N` directly under the verdict. Capture N as integer.
3. **`suggestion_count`** — search for the line `- Suggestions: N`. Capture N as integer.
4. **`blocking_titles`** — extract each `[BLOCKING] <title>` line from the `### Blocking Issues` section as a list of title strings.

**Parse failure handling:** If you cannot find the verdict line, OR cannot extract the blocking count, this is a parse failure.

- **First parse failure** → re-dispatch the reviewer with this addition to the prompt: "PRIOR ATTEMPT FAILED to follow the template. Output STRICTLY per the template in report-templates.md. The first three lines of your response must be `## Review Report (Round N/3)`, blank line, `### Domain: <domain>`."
- **Second consecutive parse failure** → set `termination_reason = "parse-failure"`, save `current_review_report` raw, exit the loop, go to Phase 4.

Once parsed successfully, save `current_review_report` as `last_review_report`.

### Step 3d: Check Termination Conditions (Pre-Corrector)

In order:

1. **PASS** — if `verdict == "PASS"`:
   - Set `termination_reason = "PASS"`.
   - Append to `round_history`: `{round: <ROUND>, blocking_in: 0, fixed: 0, deferred: 0}`.
   - (Nothing to append to `all_deferred` — there were no issues this round.)
   - Exit loop, go to Phase 4.

2. **Stalled (no progress)** — if `round > 1` AND `blocking_count >= previous_blocking_count`:
   - Set `termination_reason = "stalled-no-progress"`.
   - Append to `round_history`: `{round: <ROUND>, blocking_in: <blocking_count>, fixed: 0, deferred: 0}` (corrector did not run this round).
   - Exit loop, go to Phase 4.

3. **Round cap** — if `round >= max_rounds`: do NOT exit yet — let the corrector run one more time so the user gets the final state. Mark a local flag `round_cap_triggered = true`. After the corrector runs and Phase 3h appends history, set `termination_reason = "round-cap"` and exit.

If none of the above triggers exit, proceed to step 3e.

### Step 3e: Dispatch the Corrector Agent

Use `Agent` tool with `subagent_type: general-purpose`, `run_in_background: true`.

**Corrector prompt template:**

```
You are the Plan Corrector for round <ROUND>/3 of a multi-agent plan reflection loop.

ROLE BOUNDARIES (non-negotiable):
- You may ONLY edit the plan file at: <PLAN_PATH>
- You must NOT modify any other file.
- You must NOT create or delete files.
- You must NOT address suggestions (non-blocking) — only blocking issues.
- MINIMUM-SCOPE EDITS only. Do not refactor adjacent text. Do not "improve" sections that are not flagged.
- If a blocking issue requires substantial rewrite or contradicts another constraint, mark it [DEFERRED] instead of acting on it. The user will decide later.

YOUR INPUT:
- Plan file: <PLAN_PATH>
- Reviewer report (the blocking issues you must address):

<REVIEW_REPORT>

YOUR TASK:
1. Read the plan file with the Read tool.
2. Read the report template reference: ${CLAUDE_PLUGIN_ROOT}/skills/plan-reflection/references/report-templates.md
3. For each [BLOCKING] issue in the reviewer's report:
   a. Locate the corresponding section/line in the plan.
   b. Apply the minimum edit (using the Edit tool) to resolve the issue, OR mark it [DEFERRED] if it cannot be resolved at the plan level.
4. Output a Correction Report following the EXACT template in report-templates.md.

CRITICAL OUTPUT REQUIREMENTS:
- Use the literal section headers from the template.
- Replace "Round N/3" with "Round <ROUND>/3".
- Every blocking issue from the reviewer's report must appear in your Changes Made list as [FIXED] or [DEFERRED] — one-to-one mapping.
- Issue titles must match the reviewer's titles VERBATIM (exact case, exact whitespace). The orchestrator compares titles across rounds.
- The Summary counts must match the actual entries above.

Output the Correction Report and nothing else. No preamble.
```

Wait for completion. Capture full output as `current_correction_report`.

### Step 3f: Parse the Corrector Report

Extract these fields from `current_correction_report` and bind to local variables:
1. **`fixed_count`** — from `- Fixed: N` (integer)
2. **`deferred_count`** — from `- Deferred: N` (integer)
3. **`fixed_titles`** — every `[FIXED] <title>` line in `### Changes Made` as a list of strings
4. **`deferred_titles`** — every `[DEFERRED] <title>` line in `### Changes Made` as a list of strings (each entry should also retain the associated `Reason` text for `all_deferred` bookkeeping)

Normalize all titles for comparison: lowercase, collapse internal whitespace to single space, trim. Use the normalized form when comparing across rounds; preserve the original form when displaying to the user.

### Step 3g: Check Persistent Deferred

Compare normalized `deferred_titles` against `previous_deferred_titles`:

- If `round >= 2` AND any title appears in both sets:
  - Set `termination_reason = "persistent-deferred"`.
  - Append to `round_history`: `{round: <ROUND>, blocking_in: <blocking_count>, fixed: <fixed_count>, deferred: <deferred_count>}`.
  - Append every deferred issue from this round to `all_deferred` (record `{title, round: <ROUND>, reason}`).
  - Exit loop, go to Phase 4.

Otherwise, set `previous_deferred_titles = deferred_titles` for the next round.

### Step 3h: Record Round History and Increment

Append to `round_history`:
```
{
  round: <ROUND>,
  blocking_in: <blocking_count>,
  fixed: <fixed_count>,
  deferred: <deferred_count>
}
```

Append all deferred issues from this round to `all_deferred` (record title, round, reason).

Set `previous_blocking_count = blocking_count`.

If `round_cap_triggered == true` (set in step 3d) → set `termination_reason = "round-cap"`, exit loop, go to Phase 4.

Otherwise, increment `round += 1` and go back to step 3a.

## Phase 4: Present Final Summary

Build the final summary using the template in `report-templates.md` (Final Summary Template section). Substitute:

- `<path>` → `plan_path`
- `Total rounds` → highest round number reached
- `Final verdict` → derived from `termination_reason`:
  - `"PASS"` → verdict `PASS`
  - `"round-cap"` → verdict `FAIL`
  - `"stalled-no-progress"` → verdict `STALLED`
  - `"persistent-deferred"` → verdict `STALLED`
  - `"parse-failure"` → verdict `FAIL` (with note)
  - `"dispatch-failure"` → verdict `FAIL` (with note)
- `Total blocking issues fixed` → sum of `fixed` across all rounds in `round_history`
- `Deferred issues` → length of `all_deferred`
- `Termination reason` → the raw `termination_reason` value
- Round History table → from `round_history`
- Final Review Report → verbatim `last_review_report`
- Deferred Issues section → expand `all_deferred` (one entry per item)
- Next Steps → use the canned text for the matching verdict from the Final Summary Template

Show this entire summary to the user as your final response. **Do not** automatically dispatch any other skill. The user decides what to do next.

## Error Handling

These are the only termination paths. If anything else goes wrong:

- **Agent dispatch fails** (Agent tool errors out before agent starts) → set `termination_reason = "dispatch-failure"`, exit loop, go to Phase 4. No retry.
- **Agent never returns** (timeout or hang) → same handling as dispatch failure.
- **Reviewer parse fails twice consecutively** → set `termination_reason = "parse-failure"`, exit loop. The raw failed reports are included in the final summary.
- **Plan file disappears mid-loop** → if a `Read` of `plan_path` fails inside an agent, the agent will report an error. Treat as dispatch failure.

Do NOT auto-retry. Do NOT silently swallow errors. The user must always see the final summary, even if the loop terminated early.

## Hard Boundaries (Orchestrator)

These are non-negotiable:

- You do NOT read the plan content into your own context. The most you read is the first 500 chars for domain detection in Phase 1. After that, the plan is a path you pass to agents.
- You do NOT make semantic judgments about the plan. Your decisions are based only on structured fields (verdict, counts, titles) parsed from agent reports.
- You do NOT modify any file. Only the corrector agent edits the plan file.
- You do NOT loop more than 3 rounds. Round cap is hard.
- You do NOT auto-execute the plan after the loop. The user decides next steps.
- You do NOT skip the final summary. Even on failure, show what happened.
````

- [ ] **Step 2: Verify the SKILL.md exists and has frontmatter**

Run:

```bash
head -15 plugins/plan-reflection/skills/plan-reflection/SKILL.md
```

Expected: starts with `---`, has `name: plan-reflection`, has a multi-line `description:`, ends frontmatter with `---`.

- [ ] **Step 3: Verify all phases are present**

Run:

```bash
grep "^## Phase" plugins/plan-reflection/skills/plan-reflection/SKILL.md
```

Expected output:
```
## Phase 0: Find the Active Plan
## Phase 1: Detect Domain
## Phase 2: Initialize Loop State
## Phase 3: Reflection Loop
## Phase 4: Present Final Summary
```

- [ ] **Step 4: Verify references are pointed to correctly**

Run:

```bash
grep "CLAUDE_PLUGIN_ROOT" plugins/plan-reflection/skills/plan-reflection/SKILL.md
```

Expected: at least 2 matches, both pointing into `skills/plan-reflection/references/`.

---

## Task 5: Write the plugin's Chinese README

**Files:**
- Create: `plugins/plan-reflection/README.md`

Per henry-hub convention, every plugin README is in Chinese.

- [ ] **Step 1: Create the file**

Write `plugins/plan-reflection/README.md` with this exact content:

````markdown
# plan-reflection — 多 Agent 计划反思循环

对 `~/.claude/plans/` 中的活跃计划执行多轮独立审核。一个 Reviewer Agent 找出 blocking issues，一个独立的 Corrector Agent 修正它们，循环最多 3 轮，带收敛保护。最终返回审核报告，由你决定下一步。

## 为什么需要这个

写 plan 的人（不管是人还是 AI）通常看不到自己的盲点：内部矛盾、遗漏的边界 case、不切实际的步骤、范围蔓延。让同一个 agent 自己审核自己的 plan 很少有效——审核者和作者共享同样的假设。

这个 skill 实现了 **多 agent 反思模式**：
- **独立审核** —— Reviewer 是只读的、独立的，没有作者的上下文偏见
- **职责分离** —— Reviewer 找问题，Corrector 修问题，互不干涉
- **硬约束循环** —— 最多 3 轮、blocking 数无进展即停止、persistent deferred 即停止
- **不自动实施** —— skill 永远把决策权交还给用户

## 使用方式

先用其他工具（比如 `superpowers:writing-plans`）写好一个 plan，确认它已经在 `~/.claude/plans/` 下，然后调用：

```
让我审一下计划
帮我 review 一下方案
adversarial review my plan
```

skill 会：
1. 找到当前活跃的 plan（多个则让你选）
2. 自动识别 plan 的领域（technical / product / devops / architecture / general）
3. 派发 Reviewer Agent 审核
4. 如果有 blocking issues，派发 Corrector Agent 修正
5. 循环最多 3 轮
6. 展示最终审核报告

## 终止条件

循环会在以下任意一个条件触发时停止：

| 条件 | 说明 |
|------|------|
| **PASS** | Reviewer 给出 PASS（零 blocking issues） |
| **Round cap** | 达到 3 轮上限 |
| **Stalled** | 第 2 轮起，blocking 数没有下降（持平或上升） |
| **Persistent deferred** | 同一个 issue 连续两轮被标记 DEFERRED |
| **Parse failure** | Reviewer 输出连续两次无法解析 |
| **Dispatch failure** | Agent 派发出错 |

无论哪种终止，都会展示完整的审核报告和轮次历史。

## 设计原则

- **Reviewer 只读** —— 不改任何文件，只输出方向性建议
- **Corrector 只改 plan 文件** —— 不动其他文件，只做最小范围修改
- **Orchestrator 不读 plan 内容** —— 主会话只解析结构化字段，避免上下文污染
- **不打分** —— 二元 blocking 判断比分数更难注水
- **不自审** —— Reviewer 和 Corrector 是不同的 agent，独立性是核心价值
- **不自动实施** —— 审核结束后用户自己决定下一步

## 不适用场景

- ❌ 生成新的 plan（请用 `superpowers:writing-plans`）
- ❌ 审核代码（请用 code-reviewer agents）
- ❌ 审核 `~/.claude/plans/` 之外的 markdown 文件
- ❌ 自动执行 plan

## 文件结构

```
plan-reflection/
├── .claude-plugin/plugin.json
├── README.md                                    # 本文件
└── skills/plan-reflection/
    ├── SKILL.md                                 # 主 skill（编排逻辑）
    └── references/
        ├── review-dimensions.md                 # 各领域审核维度
        └── report-templates.md                  # 审核/修正报告模板
```

## 安装

```
/plugins install plan-reflection@henry-hub
```
````

- [ ] **Step 2: Verify the README**

Run:

```bash
wc -l plugins/plan-reflection/README.md
```

Expected: at least 50 lines.

---

## Task 6: Register the plugin in marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

The marketplace.json registers all plugins. We need to append a new entry to the `plugins` array.

- [ ] **Step 1: Read the current marketplace.json**

Run:

```bash
cat .claude-plugin/marketplace.json
```

Note the structure: a JSON object with a `plugins` array, each entry has `name`, `description`, `source`.

- [ ] **Step 2: Add the plan-reflection entry**

Use the Edit tool to insert the new plugin entry into `.claude-plugin/marketplace.json`. Locate this line:

```
    { "name": "drawio-diagram", "description": "Draw.io 图表生成器：流程图、架构图、系统拓扑图、业务流程全景图，支持自动核验和复杂流程分区", "source": "./plugins/drawio-diagram" }
```

Replace it with:

```
    { "name": "drawio-diagram", "description": "Draw.io 图表生成器：流程图、架构图、系统拓扑图、业务流程全景图，支持自动核验和复杂流程分区", "source": "./plugins/drawio-diagram" },
    { "name": "plan-reflection", "description": "多 Agent 计划反思循环：独立 Reviewer 找 blocking issues，独立 Corrector 修正，最多 3 轮循环带收敛保护", "source": "./plugins/plan-reflection" }
```

(Note: the original line had no trailing comma because it was the last entry. After this edit, drawio-diagram has a comma, plan-reflection becomes the new last entry with no trailing comma.)

- [ ] **Step 3: Verify the JSON is still valid**

Run:

```bash
python3 -m json.tool .claude-plugin/marketplace.json
```

Expected: pretty-printed JSON with no syntax error. Verify `plan-reflection` appears in the output.

- [ ] **Step 4: Verify plugin count is now 12**

Run:

```bash
python3 -c "import json; data = json.load(open('.claude-plugin/marketplace.json')); print(len(data['plugins']))"
```

Expected output: `12`

---

## Task 7: Update the root README.md

**Files:**
- Modify: `README.md`

Add `plan-reflection` to the appropriate category table. Since it's a development/process tool, it fits under "开发工具".

- [ ] **Step 1: Locate the 开发工具 table**

Run:

```bash
grep -n "开发工具" README.md
```

Expected: returns the line number where `### 开发工具` starts (around line 57).

- [ ] **Step 2: Append plan-reflection to the 开发工具 table**

Use the Edit tool to locate this line in `README.md`:

```
| req-to-issues | 需求分析拆解工具：将需求素材分析拆解为 GitHub/GitLab Issue 并批量上传 | `/plugins install req-to-issues@henry-hub` |
```

Replace it with:

```
| req-to-issues | 需求分析拆解工具：将需求素材分析拆解为 GitHub/GitLab Issue 并批量上传 | `/plugins install req-to-issues@henry-hub` |
| plan-reflection | 多 Agent 计划反思循环：独立 Reviewer 找 blocking issues + 独立 Corrector 修正，最多 3 轮 | `/plugins install plan-reflection@henry-hub` |
```

- [ ] **Step 3: Verify the change**

Run:

```bash
grep "plan-reflection" README.md
```

Expected: one match line showing the new row.

---

## Task 8: Update CLAUDE.md (version + categories)

**Files:**
- Modify: `CLAUDE.md`

Bump the version line and add `plan-reflection` to the Plugin Categories table.

- [ ] **Step 1: Bump the version**

Use the Edit tool to locate this line in `CLAUDE.md`:

```
> Version: v0.6.0 (2026-03-31)
```

Replace it with:

```
> Version: v0.7.0 (2026-04-07)
```

(MINOR bump because we're adding a new plugin per the versioning convention in CLAUDE.md.)

- [ ] **Step 2: Add plan-reflection to the categories table**

Run:

```bash
grep -n "Dev Tools" CLAUDE.md
```

Expected: shows the line of the "Dev Tools" row in the Plugin Categories table.

Use the Edit tool to locate this line:

```
| Dev Tools | ssot-prompt-engineer |
```

Replace it with:

```
| Dev Tools | ssot-prompt-engineer, plan-reflection |
```

- [ ] **Step 3: Verify both changes**

Run:

```bash
grep -E "Version:|plan-reflection" CLAUDE.md
```

Expected: shows the new version line AND the Dev Tools line containing `plan-reflection`.

---

## Task 9: Validate plugin structure

**Files:** none modified

Use the plugin-dev:plugin-validator agent to verify the plugin scaffolding is correct.

- [ ] **Step 1: Run the validator**

Use the Agent tool with `subagent_type: plugin-dev:plugin-validator` and this prompt:

```
Validate the new plan-reflection plugin at /Users/henry/dev/2_areas/henry-hub/plugins/plan-reflection/.

Check:
1. plugin.json conforms to henry-hub's auto-discovery rules (only name/version/description, no component arrays)
2. SKILL.md frontmatter is well-formed (only `name` and `description` fields)
3. The skill follows the nested pattern: skills/plan-reflection/SKILL.md
4. Reference files exist at the paths the SKILL.md claims (skills/plan-reflection/references/review-dimensions.md and report-templates.md)
5. ${CLAUDE_PLUGIN_ROOT} references resolve correctly
6. The marketplace.json entry for plan-reflection is well-formed

Report any issues found. Do not make changes — just report.
```

Wait for the agent's report.

- [ ] **Step 2: Address any issues the validator finds**

If the validator reports issues, fix them inline using the Edit tool. Re-run the validator to confirm the fixes. Repeat until validator reports no issues.

If no issues, proceed.

---

## Task 10: Manual end-to-end test

**Files:** none modified — only verifying the skill works end-to-end

This task verifies the skill actually runs against a real plan. It's a manual smoke test.

- [ ] **Step 1: Create a deliberately flawed test plan**

Write a test plan to `~/.claude/plans/test-plan-reflection.md` with this content (intentionally contains 2 blocking issues and 1 suggestion to verify the loop fires):

```markdown
# Test Plan for Plan Reflection

## Goal

Build a CLI tool that processes CSV files.

## Approach

1. Read the input file
2. Parse the CSV using a library
3. Apply transformations
4. Write output

## Validation

We will use TBD for validation.

## Error Handling

Handle errors appropriately.
```

(The TBD in Validation, the vague "Handle errors appropriately", and the unspecified library/transformations should give the reviewer 2-3 blocking issues to find.)

Run:

```bash
mkdir -p ~/.claude/plans && cat > ~/.claude/plans/test-plan-reflection.md << 'PLAN_EOF'
# Test Plan for Plan Reflection

## Goal

Build a CLI tool that processes CSV files.

## Approach

1. Read the input file
2. Parse the CSV using a library
3. Apply transformations
4. Write output

## Validation

We will use TBD for validation.

## Error Handling

Handle errors appropriately.
PLAN_EOF
```

Verify it was created:

```bash
ls -la ~/.claude/plans/test-plan-reflection.md
```

- [ ] **Step 2: Sync the installed plugin copy**

Per CLAUDE.md's development workflow, the installed copy needs to be in sync with the working repo. The plugin hasn't been published yet, so we need to manually link it for testing.

Run:

```bash
ls ~/.claude/plugins/marketplaces/ 2>/dev/null
```

If the henry-hub marketplace is installed there, you can either:
- (a) Wait until after Task 11 (commit + push) and `git pull` the marketplace copy, OR
- (b) Symlink the plugin directory for immediate testing:

```bash
ln -sf "$(pwd)/plugins/plan-reflection" ~/.claude/plugins/marketplaces/henry-hub/plugins/plan-reflection 2>/dev/null || echo "marketplace not installed locally — skip symlink, run e2e after publish"
```

- [ ] **Step 3: Document the manual test instructions for the user**

Output to the user:

```
Manual end-to-end test ready. To verify the skill works:

1. Open a fresh Claude Code session
2. Type: "review my plan"
3. Expected behavior:
   - Skill discovers ~/.claude/plans/test-plan-reflection.md
   - Detects domain (probably "technical")
   - Dispatches Reviewer Agent → finds at least 2 blocking issues (the TBD and the vague error handling)
   - Dispatches Corrector Agent → fixes or defers them
   - May run round 2 depending on what's left
   - Shows final summary with round history

After verifying, delete the test plan:
   rm ~/.claude/plans/test-plan-reflection.md
```

This step is informational for the user. The plan executor should NOT actually open another Claude Code session — that's a human verification step. Just confirm the test plan file exists and the user knows how to test.

- [ ] **Step 4: Verify the test plan exists and is well-formed**

Run:

```bash
test -f ~/.claude/plans/test-plan-reflection.md && echo "Test plan ready"
```

Expected output: `Test plan ready`

---

## Task 11: Commit and push

**Files:** all the files created/modified in tasks 1-8

- [ ] **Step 1: Verify git status shows the expected changes**

Run:

```bash
git status --short
```

Expected output (some order):
```
A  plugins/plan-reflection/.claude-plugin/plugin.json
A  plugins/plan-reflection/README.md
A  plugins/plan-reflection/skills/plan-reflection/SKILL.md
A  plugins/plan-reflection/skills/plan-reflection/references/review-dimensions.md
A  plugins/plan-reflection/skills/plan-reflection/references/report-templates.md
M  .claude-plugin/marketplace.json
M  README.md
M  CLAUDE.md
```

(Note: untracked files show as `??` not `A` until staged.)

- [ ] **Step 2: Stage only the plan-reflection files**

Run:

```bash
git add plugins/plan-reflection/ .claude-plugin/marketplace.json README.md CLAUDE.md
```

Do NOT use `git add .` or `git add -A` — those would also pick up `~/.claude/plans/test-plan-reflection.md` if it's somewhere tracked, or other in-progress work.

- [ ] **Step 3: Verify staged files**

Run:

```bash
git status --short
```

Expected: all 8 files now show as `A` (added) or `M` (modified) in the staged area.

- [ ] **Step 4: Create the commit**

Run:

```bash
git commit -m "$(cat <<'EOF'
feat(plan-reflection): add multi-agent plan reflection skill

New plugin that runs a dual-agent reflection loop on plans in
~/.claude/plans/. Independent Reviewer agent finds blocking issues,
separate Corrector agent fixes them, loops up to 3 rounds with
convergence protection (round cap, no-progress detection, persistent
deferred detection). Returns audit report — no auto-execution.

Design rationale:
- Dual-agent over single-agent: independence is the core value
- Blocking-count gating over scoring: scores inflate, counts don't
- Orchestrator never reads plan content: prevents context pollution
- Inline agent dispatch (no agents/ dir): matches henry-hub convention

Bumps marketplace to v0.7.0.

Spec: docs/plans/2026-04-07-plan-reflection-design.md
Plan: docs/plans/2026-04-07-plan-reflection-implementation.md

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit created successfully.

- [ ] **Step 5: Push to remote**

Run:

```bash
git push
```

Expected: push succeeds, branch is up to date with remote.

- [ ] **Step 6: Confirm completion**

Output to the user:

```
Plan reflection skill implemented and pushed.

New plugin: plan-reflection v0.1.0 (henry-hub v0.7.0)

Files created:
  plugins/plan-reflection/.claude-plugin/plugin.json
  plugins/plan-reflection/README.md
  plugins/plan-reflection/skills/plan-reflection/SKILL.md
  plugins/plan-reflection/skills/plan-reflection/references/review-dimensions.md
  plugins/plan-reflection/skills/plan-reflection/references/report-templates.md

Files modified:
  .claude-plugin/marketplace.json (+1 plugin entry)
  README.md (+1 row in Dev Tools table)
  CLAUDE.md (version v0.6.0 → v0.7.0, +plan-reflection in categories)

To test end-to-end:
  1. In a fresh Claude Code session, type "review my plan"
  2. The skill discovers ~/.claude/plans/test-plan-reflection.md
  3. Verify it dispatches reviewer + corrector and produces a final summary
  4. Clean up: rm ~/.claude/plans/test-plan-reflection.md
```
