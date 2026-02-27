# BMAD Agent Extraction Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extract Quinn (QA) and John (PM) from BMAD-METHOD v6.0.1 as two independent Claude Code plugins in henry-marketplace.

**Architecture:** Each plugin is self-contained with auto-discovered skills and agents. BMAD's step-file workflows are condensed into single SKILL.md files. No external dependencies.

**Tech Stack:** Claude Code plugin system (plugin.json + skills/ + agents/ auto-discovery), Markdown

**Design doc:** `docs/plans/2026-02-22-bmad-agent-extraction-design.md`
**BMAD source:** `/Users/henry/dev/BMAD-METHOD/`

---

## Task 1: Create bmad-qa-agent plugin scaffold

**Files:**
- Create: `plugins/bmad-qa-agent/.claude-plugin/plugin.json`

**Step 1: Create plugin.json**

```json
{
  "name": "bmad-qa-agent",
  "version": "1.0.0",
  "description": "QA 自动化测试生成 Agent（基于 BMAD Method Quinn）。自动检测测试框架，生成 API 和 E2E 测试。"
}
```

**Step 2: Verify directory exists**

Run: `ls plugins/bmad-qa-agent/.claude-plugin/plugin.json`
Expected: file exists

---

## Task 2: Create Quinn agent definition

**Files:**
- Create: `plugins/bmad-qa-agent/agents/quinn.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/agents/qa.agent.yaml`

**Step 1: Write quinn.md**

The agent file should contain:
- Frontmatter: name (`quinn`), description (QA automation engineer that generates tests for existing code)
- System prompt extracted from BMAD's qa.agent.yaml persona section
- Persona: pragmatic, "ship it and iterate", practical and straightforward
- Critical actions: never skip running tests, use standard framework APIs, keep simple, focus on realistic scenarios
- Welcome message with capabilities list
- Menu of available skills: qa-automate

Key adaptation: remove all `{project-root}/_bmad/` references, remove workflow.yaml pointer, replace with skill invocation guidance.

**Step 2: Verify**

Run: `ls plugins/bmad-qa-agent/agents/quinn.md`
Expected: file exists

---

## Task 3: Create qa-automate skill

**Files:**
- Create: `plugins/bmad-qa-agent/skills/qa-automate/SKILL.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/qa/automate/instructions.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/qa/automate/checklist.md`

**Step 1: Write SKILL.md**

Frontmatter:
```yaml
name: qa-automate
description: >-
  Generate API and E2E tests for existing code. Auto-detect test framework,
  discover features, generate tests, run and verify.
  当用户说「生成测试」「自动化测试」「写测试」「test generation」时触发。
```

Body should condense BMAD's instructions.md + checklist.md into a single skill:

1. **Detect test framework** — scan package.json, existing test files, suggest if none
2. **Identify features** — ask user or auto-discover from codebase
3. **Generate API tests** — status codes, response structure, happy path + 1-2 error cases
4. **Generate E2E tests** — user workflows, semantic locators, visible outcomes
5. **Run tests** — execute and fix failures immediately
6. **Summary** — output markdown coverage report

Include the validation checklist inline (tests pass, semantic locators, clear descriptions, no hardcoded waits, independent tests).

**Step 2: Verify**

Run: `ls plugins/bmad-qa-agent/skills/qa-automate/SKILL.md`
Expected: file exists

---

## Task 4: Create bmad-qa-agent README

**Files:**
- Create: `plugins/bmad-qa-agent/README.md`

**Step 1: Write README.md (Chinese)**

Sections:
- 简介：基于 BMAD Method 的 QA Agent (Quinn)
- 功能：测试框架检测、API 测试生成、E2E 测试生成、自动运行验证
- 使用方式：直接对话或 `/qa-automate`
- 示例
- 致谢：BMAD-METHOD (MIT License, bmad-code-org)

**Step 2: Commit bmad-qa-agent plugin**

