# Plan: Add PM Agent to Squad with Agile GitHub Project Board

## Problem Statement

The squad currently has 7 members (Lead, Backend, Frontend, Data, Tester, Scribe, Monitor) but no Product Manager. The user wants a PM agent that manages requirements and tasks using agile methodology via GitHub Projects, with a board modeled after Azure DevOps Agile process.

## Approach

Add a new "PM" squad agent and configure a GitHub Project board that mirrors an Azure DevOps Agile board. The PM agent will own the backlog, sprint planning, issue lifecycle, and board hygiene. GitHub Projects will be the single source of truth for work items.

---

## Part 1: Create the PM Squad Agent

### 1A. Agent Definition — `.squad/agents/martinez/charter.md`

Name the PM agent **Martinez** (from The Martian universe, consistent with existing cast). Martinez was the mission pilot — good fit for someone who navigates the team's direction.

The charter will define:
- **Role:** Product Manager
- **Specialization:** Requirements, backlog grooming, sprint planning, acceptance criteria, stakeholder communication
- **Boundaries:**
  - Owns the backlog and GitHub Project board
  - Writes user stories, acceptance criteria, and sprint goals
  - Does NOT write code or make architecture decisions (delegates to Lewis/specialists)
  - Triages incoming issues and prioritizes work
- **Working style:** Agile ceremonies, ADO-style board management

### 1B. Update Team Files

- **`.squad/team.md`** — Add Martinez to the Members table
- **`.squad/routing.md`** — Add routing rules for PM-related signals
- **`.squad/casting/registry.json`** — Register Martinez in the cast registry

---

## Part 2: GitHub Project Board (ADO Agile Style)

### 2A. Board Structure

Mirror the Azure DevOps Agile process template with these columns/statuses:

| Column | ADO Equivalent | Description |
|--------|---------------|-------------|
| **New** | New | Newly created, not yet triaged |
| **Ready** | Approved | Triaged, refined, ready to be picked up |
| **Active** | Active / Committed | In current sprint, actively being worked |
| **In Review** | (custom) | PR submitted, awaiting code review |
| **Closed** | Done / Closed | Completed and verified |

### 2B. Work Item Types (Issue Labels)

Map ADO work item types to GitHub labels:

| ADO Type | GitHub Label | Color | Description |
|----------|-------------|-------|-------------|
| Epic | `epic` | `#7057ff` (purple) | Large feature spanning multiple stories |
| User Story | `user-story` | `#0e8a16` (green) | Deliverable from user perspective |
| Task | `task` | `#1d76db` (blue) | Technical work item |
| Bug | `bug` | `#d73a4a` (red) | Defect to fix |
| Spike | `spike` | `#fbca04` (yellow) | Research/investigation |

### 2C. Custom Fields (GitHub Project)

| Field | Type | Values | ADO Equivalent |
|-------|------|--------|---------------|
| Priority | Single select | P0-Critical, P1-High, P2-Medium, P3-Low | Priority |
| Story Points | Number | 1, 2, 3, 5, 8, 13 | Story Points |
| Sprint | Iteration | Sprint 1, Sprint 2, ... | Iteration Path |
| Area | Single select | SPACE, Copilot, Infrastructure, DevOps | Area Path |

### 2D. Issue Templates

Create GitHub issue templates for each work item type:
- **User Story** — `As a [persona], I want [goal] so that [benefit]` + acceptance criteria
- **Bug Report** — Repro steps, expected vs actual, severity
- **Task** — Description, technical notes, definition of done
- **Spike** — Question to answer, timebox, expected output

---

## Part 3: PM Agent Charter — Agile Ceremonies

Define the PM's ceremony responsibilities:

| Ceremony | Frequency | PM Role |
|----------|-----------|---------|
| Backlog Refinement | Before each sprint | Writes/refines stories, sets priority, adds acceptance criteria |
| Sprint Planning | Sprint start | Selects items from Ready → Active, sets sprint goal |
| Daily Standup | Per work session | Reviews board, unblocks, updates status |
| Sprint Review | Sprint end | Validates done items meet acceptance criteria |
| Retrospective | Sprint end | Participates (Lewis facilitates) |

---

## Part 4: Implementation Todos

1. ✅ **create-pm-charter** — Create `.squad/agents/martinez/charter.md` with full PM role definition
2. ✅ **create-pm-history** — Create `.squad/agents/martinez/history.md` (empty starting file)
3. ✅ **update-team-md** — Add Martinez to `.squad/team.md` members table
4. ✅ **update-routing** — Add PM routing rules to `.squad/routing.md`
5. ✅ **update-casting-registry** — Register Martinez in `.squad/casting/registry.json`
6. ✅ **create-issue-templates** — Create GitHub issue templates (user-story, bug, task, spike) in `.github/ISSUE_TEMPLATE/`
7. ✅ **create-project-board** — Updated existing Project #12 with ADO-style columns and Area field
8. ✅ **create-labels** — Created work-item-type labels (epic, user-story, task, spike) + priority labels
9. ✅ **update-ceremonies** — Added Backlog Refinement and Sprint Planning to `.squad/ceremonies.md`
10. ✅ **seed-backlog** — 18 existing issues already linked in Project #12

