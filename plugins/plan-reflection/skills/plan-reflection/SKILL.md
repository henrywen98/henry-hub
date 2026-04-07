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