```bash
git add plugins/bmad-qa-agent/
git commit -m "feat: add bmad-qa-agent plugin (Quinn QA Engineer)

Extracted from BMAD-METHOD v6.0.1. Generates API and E2E tests
for existing code with auto framework detection.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: Create bmad-prd-agent plugin scaffold

**Files:**
- Create: `plugins/bmad-prd-agent/.claude-plugin/plugin.json`

**Step 1: Create plugin.json**

```json
{
  "name": "bmad-prd-agent",
  "version": "1.0.0",
  "description": "产品经理 Agent（基于 BMAD Method John）。PRD 创建/验证/编辑 + Epics/Stories + 实现准备检查 + 纠偏。"
}
```

**Step 2: Verify**

Run: `ls plugins/bmad-prd-agent/.claude-plugin/plugin.json`
Expected: file exists

---

## Task 6: Create John agent definition

**Files:**
- Create: `plugins/bmad-prd-agent/agents/john.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/agents/pm.agent.yaml`

**Step 1: Write john.md**

Frontmatter: name (`john`), description (Product Manager specializing in PRD lifecycle, epic decomposition, implementation readiness)

System prompt from BMAD's pm.agent.yaml:
- Persona: PM veteran 8+ years, asks "WHY?" relentlessly, direct and data-sharp
- Principles: user-centered design, Jobs-to-be-Done, ship smallest validation, user value first
- Communication style: detective-like, cuts through fluff
- Available skills list with descriptions (6 skills)

Key adaptation: replace all `{project-root}/_bmad/bmm/workflows/...` exec/workflow pointers with skill invocation guidance.

**Step 2: Verify**

Run: `ls plugins/bmad-prd-agent/agents/john.md`
Expected: file exists

---

## Task 7: Create create-prd skill

**Files:**
- Create: `plugins/bmad-prd-agent/skills/create-prd/SKILL.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/2-plan-workflows/create-prd/steps-c/` (all 12 step files)
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/2-plan-workflows/create-prd/templates/prd-template.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/2-plan-workflows/create-prd/data/prd-purpose.md`

**Step 1: Write SKILL.md**

This is the largest skill. Condense 12 BMAD step files into a structured guide:

Frontmatter:
```yaml
name: create-prd
description: >-
  Create comprehensive PRD through collaborative discovery workflow.
  当用户说「创建PRD」「写PRD」「create PRD」「产品需求文档」时触发。
```

Body structure:
1. **Role definition** — facilitator collaborating with peer, NOT template filling
2. **Initialization** — ask project name, discover existing docs (briefs, research), classify greenfield/brownfield
3. **Phase 1: Discovery** — project type, domain, complexity classification
4. **Phase 2: Vision** — differentiator, unique value proposition, executive summary
5. **Phase 3: Success Criteria** — user/business/technical metrics, MVP scope definition
6. **Phase 4: User Journeys** — map ALL user types, narrative stories with emotional arcs
7. **Phase 5: Domain & Innovation** (conditional) — domain requirements if complex, innovation if signals detected
8. **Phase 6: Project-Type Deep Dive** — type-specific questions and requirements
9. **Phase 7: Scoping** — MVP boundaries, phased roadmap (MVP/Growth/Expansion), risks
10. **Phase 8: Requirements** — Functional (20-50 FRs, "Actor can [capability]") + Non-functional (selective, measurable)
11. **Phase 9: Polish & Complete** — review for density, coherence, completeness

Key rules to embed:
- Each phase: present draft, get user confirmation, then continue
- FR traceability: Vision → Success → Journeys → FRs
- No journey = no requirements
- WHAT not HOW (no implementation details)
- Append-only document building

