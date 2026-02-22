# Data Schemas and Storage Documentation

## Overview

The DevMetrics Dashboard uses JSON files for data storage with a well-defined schema structure. All data files follow a consistent pattern with metadata and data arrays.

## Directory Structure

```
data/
├── space/                      # SPACE framework metrics
│   ├── pr_cycle_times.json
│   ├── review_turnaround.json
│   ├── rework_rates.json
│   └── wip_counts.json
├── copilot/                    # Copilot AI ROI metrics
│   ├── usage_metrics.json
│   ├── acceptance_rates.json
│   └── seat_utilization.json
├── project/                    # GitHub Project board metrics (PLANNED)
│   ├── board_snapshot.json     # Item-level field values snapshot
│   └── flow_metrics.json      # Cumulative flow & sprint velocity
├── snapshots/                  # Daily aggregated snapshots
│   └── YYYY-MM-DD.json        # One file per day
└── logs/                       # Application logs
    ├── app.log
    └── events.json
```

## Common Structure

All metric files share this base structure:

```json
{
  "metadata": {
    "last_updated": "2025-01-22T14:30:00Z",
    "version": "1.0",
    "source": "github_api" | "dummy_data"
  },
  "data": [
    // Array of metric records
  ]
}
```

## SPACE Metrics Schemas

### 1. PR Cycle Times (`space/pr_cycle_times.json`)

Tracks time from PR open to merge across repositories.

**Schema**: `schemas/pr_cycle_times_schema.json`

**Example Record**:
```json
{
  "pr_id": 1234,
  "pr_url": "https://github.com/org/repo/pull/1234",
  "repo": "org/repo-name",
  "title": "Add user authentication",
  "author": "octocat",
  "opened_at": "2025-01-20T09:00:00Z",
  "merged_at": "2025-01-21T15:30:00Z",
  "cycle_time_hours": 30.5,
  "lines_changed": 245,
  "commits": 3
}
```

**Key Fields**:
- `cycle_time_hours`: Core SPACE flow metric
- `repo`: Enables per-repo filtering
- `lines_changed`: Context for cycle time analysis

---

### 2. Review Turnaround (`space/review_turnaround.json`)

Measures time from PR open to first review.

**Schema**: `schemas/review_turnaround_schema.json`

**Example Record**:
```json
{
  "pr_id": 1234,
  "pr_url": "https://github.com/org/repo/pull/1234",
  "repo": "org/repo-name",
  "author": "octocat",
  "opened_at": "2025-01-20T09:00:00Z",
  "first_review_at": "2025-01-20T13:15:00Z",
  "first_reviewer": "reviewer-name",
  "turnaround_hours": 4.25,
  "review_type": "APPROVED"
}
```

**Key Fields**:
- `turnaround_hours`: Bottleneck indicator
- `review_type`: Quality signal (APPROVED, CHANGES_REQUESTED, COMMENTED)
- `first_reviewer`: Collaboration patterns

---

### 3. Rework Rates (`space/rework_rates.json`)

Weekly aggregation of PRs requiring changes vs clean merges.

**Schema**: `schemas/rework_rates_schema.json`

**Example Record**:
```json
{
  "week_start": "2025-01-20",
  "repo": "org/repo-name",
  "total_merged": 15,
  "changes_requested": 4,
  "approved_first_time": 11,
  "rework_rate": 0.267
}
```

**Key Fields**:
- `rework_rate`: Quality metric (0.0 = perfect, 1.0 = all rework)
- `week_start`: Monday of the week for trending
- Leave `repo` null for org-wide aggregation

---

### 4. WIP Counts (`space/wip_counts.json`)

Daily snapshot of open PRs (Work in Progress).

**Schema**: `schemas/wip_counts_schema.json`

**Example Record**:
```json
{
  "date": "2025-01-22",
  "repo": "org/repo-name",
  "open_prs": 8,
  "draft_prs": 2,
  "ready_prs": 6
}
```

**Key Fields**:
- `open_prs`: Total WIP count
- `draft_prs` vs `ready_prs`: Flow state breakdown
- Leave `repo` null for org-wide total

---

## Copilot Metrics Schemas

### 5. Usage Metrics (`copilot/usage_metrics.json`)

Daily Copilot usage and engagement.

**Schema**: `schemas/usage_metrics_schema.json`

