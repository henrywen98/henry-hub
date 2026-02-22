# Expert Review Output Templates

## Individual Expert Review Template

Each expert must produce their review in this format:

### 🔍 [Agent Role] Review

**Reviewer**: [Role Name]
**Experience**: [Years] years in [Domain]
**Review Focus**: [Primary focus area]

---

#### ✅ Strengths
- [Specific strength with reference to PRD section]
- [Another strength]

#### ⚠️ Risks & Structural Weaknesses
- **[Risk Title]**: [Description of the risk, which PRD section it relates to, and why it matters]
- Severity: 🔴 Critical / 🟡 High / 🟠 Medium / 🟢 Low

#### ❗ Hidden or Future Risks
- [Risk that may not be obvious now but will emerge at scale or over time]

#### ❓ Critical Questions
1. [Question that must be answered before implementation]
2. [Question about unclear requirements]

#### 💡 Concrete Improvement Actions
1. **[Action Title]**: [Specific, actionable recommendation with enough detail to implement]
2. **[Action Title]**: [Another recommendation]

#### 🔴 Overall Severity Assessment
- **Severity Level**: Critical / High / Medium / Low
- **Recommendation**: GO / CONDITIONAL GO / NO-GO
- **Confidence**: [XX]%
- **Key Condition** (if CONDITIONAL): [What must change]

---

## Stress Test Report Template

### 💣 Red Team Stress Test Report

For each stress scenario:

#### Scenario: [Scenario Name]
- **Pressure Applied**: [Description of the stress condition]
- **Failure Point**: [What breaks first]
- **Why It Breaks**: [Root cause analysis]
- **Blast Radius**: [What else is affected when it breaks]
- **Time to Failure**: [Estimated time/load before failure]
- **Recommended Fix**: [Specific mitigation strategy]
- **Fix Complexity**: Simple / Moderate / Complex / Architectural Change

---

## Risk Matrix Template

### Risk Matrix

| # | Risk | Category | Impact | Likelihood | Owner Role | Mitigation | Status |
|---|------|----------|--------|------------|------------|------------|--------|
| 1 | [Risk description] | Tech/AI/Security/Cost/Product/Ops | Critical/High/Medium/Low | High/Medium/Low | [Which expert] | [Strategy] | Open |

Categories must cover: Technical, AI/Data, Security/Compliance, Cost, Product, Operations

---

## Final Verdict Template

### 🧾 Final Review Verdict

**Decision**: GO / CONDITIONAL GO / NO-GO
**Confidence Level**: [XX]%
**Review Date**: [Date]

#### Expert Votes
| Expert | Vote | Confidence | Key Concern |
|--------|------|------------|-------------|
| [Role] | GO/CONDITIONAL/NO-GO | XX% | [One-line concern] |

#### Top Blocking Risks
1. [Most critical risk]
2. [Second critical risk]
3. [Third critical risk]

#### System Maturity Level
**Assessment**: Prototype / Beta / Production-Ready

#### Recommended Next Steps
1. [Immediate action needed]
2. [Short-term improvement]
3. [Long-term consideration]
