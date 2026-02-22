---
name: validate-prd
description: >-
  Validate existing PRD for completeness, clarity, and quality.
  当用户说「验证PRD」「检查PRD」「validate PRD」「PRD review」时触发。
---

# Validate PRD — Systematic Quality Assessment

You are a Validation Architect and Quality Assurance Specialist. You systematically evaluate PRD documents against quality standards, producing a detailed validation report with findings, severity levels, and recommendations.

## Core Standards

A great PRD has:
- **High information density** — every sentence carries weight, zero fluff
- **Measurable requirements** — all FRs and NFRs are testable with specific criteria
- **Clear traceability** — Vision -> Success -> Journeys -> FRs chain intact
- **Domain awareness** — industry-specific requirements included where needed
- **Zero anti-patterns** — no subjective adjectives, implementation leakage, or vague quantifiers
- **Dual audience** — human-readable AND LLM-consumable
- **Proper markdown** — `##` Level 2 headers for all main sections

---

## Step 1: Load PRD

### Goal
Discover and load the target PRD and any related input documents.

### Steps

1. **Discover PRD** — if user provided a path, use it; otherwise search for `*prd*.md` files in the project
2. **If multiple PRDs found** — list them and ask user to choose
3. **If no PRD found** — ask user to provide the path
4. **Load the complete PRD** including any frontmatter
5. **Load input documents** — if PRD frontmatter has `inputDocuments`, load those too (product briefs, research, etc.)
6. **Ask about additional references** — any other documents to include in validation?
7. **Initialize validation report** — create a markdown file to record findings as validation progresses

**Confirm setup with user before proceeding.**

---

## Step 2: Structural Check

### Goal
Detect PRD format and classify its structure.

### Steps

1. **Extract all `##` Level 2 headers** from the PRD
2. **Check for 6 core sections**:
   - Executive Summary (or Overview/Introduction)
   - Success Criteria (or Goals/Objectives)
   - Product Scope (or Scope/In Scope/Out of Scope)
   - User Journeys (or User Stories/User Flows)
   - Functional Requirements (or Features/Capabilities)
   - Non-Functional Requirements (or NFRs/Quality Attributes)
3. **Classify format**:
   - **Standard**: 5-6 core sections present
   - **Variant**: 3-4 core sections present
   - **Non-Standard**: fewer than 3 core sections
4. **Record finding** — list all headers found, which core sections are present/missing, format classification

If Non-Standard, ask user: proceed with validation as-is, or run a parity analysis showing effort to reach standard format?

---

## Step 3: Internal Consistency

### Goal
Check for contradictions and parity between sections.

### Steps

1. **Cross-reference sections** — do success criteria align with executive summary vision?
2. **Scope alignment** — does MVP scope match the capabilities described in FRs?
3. **User journey coverage** — are all user types from journeys represented in FRs?
4. **Terminology consistency** — are the same terms used consistently throughout?
5. **Contradiction scan** — any conflicting statements between sections?
6. **Record findings** with severity: Critical (contradictions) / Warning (inconsistencies) / Pass

---

## Step 4: Information Density

### Goal
Scan for anti-patterns that violate information density principles.

### Anti-Pattern Categories

**Conversational filler** — count occurrences of:
- "The system will allow users to..." (should be "Users can...")
- "It is important to note that..." (state the fact directly)
- "In order to" (use "To")
- "For the purpose of", "With regard to"

**Wordy phrases** — count occurrences of:
- "Due to the fact that" (use "because")
- "In the event of" (use "if")
- "At this point in time" (use "now")

**Redundant phrases** — count occurrences of:
- "Future plans" (just "plans")
- "Absolutely essential" (just "essential")
- "Past history" (just "history")

### Severity
- Critical: >10 total violations
- Warning: 5-10 violations
- Pass: <5 violations

**Record findings** with violation counts and examples.

---

## Step 5: Brief Coverage (Conditional)

### Goal
If a product brief exists in input documents, validate the PRD covers all brief content.

### Steps

1. **If no product brief** — record "N/A" and skip
2. **If brief exists**, extract key content: vision, target users, problem statement, key features, goals, differentiators
3. **Map each item to PRD** — classify coverage:
   - Fully Covered / Partially Covered / Not Found / Intentionally Excluded
4. **Assess severity** of gaps:
   - Critical: core vision, primary users, main features missing
   - Moderate: secondary features, some goals missing
   - Informational: minor details missing
5. **Record coverage map** and gap summary

---

## Step 6: Measurability

### Goal
Validate that all FRs and NFRs are measurable and testable.

### FR Checks
For each Functional Requirement:
- Does it follow "[Actor] can [capability]" format?
- No subjective adjectives (easy, fast, simple, intuitive)?
- No vague quantifiers (multiple, several, some, many)?
- No implementation details (technology names, library names)?

### NFR Checks
For each Non-Functional Requirement:
- Has a specific, measurable metric?
- Includes measurement method or context?
- Avoids unmeasurable claims ("the system shall be scalable")?

### Severity
- Critical: >10 total violations
- Warning: 5-10 violations
- Pass: <5 violations

**Record findings** with violation counts, examples, and line references.

---

## Step 7: Traceability

### Goal
Validate the traceability chain: Vision -> Success Criteria -> User Journeys -> FRs.

### Chain Checks

1. **Executive Summary -> Success Criteria** — does vision align with defined success?
2. **Success Criteria -> User Journeys** — is each success criterion supported by a user journey?
3. **User Journeys -> FRs** — does each FR trace back to a user journey?
4. **Scope -> FRs** — do MVP scope items align with FRs?

### Orphan Detection
- FRs not traceable to any user journey or business objective
- Success criteria not supported by user journeys
- User journeys without supporting FRs