---

## Recommendations

1. **Sprint cadence:** 2-week sprints recommended for this project size
2. **WIP limits:** Cap "Active" column at 3 items per agent to prevent context-switching
3. **Definition of Done:** PR merged + tests pass + acceptance criteria verified by PM (Martinez)
4. **Linking convention:** Every PR references an issue (`Fixes #N`), Martinez verifies before moving to Closed
5. **Board views:** Create a "Current Sprint" filtered view + "Backlog" view (like ADO's backlog vs board views)
6. **Automation:** Use GitHub Project workflows to auto-move items (e.g., issue closed → Closed column, PR opened → In Review)

---

## Part 5: Project Views (Semantic Kernel / ADO Agile Style)

Modeled after the Microsoft Semantic Kernel GitHub Project board.
Open the project at: https://github.com/users/tmcclell/projects/12

### Board Statuses (SK-style sprint-prefixed)

| Status | Color | Description |
|--------|-------|-------------|
| **Bug** | Red | Bugs list |
| **Backlog** | Gray | Product backlog — not yet planned for a sprint |
| **Sprint: Planned** | Blue | What is planned to happen during this sprint |
| **Sprint: In Progress** | Orange | This is actively being worked on |
| **Sprint: In Review** | Purple | SLA 3 Days. PR submitted, awaiting code review |
| **Sprint: Done** | Green | Completed and verified in sprint |
| **Released** | Green | Shipped to production |
| **Please Close** | Pink | Ready for final verification and closure |

### Views (Created via REST API)

All views were created programmatically using the **GitHub Projects V2 REST API** (shipped September 2025).

**API Endpoint:**
```
POST /users/{user_id}/projectsV2/{project_number}/views
```

**Documentation:** https://docs.github.com/en/rest/projects/views

**Request body:**
```json
{
  "name": "View Name",
  "layout": "table | board | roadmap",
  "filter": "status:Backlog label:bug ...",
  "visible_fields": [260536183, 260536184, ...]
}
```

**Field IDs for this project (#12):**

| Field | REST ID | Purpose |
|-------|---------|---------|
| Title | 260536183 | Item title |
| Assignees | 260536184 | Who's working on it |
| Status | 260536185 | Board column |
| Labels | 260536186 | Work item type |
| Linked PRs | 260536187 | Associated pull requests |
| Milestone | 260536188 | Release milestone |
| Repository | 260536189 | Source repo |
| Reviewers | 260536190 | Code reviewers |
| Priority | 260536698 | P0–P3 |
| Sprint | 260536699 | Sprint assignment |
| Estimate | 260536700 | Story points |
| Area | 260692740 | SPACE / Copilot / Infra / DevOps |

**Example `gh` CLI call:**
```powershell
$body = @{
    name = "Current Sprint"
    layout = "board"
    filter = 'sprint:"Sprint 1"'
    visible_fields = @(260536183, 260536184, 260536185, 260536698, 260536700)
} | ConvertTo-Json -Compress

echo $body | gh api -X POST "/users/tmcclell/projectsV2/12/views" --input -
```

> **Note:** The GraphQL API (`ProjectV2View` type) is read-only — there is no `createProjectV2View` mutation. View creation is only available via the REST API. For user-owned projects, classic PATs or OAuth tokens work; fine-grained PATs do NOT (per GitHub docs).

**Changelog:** https://github.blog/changelog/2025-09-11-a-rest-api-for-github-projects-sub-issues-improvements-and-more/

#### View 1: "Current Sprint" (Board Layout) ⭐ Default — [View #3](https://github.com/users/tmcclell/projects/12/views/3)

**Purpose:** Active sprint work — the primary working view.
**Layout:** Board
**Column field:** Status (Bug | Sprint: Planned | Sprint: In Progress | Sprint: In Review | Sprint: Done)
**Filter:** `-status:"No Status",Released,"Backlog","Please Close" sprint:@current`
**Group by:** Assignees
**Card fields:** Title, Priority, Estimate, Area, Labels

#### View 2: "Current Bugs" (Table Layout) — [View #4](https://github.com/users/tmcclell/projects/12/views/4)

**Purpose:** Bug triage and tracking for the current sprint.
**Layout:** Table
**Columns:** Title, Status, Priority, Area, Assignees, Sprint, Estimate
**Filter:** `status:Bug sprint:@current`
**Sort:** Priority ascending

#### View 3: "@Me" (Table Layout) — [View #5](https://github.com/users/tmcclell/projects/12/views/5)

**Purpose:** Personal view — items assigned to the current user.
**Layout:** Table
**Columns:** Title, Status, Priority, Sprint, Estimate, Area, Labels
**Filter:** `assignee:@me`
**Sort:** Status, then Priority

#### View 4: "Current Backlog" (Table Layout) — [View #6](https://github.com/users/tmcclell/projects/12/views/6)

**Purpose:** Backlog items for current iteration — sprint planning input.
**Layout:** Table
**Columns:** Title, Status, Priority, Area, Sprint, Estimate, Labels, Assignees
**Filter:** `status:Backlog,"Sprint: Planned" sprint:@current`
**Sort:** Priority ascending, Estimate descending

#### View 5: "Please Close" (Table Layout) — [View #7](https://github.com/users/tmcclell/projects/12/views/7)

**Purpose:** Items pending final verification before closure.
**Layout:** Table
**Columns:** Title, Status, Priority, Area, Assignees, Linked PRs
**Filter:** `status:"Please Close"`

#### View 6: "Bugs" (Table Layout) — [View #8](https://github.com/users/tmcclell/projects/12/views/8)

**Purpose:** All bugs across all sprints — defect tracking overview.
**Layout:** Table
**Columns:** Title, Status, Priority, Area, Sprint, Assignees, Estimate
**Filter:** `label:bug`
**Sort:** Priority ascending, Sprint

#### View 7: "Full Backlog" (Table Layout) — [View #9](https://github.com/users/tmcclell/projects/12/views/9)

**Purpose:** Entire product backlog for grooming and prioritization.
**Layout:** Table
**Columns:** Title, Status, Priority, Area, Sprint, Estimate, Labels, Assignees
**Filter:** `-status:Released,"Sprint: Done"`
**Sort:** Priority ascending

#### View 8: "Roadmap" (Roadmap Layout) — [View #10](https://github.com/users/tmcclell/projects/12/views/10)

**Purpose:** Timeline view across sprints for stakeholder communication.
**Layout:** Roadmap
**Date field:** Sprint
**Group by:** Area
**Card fields:** Title, Priority, Status, Estimate
**Filter:** None (show all for historical context)

#### View 9: "Previous Sprint" (Table Layout) — [View #11](https://github.com/users/tmcclell/projects/12/views/11)

**Purpose:** Last sprint's items for retrospective review.
**Layout:** Table
**Columns:** Title, Status, Priority, Estimate, Area, Assignees
**Filter:** `sprint:"Sprint 1 - Foundation"` (update each sprint)
**Group by:** Status

### Managing Views

Views were created via the REST API (see above). To **modify** views after creation:

- **Filters, sorting, grouping** — Edit in the GitHub UI (the REST API supports creation but not update)
- **Delete a view** — `gh api -X DELETE "/users/tmcclell/projectsV2/12/views/{view_number}"`
- **Recreate a view** — Delete then POST again with updated params
- **List views** — `gh api graphql -f query='{ node(id: "PVT_kwHOAzARAM4BP0TB") { ... on ProjectV2 { views(first: 20) { nodes { number name layout filter } } } } }'`

### Recommended Project Workflows (Automation)

In Project Settings → Workflows, enable:
- **Item closed** → Set Status to "Please Close"
- **Item reopened** → Set Status to "Backlog"
- **Pull request merged** → Set Status to "Sprint: Done"

---

## Part 6: API Reference & Extension Points

### Configuration

All project IDs, field IDs, view numbers, and CLI examples are stored in:
**`.github/project-config.json`** — single source of truth for automation scripts.

### Known Limitations

| Capability | REST API | GraphQL | Notes |
|-----------|----------|---------|-------|
| Create views | ✅ `POST /views` | ❌ No mutation | REST only (Sept 2025) |
| Delete views | ✅ `DELETE /views/{n}` | ❌ No mutation | REST only |
| Update view filter/sort/group | ❌ Not supported | ❌ Read-only | Must delete + recreate, or edit in UI |
| Read views | ✅ `GET /views` | ✅ `ProjectV2View` | Both work |
| Create/update fields | ✅ via `gh project field-create` | ✅ `createProjectV2Field` | Both work |
| Update item field values | N/A | ✅ `updateProjectV2ItemFieldValue` | GraphQL only |
| Token support (user projects) | Classic PAT ✅, OAuth ✅ | Classic PAT ✅, OAuth ✅ | Fine-grained PATs do NOT work for user-owned project view creation |

### Extension Opportunities

1. **`devmetrics/collectors/project_collector.py`** (NEW) — Collect board flow metrics (items per status, avg time in column, sprint velocity) via the REST API for project items
2. **`devmetrics/pages/3_project_dashboard.py`** (NEW) — Streamlit page showing board health: WIP limits, sprint burndown, cumulative flow diagram
3. **`.github/workflows/squad-triage.yml`** — After triage assigns a label, also set the project item's Status to "Sprint: Planned" via GraphQL `updateProjectV2ItemFieldValue`
4. **`.github/workflows/squad-issue-assign.yml`** — After assignment, update project item Priority/Sprint/Area fields
5. **Sprint carryover script** — On sprint end, update "Current Sprint" and "Previous Sprint" view filters via delete+recreate REST calls
6. **`devmetrics/collectors/github_client.py`** — Add Projects V2 REST methods (`list_views`, `create_view`, `delete_view`, `list_fields`) alongside existing PyGithub wrapper