**Example Record**:
```json
{
  "date": "2025-01-22",
  "total_active_users": 85,
  "total_engaged_users": 72,
  "total_code_suggestions": 12450,
  "total_code_acceptances": 3890,
  "total_code_lines_suggested": 48200,
  "total_code_lines_accepted": 15300,
  "total_chat_turns": 540,
  "breakdown": {
    "by_language": {
      "python": {"suggestions": 4500, "acceptances": 1400},
      "javascript": {"suggestions": 3200, "acceptances": 1100}
    },
    "by_editor": {
      "vscode": {"suggestions": 8000, "acceptances": 2600},
      "jetbrains": {"suggestions": 2500, "acceptances": 800}
    }
  }
}
```

**Key Fields**:
- `total_engaged_users`: Key adoption metric (accepted suggestions or used chat)
- `total_code_suggestions` / `acceptances`: Raw counts for acceptance rate
- `breakdown`: Optional detailed analysis by language/editor

---

### 6. Acceptance Rates (`copilot/acceptance_rates.json`)

Daily acceptance rate calculations derived from usage metrics.

**Schema**: `schemas/acceptance_rates_schema.json`

**Example Record**:
```json
{
  "date": "2025-01-22",
  "suggestions": 12450,
  "acceptances": 3890,
  "acceptance_rate": 0.312,
  "lines_suggested": 48200,
  "lines_accepted": 15300,
  "lines_acceptance_rate": 0.317
}
```

**Key Fields**:
- `acceptance_rate`: Primary quality/value metric (typically 25-35%)
- `lines_acceptance_rate`: Alternative metric (lines vs suggestions)

---

### 7. Seat Utilization (`copilot/seat_utilization.json`)

Daily seat assignment and usage tracking.

**Schema**: `schemas/seat_utilization_schema.json`

**Example Record**:
```json
{
  "date": "2025-01-22",
  "total_seats": 100,
  "active_seats": 85,
  "inactive_seats": 15,
  "utilization_rate": 0.85,
  "cost_per_seat": 19.0,
  "total_cost": 1900.0
}
```

**Key Fields**:
- `utilization_rate`: Cost efficiency metric
- `active_seats`: Activity in last 28 days
- `cost_per_seat` / `total_cost`: ROI context

---

## Planned: Project Board Metrics

> **Status:** Not yet implemented. Schema defined here for future `project_collector.py`.