Include inline PRD template (simplified from BMAD's prd-template.md).

**Step 2: Verify file exists and is substantial (>200 lines)**

Run: `wc -l plugins/bmad-prd-agent/skills/create-prd/SKILL.md`
Expected: 200+ lines

---

## Task 8: Create validate-prd skill

**Files:**
- Create: `plugins/bmad-prd-agent/skills/validate-prd/SKILL.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/2-plan-workflows/create-prd/steps-v/` (13 step files)

**Step 1: Write SKILL.md**

Frontmatter:
```yaml
name: validate-prd
description: >-
  Validate existing PRD for completeness, clarity, and quality.
  当用户说「验证PRD」「检查PRD」「validate PRD」「PRD review」时触发。
```

Body: Condense 13 validation steps into checklist-driven assessment:

1. **Load PRD** — discover and read the target PRD document
2. **Structural Check** — format detection, header structure, frontmatter
3. **Internal Consistency** — parity between sections, no contradictions
4. **Information Density** — zero fluff, every sentence adds value
5. **Brief Coverage** — PRD covers all product brief items (if brief exists)
6. **Measurability** — success metrics are specific and measurable
7. **Traceability** — requirements traceable to user needs and journeys
8. **Implementation Leakage** — no HOW in WHAT document
9. **Domain Compliance** — domain-specific requirements addressed
10. **Project Type Validation** — type-appropriate sections present
11. **SMART Validation** — Specific, Measurable, Achievable, Relevant, Time-bound
12. **Holistic Quality** — overall readability, coherence, completeness
13. **Report Generation** — produce validation report with findings, severity, recommendations

Output: validation report markdown file.

**Step 2: Verify**

Run: `ls plugins/bmad-prd-agent/skills/validate-prd/SKILL.md`
Expected: file exists

---

## Task 9: Create edit-prd skill

**Files:**
- Create: `plugins/bmad-prd-agent/skills/edit-prd/SKILL.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/2-plan-workflows/create-prd/steps-e/` (4 step files)

**Step 1: Write SKILL.md**

Frontmatter:
```yaml
name: edit-prd
description: >-
  Edit and improve existing PRD for clarity, completeness, quality.
  当用户说「编辑PRD」「改PRD」「edit PRD」「更新PRD」时触发。
```

Body: Condense 4 BMAD edit steps:

1. **Discovery** — load existing PRD, identify structural issues, detect legacy format
2. **Legacy Conversion** (if needed) — convert to current PRD structure
3. **Review** — systematic review of each section, identify improvements
4. **Edit & Complete** — apply improvements, preserve essential content, verify coherence

**Step 2: Verify**

Run: `ls plugins/bmad-prd-agent/skills/edit-prd/SKILL.md`
Expected: file exists

---

## Task 10: Create create-epics skill

**Files:**
- Create: `plugins/bmad-prd-agent/skills/create-epics/SKILL.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/3-solutioning/create-epics-and-stories/` (workflow.md + 4 step files)

**Step 1: Write SKILL.md**

Frontmatter:
```yaml
name: create-epics
description: >-
  Transform PRD into Epics and Stories with BDD acceptance criteria.
  当用户说「创建Epic」「拆分需求」「create epics」「用户故事」「stories」时触发。
```

Body: Condense 4 BMAD steps:

1. **Validate Prerequisites** — verify PRD exists, extract ALL FRs/NFRs, extract architecture constraints (if arch doc exists), extract UX requirements (if UX doc exists)
2. **Design Epic List** — group by user value, each epic standalone, no forward dependencies, get user approval
3. **Generate Stories** — per epic: user story format ("As a {user}, I want {capability}, so that {value}"), BDD Given/When/Then acceptance criteria, single-dev sized, database/entities only when needed
4. **Final Validation** — every FR covered, no forward dependencies, story quality check

Key rules to embed:
- Each epic enables future epics without requiring them
- Stories sized for single dev agent completion
- FR → Epic coverage map

**Step 2: Verify**

Run: `ls plugins/bmad-prd-agent/skills/create-epics/SKILL.md`
Expected: file exists

---

## Task 11: Create check-readiness skill

**Files:**
- Create: `plugins/bmad-prd-agent/skills/check-readiness/SKILL.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/3-solutioning/check-implementation-readiness/` (workflow.md + 6 step files)

**Step 1: Write SKILL.md**

Frontmatter:
```yaml
name: check-readiness
description: >-
  Check implementation readiness: validate PRD, Architecture, Epics alignment.
  当用户说「实现准备」「检查对齐」「readiness check」「implementation ready」时触发。
```

Body: Condense 6 BMAD steps using adversarial review approach:

1. **Document Discovery** — find and load PRD, Architecture, Epics documents
2. **PRD Quality Analysis** — completeness, clarity, no implementation leakage
3. **Epic Coverage Validation** — every FR has at least one story
4. **UX Alignment** — UX spec matches PRD requirements and stories
5. **Epic Quality Review** — story granularity, acceptance criteria quality, dependency order
6. **Final Assessment** — PASS / CONCERNS / FAIL with detailed findings

Key principle: "Your success metric is spotting the failures others have made in planning."

**Step 2: Verify**

Run: `ls plugins/bmad-prd-agent/skills/check-readiness/SKILL.md`
Expected: file exists

---

## Task 12: Create correct-course skill

**Files:**
- Create: `plugins/bmad-prd-agent/skills/correct-course/SKILL.md`
- Reference: `/Users/henry/dev/BMAD-METHOD/src/bmm/workflows/4-implementation/correct-course/` (workflow.yaml + instructions.md + checklist.md)

**Step 1: Write SKILL.md**

Frontmatter:
```yaml
name: correct-course
description: >-
  Navigate mid-implementation changes: analyze impact, propose solutions, route for implementation.
  当用户说「纠偏」「变更分析」「correct course」「需求变更」「scope change」时触发。
```

Body: Condense 6 BMAD steps:

1. **Initialize** — confirm change trigger, gather description, verify access to project docs
2. **Impact Analysis** — systematic checklist: epic impact, story impact, architecture impact, UI/UX impact, technical impact
3. **Change Proposals** — draft specific edits (old → new with rationale) for each affected artifact
4. **Sprint Change Proposal** — compile comprehensive proposal document (issue summary, impact analysis, recommended approach, detailed changes, implementation handoff)
5. **Route** — classify scope (Minor/Moderate/Major), recommend routing
6. **Complete** — summary and next steps

**Step 2: Verify**

Run: `ls plugins/bmad-prd-agent/skills/correct-course/SKILL.md`
Expected: file exists

---

## Task 13: Create bmad-prd-agent README

**Files:**
- Create: `plugins/bmad-prd-agent/README.md`

**Step 1: Write README.md (Chinese)**

Sections:
- 简介：基于 BMAD Method 的产品经理 Agent (John)
- 功能概览：6 个 skill 的简要说明
- 使用方式：直接对话或各 skill 的触发方式
- 典型工作流示例：create-prd → validate-prd → create-epics → check-readiness
- 致谢：BMAD-METHOD (MIT License, bmad-code-org)

**Step 2: Commit bmad-prd-agent plugin**

```bash
git add plugins/bmad-prd-agent/
git commit -m "feat: add bmad-prd-agent plugin (John Product Manager)

Extracted from BMAD-METHOD v6.0.1. Full PRD lifecycle:
create/validate/edit PRD, create epics & stories,
implementation readiness check, course correction.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 14: Update marketplace registry

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md` (root)
- Modify: `CLAUDE.md`

**Step 1: Add both plugins to marketplace.json**

Add to plugins array:
```json
{ "name": "bmad-qa-agent", "description": "QA 自动化测试生成 Agent (Quinn)", "source": "./plugins/bmad-qa-agent" },
{ "name": "bmad-prd-agent", "description": "产品经理 Agent (John) - PRD 全生命周期", "source": "./plugins/bmad-prd-agent" }
```

**Step 2: Update root README.md plugin table**

Add both plugins to the appropriate category.

**Step 3: Update CLAUDE.md version and category table**

- Bump version: v0.2.0 (new plugins = MINOR)
- Add to Plugin Categories table:
  - Requirements & Workflow: add bmad-prd-agent
  - Testing: add bmad-qa-agent
- Add to Forked Plugins section note about BMAD attribution

**Step 4: Commit registry updates**

```bash
git add .claude-plugin/marketplace.json README.md CLAUDE.md
git commit -m "feat: register bmad-qa-agent and bmad-prd-agent in marketplace

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Parallelization Strategy

Tasks can be grouped for parallel execution:

- **Group A (QA Plugin):** Tasks 1-4 (sequential within group)
- **Group B (PRD Plugin):** Tasks 5-13 (sequential within group)
- **Group C (Registry):** Task 14 (after A and B complete)

Groups A and B are fully independent and can run in parallel.
