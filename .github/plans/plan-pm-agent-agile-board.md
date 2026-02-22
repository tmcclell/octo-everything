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

## Part 5: Project Views (ADO Agile Equivalents)

GitHub Projects V2 views must be configured in the UI (no API support for view creation).
Open the project at: https://github.com/users/tmcclell/projects/12

### View 1: "Backlog" (Table Layout) — mirrors ADO Backlog View

**Purpose:** Flat prioritized list of all work items, like ADO's backlog view with drag-and-drop reordering.

**Layout:** Table
**Columns to show:** Title, Status, Priority, Area, Sprint, Estimate, Labels, Assignees
**Group by:** None (flat list sorted by priority)
**Filter:** `-status:Closed` (hide completed work)
**Sort:** Priority ascending, then Estimate descending

This mirrors ADO's **Product Backlog** — a ranked list where the PM (Martinez) manages priority order, assigns items to sprints, and refines acceptance criteria.

### View 2: "Sprint Board" (Board Layout) — mirrors ADO Kanban/Taskboard

**Purpose:** Kanban-style board showing cards flowing through workflow stages.

**Layout:** Board
**Column field:** Status (New → Ready → Active → In Review → Closed)
**Card fields:** Title, Priority, Estimate, Area, Assignees, Labels
**Filter:** Sprint = current sprint (e.g., `sprint:"Sprint 1 - Foundation"`)
**Swimlanes (Group by):** Area (SPACE, Copilot, Infrastructure, DevOps)

This mirrors ADO's **Kanban Board** — cards move across columns as work progresses. The swimlanes by Area replicate ADO's ability to see work grouped by Area Path.

### View 3: "Roadmap" (Roadmap Layout) — mirrors ADO Delivery Plans

**Purpose:** Timeline view showing work items across sprints, for cross-sprint planning.

**Layout:** Roadmap
**Date field:** Sprint (iteration-based timeline)
**Group by:** Area
**Card fields:** Title, Priority, Estimate, Status
**Filter:** None (show all items including closed for historical view)

This mirrors ADO's **Delivery Plans** — a calendar/timeline view showing when work is scheduled across iterations. Useful for stakeholder communication and release planning.

### View 4: "Current Sprint" (Table Layout) — mirrors ADO Sprint Backlog

**Purpose:** Focused table view of only current sprint items, with detail for daily standups.

**Layout:** Table
**Columns:** Title, Status, Priority, Estimate, Assignees, Labels, Linked PRs
**Filter:** `sprint:"Sprint 1 - Foundation"` (update per sprint)
**Group by:** Status
**Sort:** Priority ascending

This mirrors ADO's **Sprint Backlog** view — shows committed work for the current iteration, grouped by status for standup reviews.

### View 5: "By Area" (Board Layout) — mirrors ADO Area Path filtering

**Purpose:** Board view grouped by feature area for cross-functional visibility.

**Layout:** Board
**Column field:** Status
**Filter:** None
**Swimlanes (Group by):** Area
**Card fields:** Title, Sprint, Estimate, Assignees

This mirrors ADO's board filtered by **Area Path** — useful for area leads to see all work in their domain.

### How to Create These Views

1. Open https://github.com/users/tmcclell/projects/12
2. Click the **+** tab next to existing views
3. Select layout (Table, Board, or Roadmap)
4. Name the view
5. Use the **Filter** bar to set filters
6. Use **Group by** dropdown to set grouping
7. Use **Sort** to configure ordering
8. Click the column header **+** to add/remove visible fields
9. Changes auto-save

### Recommended Project Workflows (Automation)

In Project Settings → Workflows, enable:
- **Item closed** → Set Status to "Closed"
- **Item reopened** → Set Status to "New"
- **Pull request merged** → Set Status to "Closed"

These replicate ADO's automatic state transitions.
