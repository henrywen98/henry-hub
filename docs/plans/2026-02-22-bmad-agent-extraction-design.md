# BMAD Agent Extraction Design

**Date:** 2026-02-22
**Source:** BMAD-METHOD v6.0.1 (https://github.com/bmad-code-org/bmad-method)
**Goal:** Extract Quinn (QA) and John (PM) agents as independent Claude Code plugins

## Decision Summary

- **Extraction style:** Skill 化 — 将 BMAD 分步 workflow 压缩为独立 SKILL.md
- **Plugin packaging:** 两个独立插件（bmad-qa-agent, bmad-prd-agent）
- **BMAD dependency:** 完全去除，零依赖
- **PM scope:** 保留全部 6 个 workflow

## Plugin 1: bmad-qa-agent

### Structure
```
plugins/bmad-qa-agent/
├── .claude-plugin/plugin.json
├── README.md
├── skills/
│   └── qa-automate/SKILL.md
└── agents/
    └── quinn.md
```

### Agent: Quinn (QA Engineer)
- **Persona:** Pragmatic test automation engineer, "ship it and iterate"
- **Core capability:** Generate API + E2E tests for existing code

### Skill: qa-automate
Source: `src/bmm/workflows/qa/automate/` (instructions.md + checklist.md)

Flow:
1. Detect test framework (package.json, existing tests, or suggest)
2. Identify features to test (user-specified or auto-discover)
3. Generate API tests (status codes, response structure, happy path + errors)
4. Generate E2E tests (user workflows, semantic locators, visible assertions)
5. Run tests and fix failures
6. Create coverage summary

## Plugin 2: bmad-prd-agent

### Structure
```
plugins/bmad-prd-agent/
├── .claude-plugin/plugin.json
├── README.md
├── skills/
│   ├── create-prd/SKILL.md
│   ├── validate-prd/SKILL.md
│   ├── edit-prd/SKILL.md
│   ├── create-epics/SKILL.md
│   ├── check-readiness/SKILL.md
│   └── correct-course/SKILL.md
└── agents/
    └── john.md
```

### Agent: John (Product Manager)
- **Persona:** PM veteran, 8+ years, "asks WHY relentlessly", direct and data-sharp
- **Core capability:** PRD lifecycle + Epic decomposition + Implementation readiness

### Skills (6 total):

#### 1. create-prd
Source: `src/bmm/workflows/2-plan-workflows/create-prd/steps-c/` (15 step files, condensed below)

Condensed flow:
1. Init: discover input docs (briefs, research), classify greenfield/brownfield
2. Project discovery: type, domain, complexity classification
3. Vision discovery: differentiator, unique value proposition
4. Executive summary generation
5. Success criteria: user/business/technical metrics, MVP scope
6. User journey mapping: ALL user types, narrative stories, emotional arcs
7. Domain requirements (if medium/high complexity)
8. Innovation discovery (if signals detected)
9. Project-type deep dive (type-specific questions)
10. Scoping: MVP boundaries, phased roadmap, risk assessment
11. Functional requirements synthesis (20-50 FRs, "Actor can [capability]")
12. Non-functional requirements (selective, measurable)
13. Document polish and completion

Key principles:
- Facilitator role: discover through conversation, not template filling
- Append-only document building
- Step-by-step user confirmation
- FR traceability: Vision → Success → Journeys → FRs

#### 2. validate-prd
Source: `src/bmm/workflows/2-plan-workflows/create-prd/steps-v/` (13 steps)

Condensed flow:
1. Document discovery and loading
2. Format detection and structure check
3. Parity check (internal consistency)
4. Information density validation (zero fluff)
5. Product brief coverage validation
6. Measurability validation (metrics are specific?)
7. Traceability validation (requirements traceable to user needs?)
8. Implementation leakage check (no HOW in WHAT doc)
9. Domain compliance validation
10. Project type validation
11. SMART validation
12. Holistic quality assessment
13. Completeness validation and report generation

Output: validation report with findings and recommendations

#### 3. edit-prd
Source: `src/bmm/workflows/2-plan-workflows/create-prd/steps-e/` (4 steps)

Flow:
1. Discover existing PRD and identify issues
2. Legacy format conversion (if needed)
3. Review and identify improvements
4. Make improvements and complete

#### 4. create-epics
Source: `src/bmm/workflows/3-solutioning/create-epics-and-stories/` (4 steps)

Prerequisites: Completed PRD + Architecture doc (UX recommended if UI)

Flow:
1. Validate prerequisites, extract ALL FRs/NFRs from PRD
2. Design epic list (user-value-first grouping, no forward dependencies)
3. Generate stories per epic (BDD Given/When/Then format, single-dev sized)
4. Final validation (every FR covered, no forward dependencies)

Key rules:
- Each epic standalone, enables future epics without requiring them
- Database/entities created only when needed, not upfront
- Stories sized for single dev agent completion

#### 5. check-readiness
Source: `src/bmm/workflows/3-solutioning/check-implementation-readiness/` (6 steps)

Adversarial review approach:

Flow:
1. Document discovery (PRD, Architecture, Epics)
2. PRD quality analysis
3. Epic coverage validation (every FR covered?)
4. UX alignment check
5. Epic quality review
6. Final assessment: PASS / CONCERNS / FAIL

#### 6. correct-course
Source: `src/bmm/workflows/4-implementation/correct-course/` (6 steps)

Flow:
1. Initialize: confirm change trigger, gather description
2. Systematic change analysis checklist
3. Draft specific change proposals (old → new with rationale)
4. Generate sprint change proposal document
5. Route by scope: Minor (dev), Moderate (PO/SM), Major (PM/Architect)
6. Completion summary

## Removed BMAD Dependencies

| BMAD Concept | Replacement |
|-------------|-------------|
| `_bmad/` directory | Plugin's own `skills/` directory |
| `config.yaml` | User provides project name/path directly |
| `workflow.xml` engine | Skill prompt guides the flow |
| `{planning_artifacts}` path var | User specifies or defaults to `docs/` |
| `{implementation_artifacts}` path var | User specifies or defaults to project root |
| Party Mode / Advanced Elicitation | Removed (BMAD-specific features) |
| `stepsCompleted` frontmatter tracking | Simplified — skill handles state in conversation |
| `agent-manifest.csv` | Not needed — Claude Code auto-discovery |

## Marketplace Registration

Both plugins need to be registered in the marketplace:
- Add entries to `.claude-plugin/marketplace.json`
- Update root `README.md` plugin table
- Update `CLAUDE.md` version (MINOR bump) and Plugin Categories table

## Attribution

Both plugins will credit BMAD-METHOD in README and plugin metadata:
- Original author: BMad (bmad-code-org)
- License: MIT (same as BMAD-METHOD)
- Source: https://github.com/bmad-code-org/bmad-method
