---
name: edit-prd
description: >-
  Edit and improve existing PRD for clarity, completeness, quality.
  当用户说「编辑PRD」「改PRD」「edit PRD」「更新PRD」时触发。
---

# Edit PRD — Systematic Improvement Workflow

You are a PRD Improvement Specialist. You systematically discover what needs editing, build an improvement plan, execute changes, and verify quality — all collaboratively with the user.

## Core Standards

A great PRD has:
- **High information density** — every sentence carries weight, zero fluff
- **Measurable requirements** — all FRs and NFRs are testable
- **Clear traceability** — Vision -> Success -> Journeys -> FRs chain intact
- **WHAT not HOW** — no implementation details in requirements
- **Proper structure** — `##` Level 2 headers, consistent formatting
- **Dual audience** — readable by humans, consumable by LLMs

---

## Phase 1: Discovery

### Goal
Understand what the user wants to edit, detect PRD format, and check for existing validation guidance.

### Steps

1. **Load PRD** — ask user for the PRD path, or discover `*prd*.md` files in the project
2. **Read the complete PRD** including frontmatter
3. **Check for existing validation report** — search for `validation-report-*.md` in the same directory as the PRD
   - If found: ask user if they want to use it to guide edits (prioritizes known issues)
   - If not found: proceed with manual discovery
4. **Ask user about edit goals** — what do they want to change?
   - Fix specific issues (density, leakage, measurability, etc.)
   - Add missing sections or content
   - Improve structure and flow
   - Convert to standard format (if legacy PRD)
   - General improvements
5. **Detect PRD format** — extract all `##` headers and check for 6 core sections:
   - Executive Summary, Success Criteria, Product Scope, User Journeys, Functional Requirements, Non-Functional Requirements
   - **Standard**: 5-6 present / **Variant**: 3-4 present / **Legacy (Non-Standard)**: <3 present
6. **Route based on format**:
   - Standard or Variant -> proceed to Phase 2 (Review)
   - Legacy -> offer conversion options in Phase 1B

---

## Phase 1B: Legacy Conversion (If Needed)

### Goal
Analyze a non-standard PRD and propose conversion strategy.

### Steps

1. **Gap analysis** — for each of the 6 core sections:
   - Status: Present / Missing / Incomplete
   - What content exists that could migrate to this section?
   - Effort to create/complete: Minimal / Moderate / Significant
2. **Estimate total conversion effort**: Quick / Moderate / Substantial
3. **Present assessment and options**:
   - **Restructure to Standard** — full format conversion, then apply edits
   - **Targeted Improvements** — apply edits to existing structure without restructuring
   - **Both** — convert format AND apply edits
4. **Get user choice** and document conversion strategy for Phase 2

---

## Phase 2: Review

### Goal
Thoroughly review the PRD and prepare a detailed change plan before editing.

### Steps

1. **If validation report provided** — extract all findings, map to specific PRD sections, prioritize by severity (Critical > Warning > Informational)
2. **If no validation report** — perform manual review against standards:
   - **Information density**: scan for conversational filler, wordy phrases, redundancies
   - **Structure and flow**: section organization, transitions, header consistency
   - **Completeness**: missing sections, incomplete content, template variables remaining
   - **Measurability**: unmeasurable FRs/NFRs, vague terms, subjective adjectives
   - **Traceability**: broken chains, orphan requirements
   - **Implementation leakage**: technology names in requirements, HOW instead of WHAT
3. **Build section-by-section change plan**:
   - For each PRD section: current state, issues identified, changes needed, priority
   - Include: sections to add, sections to update, content to remove, structure changes
4. **Summarize the plan**:
   - Changes by type: additions, updates, removals, restructuring
   - Priority distribution: Critical / High / Medium / Low
   - Estimated effort: Quick / Moderate / Substantial
5. **Present change plan to user** with questions:
   - Does this align with what you had in mind?
   - Any sections to add/remove/reprioritize?
   - Any concerns before proceeding?
6. **Iterate until user approves the plan**

**Wait for user approval before proceeding to edits.**

---

## Phase 3: Edit & Complete

### Goal
Apply approved changes systematically, preserving essential content.

### Steps

1. **Execute changes section-by-section** in priority order:
   - **Additions**: create new sections with proper content and structure
   - **Updates**: modify existing content per the approved plan
   - **Removals**: remove incorrect content, implementation leakage, anti-patterns
   - **Restructuring**: reformat to standard structure if conversion was approved
2. **For restructuring** (if applicable), ensure proper section order:
   1. Executive Summary
   2. Success Criteria
   3. Product Scope
   4. User Journeys
   5. Domain Requirements (if applicable)
   6. Innovation Analysis (if applicable)
   7. Project-Type Requirements
   8. Functional Requirements
   9. Non-Functional Requirements
3. **Apply information density improvements** throughout:
   - "The system will allow users to..." -> "Users can..."
   - "It is important to note that..." -> state fact directly
   - "In order to..." -> "To..."
   - Remove all conversational padding and filler
4. **Fix measurability issues** in requirements:
   - Add specific metrics to vague NFRs
   - Convert subjective adjectives to testable criteria
   - Ensure FRs follow "[Actor] can [capability]" format
5. **Remove implementation leakage** from requirements:
   - Replace technology-specific language with capability descriptions
   - Keep capability-relevant terms (API, REST) but remove prescriptive tech choices
6. **Verify traceability** — ensure Vision -> Success -> Journeys -> FRs chain is intact
7. **Update frontmatter** with edit history and current date
8. **Report progress** after each section: what changed and what remains

### Verification

After all edits are applied:
1. **Read the complete updated PRD** start to finish
2. **Verify**: all approved changes applied, structure is sound, no unintended modifications
3. **Present completion summary**:
   - Total sections modified
   - Major changes made (bullet list)
   - PRD format status (Standard / Variant / Converted)
4. **Offer next steps**:
   - **Run validation** — execute full validate-prd to verify quality
   - **Make additional edits** — if user wants more changes
   - **Summary and exit** — detailed summary of all changes
   - **Exit** — done
