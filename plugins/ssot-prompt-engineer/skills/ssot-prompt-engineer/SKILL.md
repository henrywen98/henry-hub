---
name: ssot-prompt-engineer
description: "SSOT-Driven Prompt Engineering: Extract transformation rules from input-output pairs, codify them as a Single Source of Truth (SSOT), then derive prompts and tooling from the SSOT. Use when the user wants to: (1) analyze how inputs map to outputs and extract the underlying rules, (2) create a prompt toolkit from existing examples or templates, (3) reverse-engineer an SOP from sample inputs and outputs, (4) build reusable prompt systems where rules are separated from prompt templates, (5) formalize tacit domain knowledge into structured generation rules. Triggers: 'extract rules', 'create SSOT', 'reverse engineer the process', 'build prompt from examples', 'formalize the SOP', 'make a prompt toolkit', 'SSOT to prompt'."
---

# SSOT-Driven Prompt Engineering

A methodology for creating reliable, maintainable AI prompt systems by first extracting transformation rules as a Single Source of Truth (SSOT), then deriving all prompts and tooling from it.

## Core Principle

```
Never write prompts directly. Extract the rules first.

Input Samples ──┐
                 ├──▶ SSOT (Rules) ──▶ System Prompt
Output Samples ──┘                  ──▶ User Prompt Templates
                                    ──▶ Conversion Scripts
                                    ──▶ Quality Checklists
```

**Prompt is not the source. SSOT is the source. Prompt is a projection of SSOT.**

## Methodology: 5-Phase Process

### Phase 1: Collect I/O Pairs

Gather concrete input-output examples from the user's domain:

- **Inputs**: Source documents, raw data, requirements, etc.
- **Outputs**: The desired deliverables (reports, test cases, code, etc.)
- **Existing templates**: Any formatting/style references for the output

Ask the user:
- "Can you show me a real input and its corresponding output?"
- "Is there an existing template or style guide for the output?"
- "What are the quality criteria for a good output?"

### Phase 2: Reverse-Engineer Transformation Rules

Analyze I/O pairs to extract the mapping logic. Work through three levels:

**Level 1 — Structure Mapping**
How does the input structure map to the output structure?
- What sections/fields from input become what sections/fields in output?
- What is generated (not from input) but from conventions/templates?
- What is the output's organizational hierarchy?

**Level 2 — Content Transformation Rules**
For each mapping, what are the specific rules?
- Fixed templates (always the same regardless of input)
- Conditional logic (if X in input, then Y in output)
- Enumeration rules (for each item in input, generate N items in output)
- Type-based rules (input type determines output pattern)

**Level 3 — Quality Constraints**
What makes an output "correct"?
- Completeness: every input element has corresponding output
- Consistency: naming conventions, formatting, terminology
- Traceability: output can be traced back to input source

Document these rules as the **SSOT** — a structured, hierarchical rule set.

### Phase 3: Write the SSOT Document

Structure the SSOT as a standalone, self-contained document:

```markdown
# [Domain] SSOT

## 1. Input Structure Definition
   (What the input looks like, its components)

## 2. Output Structure Definition
   (What the output looks like, its format/columns/schema)

## 3. Transformation Rules
   (Hierarchical rules, organized by layer/category)

   ### Rule Layer 1: ...
   ### Rule Layer 2: ...
   ...

## 4. Type-Specific Templates
   (For each input type → output pattern mapping)

## 5. Quality Constraints
   (Completeness, consistency, traceability requirements)

## 6. Naming & Style Conventions
   (Formatting, terminology, numbering rules)
```

Key principles for SSOT writing:
- **Self-contained**: Another person (or AI) can follow it without additional context
- **Unambiguous**: Each rule has clear trigger conditions and outputs
- **Hierarchical**: Rules organized from general to specific
- **Testable**: Each rule can be verified against I/O pairs

### Phase 4: Derive Prompts from SSOT

Generate all prompts by projecting the SSOT into the target format:

**System Prompt** = SSOT rules reformulated as AI instructions:
- Role definition + output format + complete rule set + templates + constraints + few-shot examples
- The System Prompt should embed the SSOT, not reference it

**User Prompt Templates** = Parameterized input slots:
- Structured template with `{placeholders}` for user's specific input
- Control parameters (scope, quantity expectations, special focus areas)

**Multi-step strategy** (for complex domains):
- Step 1 prompt: Framework/outline generation (broad view)
- Step 2 prompt: Detail generation per section (deep view)
- Each step's output feeds into the next step's input

### Phase 5: Build Tooling & Validate

Create supporting tools and validate the full pipeline:

1. **Conversion tools**: Scripts to transform AI output into final deliverable format
2. **Validation checklist**: Verify output against SSOT rules
3. **Pilot test**: Run the full pipeline on a real example, compare with existing reference output
4. **Iterate**: Adjust SSOT rules based on gaps found during validation

## Output Deliverables

A complete SSOT-Driven Prompt Toolkit typically includes:

| Deliverable | Purpose |
|-------------|---------|
| `ssot.md` | The Single Source of Truth — all transformation rules |
| `system_prompt.md` | System Prompt derived from SSOT |
| `user_prompt_step1.md` | User Prompt template for framework generation |
| `user_prompt_step2.md` | User Prompt template for detail generation |
| `example_*.md` | Filled-in examples showing how to use the templates |
| `convert_*.*` | Script(s) to convert AI output to final format |
| `README.md` | Usage guide explaining the workflow |

## When to Use Multi-Step vs Single-Step

| Scenario | Approach |
|----------|----------|
| Output < 50 items, simple rules | Single-step: one prompt generates everything |
| Output 50-200 items, moderate rules | Two-step: framework first, then details |
| Output 200+ items or complex conditionals | Multi-step: split by section/category |
| Multiple output types from same input | Parallel: separate prompts per output type |

## Anti-Patterns to Avoid

1. **Writing prompts before understanding rules** — Always extract SSOT first
2. **Embedding rules only in prompts** — Rules should live in SSOT; prompts derive from it
3. **Vague transformation rules** — "Generate appropriate test cases" vs "For each required field, generate: empty validation, type validation, boundary validation"
4. **Missing few-shot examples** — Always include 2-3 concrete examples in system prompt
5. **Monolithic prompt** — Split into system (rules) + user (input) + control (parameters)
