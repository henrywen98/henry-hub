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
