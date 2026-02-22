# Red Team Stress Test Scenarios

Apply each scenario to the PRD under review. For each, identify the failure point, why it breaks, blast radius, and recommended fix.

## Scenario 1: 10x User Growth
- **Condition**: User base grows 10x within 3 months
- **Test Focus**: Database queries, API rate limits, session management, caching layers
- **Key Questions**:
  - Which database queries become N+1 problems at scale?
  - Does the authentication system handle 10x concurrent sessions?
  - Are there hard-coded limits that silently fail?

## Scenario 2: Data Volume Explosion
- **Condition**: Data storage grows 100x (e.g., user-generated content, logs, analytics)
- **Test Focus**: Storage costs, query performance, backup/restore time, data migration
- **Key Questions**:
  - How long does a full backup take at 100x data?
  - Which aggregation queries become prohibitively slow?
  - Is there a data retention/archival strategy?

## Scenario 3: Multi-Tenant Enterprise Customers
- **Condition**: System must support isolated tenants with custom configurations
- **Test Focus**: Data isolation, tenant-specific customization, noisy neighbor problems
- **Key Questions**:
  - Is data physically or logically isolated?
  - Can one tenant's heavy usage impact others?
  - How are tenant-specific configurations managed?

## Scenario 4: Private Deployment (On-Premise)
- **Condition**: Customer requires self-hosted deployment behind their firewall
- **Test Focus**: External dependency coupling, license management, update mechanism
- **Key Questions**:
  - Which features depend on external SaaS services?
  - How are updates delivered to air-gapped environments?
  - What telemetry/monitoring works without internet?

## Scenario 5: Weak Network / High Latency
- **Condition**: Users in regions with 500ms+ latency, intermittent connectivity
- **Test Focus**: Optimistic UI, offline capability, data sync conflicts
- **Key Questions**:
  - Does the UI become unusable at 500ms latency?
  - What happens to in-flight requests when connectivity drops?
  - Are there race conditions in data synchronization?

## Scenario 6: AI Model Instability
- **Condition**: AI/LLM responses are slow (30s+), inconsistent, or unavailable
- **Test Focus**: Fallback mechanisms, timeout handling, graceful degradation
- **Key Questions**:
  - What is the user experience when AI is down for 1 hour?
  - Are AI responses validated before being shown to users?
  - Is there a fallback to non-AI functionality?
  - How are hallucinations detected and handled?

## Scenario 7: Upstream Dependency Failure
- **Condition**: Critical third-party service (payment, auth, CDN) goes down
- **Test Focus**: Circuit breakers, retry logic, graceful degradation, SLA cascading
- **Key Questions**:
  - Which features become completely unavailable?
  - Is there circuit breaker logic to prevent cascade failures?
  - What is the recovery procedure when the dependency returns?

## Scenario 8: Security Breach Attempt
- **Condition**: Sophisticated attacker targets the system
- **Test Focus**: Authentication bypass, privilege escalation, data exfiltration, injection attacks
- **Key Questions**:
  - Is there defense in depth or single point of failure in auth?
  - Are API endpoints properly authorized (not just authenticated)?
  - Is sensitive data encrypted at rest and in transit?
  - Is there audit logging sufficient for forensic analysis?

## Scenario 9: Team Scaling
- **Condition**: Development team grows from 5 to 50 engineers
- **Test Focus**: Code modularity, service boundaries, CI/CD scalability, onboarding complexity
- **Key Questions**:
  - Can teams work on features independently without merge conflicts?
  - Is the architecture modular enough for parallel development?
  - How long does it take a new engineer to make their first contribution?

## Scenario 10: Regulatory Compliance Change
- **Condition**: New regulation requires data residency, right to deletion, or audit trails
- **Test Focus**: Data portability, deletion cascades, audit log completeness, cross-border data flow
- **Key Questions**:
  - Can all user data be exported in a standard format?
  - Can a specific user's data be completely deleted (including backups)?
  - Are all data access events logged for audit purposes?
