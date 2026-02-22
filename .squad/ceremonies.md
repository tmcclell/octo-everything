# Ceremonies

> Team meetings that happen before or after work. Each squad configures their own.

## Design Review

| Field | Value |
|-------|-------|
| **Trigger** | auto |
| **When** | before |
| **Condition** | multi-agent task involving 2+ agents modifying shared systems |
| **Facilitator** | lead |
| **Participants** | all-relevant |
| **Time budget** | focused |
| **Enabled** | ✅ yes |

**Agenda:**
1. Review the task and requirements
2. Agree on interfaces and contracts between components
3. Identify risks and edge cases
4. Assign action items

---

## Retrospective

| Field | Value |
|-------|-------|
| **Trigger** | auto |
| **When** | after |
| **Condition** | build failure, test failure, or reviewer rejection |
| **Facilitator** | lead |
| **Participants** | all-involved |
| **Time budget** | focused |
| **Enabled** | ✅ yes |

**Agenda:**
1. What happened? (facts only)
2. Root cause analysis
3. What should change?
4. Action items for next iteration

---

## Backlog Refinement

| Field | Value |
|-------|-------|
| **Trigger** | auto |
| **When** | before |
| **Condition** | sprint boundary or 5+ items in New column |
| **Facilitator** | martinez |
| **Participants** | lead, martinez |
| **Time budget** | focused |
| **Enabled** | ✅ yes |

**Agenda:**
1. Triage items in New → write acceptance criteria, assign labels and priority
2. Estimate story points with input from relevant specialists
3. Move refined items from New → Ready
4. Remove or defer low-value items

---

## Sprint Planning

| Field | Value |
|-------|-------|
| **Trigger** | auto |
| **When** | before |
| **Condition** | sprint start (every 2 weeks) or Ready column has 3+ items |
| **Facilitator** | martinez |
| **Participants** | all-active |
| **Time budget** | focused |
| **Enabled** | ✅ yes |

**Agenda:**
1. Review sprint goal and capacity
2. Select items from Ready → Active based on priority and capacity
3. Assign items to agents (respecting WIP limit of 3 per agent)
4. Confirm Definition of Done for each item
