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