The GitHub Projects V2 REST API (https://docs.github.com/en/rest/projects/views) enables collection of board-level flow metrics.

**API endpoints used:**
- `GET /users/{owner}/projectsV2/{project}/fields` — field definitions and IDs
- `POST /users/{owner}/projectsV2/{project}/views` — create views (REST only, no GraphQL mutation)
- GraphQL `ProjectV2` node → `items` connection — fetch all items with field values

**Configuration:** `.github/project-config.json` stores field IDs, view numbers, and CLI examples.

### 8. Board Item Snapshot (`project/board_snapshot.json`) — PLANNED

Periodic snapshot of all project items with their field values.

**Example Record**:
```json
{
  "item_id": "PVTI_lAHOAzARAM4BP0TB...",
  "issue_number": 42,
  "title": "Add Copilot acceptance rate chart",
  "status": "Sprint: In Progress",
  "priority": "P1-High",
  "sprint": "Sprint 1",
  "estimate": 5,
  "area": "Copilot",
  "assignees": ["watney"],
  "labels": ["user-story"],
  "captured_at": "2026-02-22T19:00:00Z"
}
```

### 9. Board Flow Metrics (`project/flow_metrics.json`) — PLANNED

Cumulative flow and cycle time per board column.

**Example Record**:
```json
{
  "date": "2026-02-22",
  "items_by_status": {
    "Backlog": 3,
    "Sprint: Planned": 2,
    "Sprint: In Progress": 4,
    "Sprint: In Review": 1,
    "Sprint: Done": 5,
    "Released": 16
  },
  "avg_days_in_column": {
    "Sprint: Planned": 1.2,
    "Sprint: In Progress": 3.5,
    "Sprint: In Review": 1.8
  },
  "sprint_velocity": 8,
  "wip_violations": 1
}
```

---

## Daily Snapshots (`snapshots/YYYY-MM-DD.json`)

Combined daily rollup of all key metrics for historical trending.

**Schema**: `schemas/snapshot_schema.json`

**Example File**: `snapshots/2025-01-22.json`
```json
{
  "date": "2025-01-22",
  "metadata": {
    "captured_at": "2025-01-22T23:59:59Z",
    "version": "1.0",
    "source": "github_api"
  },
  "space": {
    "pr_cycle_time_median_hours": 18.5,
    "review_turnaround_median_hours": 4.2,
    "rework_rate": 0.22,
    "open_prs": 42,
    "merged_prs_today": 7
  },
  "copilot": {
    "active_users": 85,
    "engaged_users": 72,
    "suggestions": 12450,
    "acceptances": 3890,
    "acceptance_rate": 0.312,
    "seat_utilization_rate": 0.85,
    "time_saved_hours": 59.6,
    "roi_value_usd": 5366.4
  }
}
```

**Purpose**:
- Enables long-term trending beyond API limits
- Single file per day for easy querying
- Pre-computed aggregations for dashboard performance

---

## Storage Layer API

### Initialize a new file:
```python
from storage import JSONStore

store = JSONStore("data")
store.initialize_file("space/pr_cycle_times.json", schema_version="1.0", source="github_api")
```

### Read data:
```python
data = store.read("space/pr_cycle_times.json")
records = data["data"]
```

### Append new records:
```python
new_prs = [
    {
        "pr_id": 1235,
        "repo": "org/repo",
        "opened_at": "2025-01-22T10:00:00Z",
        "merged_at": "2025-01-22T22:00:00Z",
        "cycle_time_hours": 12.0,
        "author": "developer"
    }
]
store.append_data("space/pr_cycle_times.json", new_prs)
```

### Query by date range:
```python
recent_prs = store.query_by_date_range(
    "space/pr_cycle_times.json",
    start_date="2025-01-15",
    end_date="2025-01-22",
    date_field="merged_at"
)
```

### Query by repository:
```python
repo_prs = store.query_by_repo("space/pr_cycle_times.json", "org/my-repo")
```

### Get file statistics:
```python
stats = store.get_stats("space/pr_cycle_times.json")
# Returns: {"count": 245, "date_range": {"start": "2024-10-22", "end": "2025-01-22"}, ...}
```

### Validate file structure:
```python
is_valid = store.validate_structure("space/pr_cycle_times.json")
```

---

## Design Principles

1. **Human-Readable**: JSON with 2-space indentation, sorted keys where appropriate
2. **Schema Validation**: All schemas defined in `schemas/` directory using JSON Schema Draft 7
3. **Immutable Appends**: New data appends to arrays, never modifies existing records
4. **Timestamped**: All events have ISO 8601 timestamps (UTC with 'Z' suffix)
5. **Self-Describing**: Metadata block tracks version, source, and last update
6. **Queryable**: Consistent field names enable date/repo filtering
7. **Portable**: Plain JSON files can be backed up, versioned, or migrated easily

---

## Data Lifecycle

1. **Collection**: Collectors fetch from GitHub API or generate dummy data
2. **Append**: New records added via `append_data()` with timestamp update
3. **Snapshot**: Daily aggregation computed and written to `snapshots/YYYY-MM-DD.json`
4. **Query**: Dashboards read and filter data for visualization
5. **Backup**: Automated backups created before major updates
6. **Archive**: Old data files can be compressed or moved to cold storage

---

## Migration and Versioning

When schemas evolve:

1. Increment `metadata.version` (e.g., "1.0" → "1.1")
2. Add migration script in `storage/migrations/`
3. Maintain backward compatibility where possible
4. Document breaking changes in CHANGELOG.md

Example migration:
```python
# migrations/migrate_v1_0_to_v1_1.py
def migrate(store: JSONStore):
    data = store.read("space/pr_cycle_times.json")
    for record in data["data"]:
        # Add new field with default value
        record["labels"] = []
    data["metadata"]["version"] = "1.1"
    store.write("space/pr_cycle_times.json", data)
```

---

## Performance Considerations

- Files kept < 10MB for fast reads (rotate to archive if needed)
- Use snapshots for historical queries (pre-aggregated)
- Index-free design (small datasets, ~90 days retention)
- Batch writes (collect records, append once)
- Filter in Python (no need for database indexes at this scale)

---

## Security Notes

- No PII stored (GitHub usernames only, publicly visible)
- Token never written to JSON files
- `.env` file excluded from git (use `.env.example` template)
- File permissions set to user-only read/write in Docker volumes
