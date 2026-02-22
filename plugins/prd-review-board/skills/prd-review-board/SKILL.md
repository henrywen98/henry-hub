---
name: prd-review-board
description: This skill should be used when the user asks to "review a PRD", "evaluate requirements", "red team a product spec", "expert review my PRD", "assess product requirements", "run a PRD review board", or wants multi-expert evaluation of a product requirements document. Orchestrates a Team Swarm of 14 cross-functional expert agents for independent review, stress testing, and real debate.
---

# PRD Review Board — Team Swarm Orchestration

Orchestrate a 14-expert Team Swarm to perform enterprise-grade red team review of a PRD (Product Requirements Document).

## Overview

This skill guides the Team Leader (main agent) through a structured multi-phase review process using real Team Swarm with independent agent contexts and message-passing debates.

## Prerequisites

- A PRD document (file path, pasted text, screenshot, or any input format)
- An output directory for review artifacts

## Workflow Phases

### Phase 1: Input Processing & PRD Draft

1. Receive user input (any format: text, file, screenshot, URL, prototype, voice description)
2. If input is NOT already a PRD, generate a structured PRD draft using the `prd-review-board:prd-writer` agent via Task tool
3. Save PRD to `{output-dir}/01-prd-v1.md`
4. Confirm with user before proceeding to review

### Phase 2: Assemble Review Board & Independent Review

1. Create team:
   ```
   TeamCreate("prd-review-board")
   ```

2. Create tasks for all 13 review experts (exclude prd-writer):
   ```
   TaskCreate for each expert's review assignment
   ```

3. Spawn all 13 expert agents in parallel using Task tool:
   ```
   Task(subagent_type="prd-review-board:<agent-name>", team_name="prd-review-board", name="<agent-name>")
   ```

   Expert agents to spawn:
   - product-manager
   - staff-architect
   - distributed-systems
   - backend-engineer
   - frontend-engineer
   - qa-director
   - ai-architect
   - llm-safety
   - devops-sre
   - performance-engineer
   - security-compliance
   - finops
   - business-strategist

4. Send PRD content to each expert via SendMessage
5. Each expert produces independent review following the template in `references/review-templates.md`
6. Collect all reviews, save to `{output-dir}/02-reviews/`

### Phase 3: Red Team Stress Test

1. Send all review reports to: staff-architect, devops-sre, performance-engineer, security-compliance
2. Request stress test analysis based on scenarios in `references/stress-test-scenarios.md`
3. Collect stress test results, save to `{output-dir}/03-stress-test.md`

### Phase 4: Expert Roundtable Debate (3 Rounds)

Follow the debate protocol defined in `references/debate-protocol.md`:

**Round 1 — Cross-Challenge:**
- Broadcast all review reports to all experts
- Each expert must challenge at least 2 other experts' findings
- Experts respond via SendMessage DMs

**Round 2 — Deep Dive on Disputes:**
- Extract top 5 unresolved disputes from Round 1
- Direct specific experts to debate each dispute point
- Guide toward consensus or documented trade-offs

**Round 3 — Final Verdict:**
- Request each expert to submit: GO / CONDITIONAL GO / NO-GO + reasoning
- Collect all final positions

Save debate log to `{output-dir}/04-debate-log.md`

### Phase 5: Risk Matrix & FinOps Assessment

1. Synthesize findings from all phases into risk matrix (minimum 10 risks)
2. Request finops agent for cost/scalability assessment
3. Save to `{output-dir}/05-risk-matrix.md` and `{output-dir}/06-finops-assessment.md`

### Phase 6: Required Changes & Revised PRD

1. Generate categorized change list:
   - 🔴 Must Fix Before Any Build (blocking)
   - 🟡 Should Improve Soon (important)
   - 🟢 Nice to Have (optimization)
2. Delegate to prd-writer agent to produce revised PRD v2 incorporating all must-fix items
3. Save to `{output-dir}/07-required-changes.md` and `{output-dir}/08-prd-v2-revised.md`

### Phase 7: Final Verdict

Produce final verdict document:
- Decision: GO / CONDITIONAL GO / NO-GO
- Confidence Level: XX%
- Top 3 Blocking Risks
- System Maturity Level: Prototype / Beta / Production-Ready
- Recommended Next Steps

Save to `{output-dir}/09-final-verdict.md`

### Phase 8: Comprehensive Report & Cleanup

1. Merge all documents into single comprehensive report
2. Save to `{output-dir}/10-comprehensive-report.md`
3. Send shutdown_request to all expert agents
4. TeamDelete to clean up team resources

## Agent Spawning Guidelines

- Use `model: "sonnet"` for review experts (cost efficiency)
- Use `model: "opus"` for prd-writer (quality critical)
- Spawn experts in parallel batches to maximize speed
- Each expert Task prompt must include the full PRD content

## Output Structure

```
{output-dir}/
├── 01-prd-v1.md
├── 02-reviews/
│   ├── product-manager-review.md
│   ├── staff-architect-review.md
│   └── ... (13 review files)
├── 03-stress-test.md
├── 04-debate-log.md
├── 05-risk-matrix.md
├── 06-finops-assessment.md
├── 07-required-changes.md
├── 08-prd-v2-revised.md
├── 09-final-verdict.md
└── 10-comprehensive-report.md
```

## Additional Resources

### Reference Files

- **`references/prd-template.md`** — Generic PRD template for generating v1 drafts
- **`references/review-templates.md`** — Output templates for each review phase
- **`references/debate-protocol.md`** — Detailed rules for the 3-round debate
- **`references/stress-test-scenarios.md`** — Red team pressure scenarios

### Agent Definitions

All 14 expert agents are defined in the plugin's `agents/` directory. Each agent has a specialized persona, domain expertise, and red team review instructions.
