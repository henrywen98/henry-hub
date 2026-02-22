# Expert Roundtable Debate Protocol

## Core Principles

1. **No surface-level agreement** — Experts must substantiate every position with evidence
2. **Mandatory challenges** — Each expert must challenge at least 2 other experts per round
3. **Reference specifics** — All arguments must reference specific PRD sections or review findings
4. **Expose trade-offs** — Every architectural or product decision has trade-offs; name them
5. **No polite deflection** — "I agree with [expert]" is not valid without adding new insight

## Round 1: Cross-Challenge

### Purpose
Surface conflicts and disagreements between expert reviews.

### Process
1. Team Leader broadcasts all 13 expert reviews to all agents
2. Each expert reads other reviews and identifies:
   - Points of disagreement with specific experts
   - Overlooked risks that other experts missed
   - Conflicting recommendations that cannot coexist
3. Each expert sends challenges via SendMessage to relevant experts
4. Challenged experts must respond with counter-arguments

### Leader Actions
- Monitor incoming messages
- Track disputes as they emerge
- Identify which disputes are substantive vs. superficial
- Prepare dispute summary for Round 2

### Expected Output per Expert
- At least 2 challenges to other experts (via SendMessage)
- Responses to any challenges received
- Updated risk assessment based on other experts' findings

## Round 2: Deep Dive on Disputes

### Purpose
Resolve or document the top disputes from Round 1.

### Process
1. Team Leader extracts top 5 unresolved disputes from Round 1
2. For each dispute, Leader sends targeted questions to the 2-3 most relevant experts
3. Experts debate directly via SendMessage
4. Leader guides toward one of:
   - **Consensus**: Experts agree on a resolution
   - **Documented Trade-off**: Experts agree to disagree, trade-off is documented
   - **Escalation**: Dispute requires user/stakeholder decision

### Dispute Format
```
Dispute #[N]: [Title]
Parties: [Expert A] vs [Expert B]
Core Question: [What is the fundamental disagreement?]
Expert A Position: [Summary]
Expert B Position: [Summary]
Resolution: Consensus / Trade-off / Escalation
Outcome: [What was decided or documented]
```

### Leader Actions
- Send dispute summaries to relevant experts
- Facilitate focused discussion (not broad broadcast)
- Time-box each dispute (2-3 message exchanges max)
- Document outcomes

## Round 3: Final Verdict

### Purpose
Collect final positions from all experts after incorporating debate insights.

### Process
1. Team Leader sends debate outcomes summary to all experts
2. Each expert submits final verdict:
   - **Vote**: GO / CONDITIONAL GO / NO-GO
   - **Confidence**: Percentage
   - **Key Condition**: (if CONDITIONAL) What must change
   - **Remaining Concerns**: Top 1-2 unresolved issues
3. Leader tallies votes and determines overall verdict

### Verdict Rules
- If any expert votes NO-GO with confidence > 80%: Overall = CONDITIONAL GO at minimum
- If majority (>50%) vote NO-GO: Overall = NO-GO
- If all vote GO: Overall = GO
- Otherwise: Overall = CONDITIONAL GO with conditions list

### Leader Actions
- Request final verdicts from all experts
- Compile verdict table
- Calculate overall decision
- Document dissenting opinions

## Message Format Guidelines

### Challenge Message Format
```
I disagree with [Expert]'s assessment on [topic].

Their position: [Quote or summarize their position]
My counter-argument: [Why I disagree, with evidence]
What they overlooked: [Specific risk or consideration]
My recommendation: [What should be done instead]
```

### Response Format
```
Responding to [Expert]'s challenge on [topic].

Their concern: [Acknowledge what they raised]
My defense: [Why my original position holds, or how I've updated it]
Updated assessment: [If my position has changed]
Remaining disagreement: [What we still disagree on, if anything]
```