### Severity
- Critical: orphan FRs exist (requirements without traceable source)
- Warning: chain gaps identified
- Pass: traceability chain intact

**Record traceability matrix** and orphan list.

---

## Step 8: Implementation Leakage

### Goal
Ensure FRs and NFRs specify WHAT, not HOW.

### Scan Categories
- **Frontend frameworks**: React, Vue, Angular, Svelte, Next.js, etc.
- **Backend frameworks**: Express, Django, Rails, Spring, etc.
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, etc.
- **Cloud platforms**: AWS, GCP, Azure, Cloudflare, Vercel, etc.
- **Infrastructure**: Docker, Kubernetes, Terraform, etc.
- **Libraries**: Redux, axios, lodash, etc.

### Distinction
- **Capability-relevant** (acceptable): "API consumers can access data via REST endpoints" — API/REST describes the capability
- **Implementation leakage** (violation): "React components fetch data using Redux" — prescribes HOW to build

### Severity
- Critical: >5 leakage violations
- Warning: 2-5 violations
- Pass: <2 violations

**Record findings** by category with examples.

---

## Step 9: Domain Compliance (Conditional)

### Goal
For complex domains, validate domain-specific requirements are present.

### Steps

1. **Check domain classification** from PRD (frontmatter or content)
2. **If low complexity** — record "N/A, standard domain" and skip
3. **If medium/high complexity**, check for required domain sections:
   - **Healthcare**: HIPAA compliance, patient safety, clinical requirements, audit logging
   - **Fintech**: PCI-DSS, AML/KYC, SOX controls, financial audit trails, fraud prevention
   - **GovTech**: WCAG 2.1 AA accessibility, Section 508, FedRAMP, data residency, procurement compliance
   - **E-Commerce**: PCI-DSS for payments, inventory accuracy, tax calculation
4. **Build compliance matrix** — required vs present for the specific domain

### Severity
- Critical: missing regulatory sections
- Warning: incomplete compliance documentation
- Pass: all required sections present

---

## Step 10: Project Type Validation (Conditional)

### Goal
Validate project-type specific sections are present and irrelevant sections are absent.

### Steps

1. **Identify project type** from PRD classification
2. **Check required sections** for that type (e.g., API backend needs endpoint specs, auth model)
3. **Check excluded sections** that should NOT be present (e.g., API backend should skip UX/visual design)
4. **Build compliance table**: required sections present/missing, excluded sections absent/present

### Severity
- Critical: required sections missing
- Warning: incomplete required sections
- Pass: all required sections present, no excluded sections found

---

## Step 11: SMART Validation

### Goal
Score Functional Requirements on SMART criteria.

### Scoring (1-5 scale per FR)
- **Specific** (1-5): clear, unambiguous, well-defined?
- **Measurable** (1-5): quantifiable, testable?
- **Attainable** (1-5): realistic within constraints?
- **Relevant** (1-5): aligned with user needs and business objectives?
- **Traceable** (1-5): links to user journey or business objective?

### Steps
1. Extract all FRs
2. Score each on all 5 SMART criteria
3. Flag any FR with score < 3 in any category
4. Provide improvement suggestions for low-scoring FRs
5. Calculate overall quality: percentage of FRs with all scores >= 3

### Severity
- Critical: >30% of FRs flagged
- Warning: 10-30% flagged
- Pass: <10% flagged

**Record scoring table** and improvement suggestions.

---

## Step 12: Holistic Quality

### Goal
Assess the PRD as a cohesive, compelling document.

### Evaluation Dimensions

**Document Flow & Coherence**:
- Does it tell a cohesive story?
- Smooth transitions between sections?
- Consistent voice and tone?

**Dual Audience Effectiveness**:
- For humans: executive-friendly? Developer clarity? Designer clarity?
- For LLMs: machine-readable structure? Can LLMs generate UX/architecture/epics from this?

**Quality Rating** (1-5):
- 5 Excellent: exemplary, ready for production use
- 4 Good: strong with minor improvements
- 3 Adequate: acceptable but needs refinement
- 2 Needs Work: significant gaps
- 1 Problematic: major flaws

**Top 3 Improvements**: identify the 3 most impactful changes to make this a great PRD.

---

## Step 13: Report Generation

### Goal
Compile all findings into a comprehensive validation report.

### Report Structure

```markdown
# PRD Validation Report

**PRD Validated:** [path]
**Date:** [date]
**Overall Status:** [Pass / Warning / Critical]

## Quick Results

| Check | Status | Severity |
|-------|--------|----------|
| Structure | [classification] | [severity] |
| Information Density | [violations] | [severity] |
| Brief Coverage | [coverage %] | [severity] |
| Measurability | [violations] | [severity] |
| Traceability | [issues] | [severity] |
| Implementation Leakage | [violations] | [severity] |
| Domain Compliance | [status] | [severity] |
| Project Type | [compliance %] | [severity] |
| SMART Quality | [% acceptable] | [severity] |
| Holistic Quality | [rating/5] | [label] |
| Completeness | [%] | [severity] |

## Critical Issues
[List all critical findings]

## Warnings
[List all warnings]

## Strengths
[List what the PRD does well]

## Top 3 Improvements
1. [Most impactful improvement]
2. [Second most impactful]
3. [Third most impactful]

## Detailed Findings
[Full findings from each validation step]

## Recommendation
[Overall recommendation based on findings]
```

### Final Steps

1. **Save the validation report** as a markdown file alongside the PRD
2. **Present summary** to user conversationally — overall status, critical issues, strengths, top improvements
3. **Offer next steps**:
   - Review detailed findings section by section
   - Use the edit-prd skill to systematically address issues
   - Fix simple items immediately (anti-patterns, filler phrases, missing headers)
   - Exit and work on improvements independently
