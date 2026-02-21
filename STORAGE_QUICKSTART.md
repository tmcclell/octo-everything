# Storage Layer Quick Start

**Created by:** Johanssen (Data Engineer)  
**Date:** 2025-01-22

This guide helps you use the JSON storage layer for DevMetrics Dashboard.

---

## For Collectors (Watney)

### Initialize a New Metric File

```python
from storage import JSONStore

store = JSONStore("data")
store.initialize_file(
    "space/pr_cycle_times.json",
    schema_version="1.0",
    source="github_api"  # or "dummy_data"
)
```

### Append New Data

```python
# After fetching from GitHub API
new_prs = [
    {
        "pr_id": 1234,
        "repo": "org/repo-name",
        "opened_at": "2025-01-22T10:00:00Z",
        "merged_at": "2025-01-22T18:30:00Z",
        "cycle_time_hours": 8.5,
        "author": "developer",
        "title": "Feature implementation",
        "lines_changed": 120,
        "commits": 2
    }
]

# Append automatically updates metadata.last_updated
store.append_data("space/pr_cycle_times.json", new_prs)
```

### Important Notes for Collectors

- **Timestamps:** Always use ISO 8601 format with 'Z' suffix: `2025-01-22T10:00:00Z`
- **Dates:** Use YYYY-MM-DD format: `2025-01-22`
- **Schema validation:** Match exact field names and types from `schemas/*.json`
- **Immutability:** Never modify existing records, only append new ones

---

## For Dashboards (Beck)

### Read Data

```python
from storage import JSONStore

store = JSONStore("data")

# Read full file
data = store.read("space/pr_cycle_times.json")
records = data["data"]
metadata = data["metadata"]

print(f"Last updated: {metadata['last_updated']}")
print(f"Total PRs: {len(records)}")
```

### Query by Date Range

```python
# Get last 7 days of merged PRs
from datetime import date, timedelta

end = date.today()
start = end - timedelta(days=7)

recent_prs = store.query_by_date_range(
    "space/pr_cycle_times.json",
    start_date=start,
    end_date=end,
    date_field="merged_at"  # or "opened_at"
)

# Calculate median cycle time
cycle_times = [pr["cycle_time_hours"] for pr in recent_prs]
median = sorted(cycle_times)[len(cycle_times) // 2]
```

### Query by Repository

```python
# Get all PRs for a specific repo
backend_prs = store.query_by_repo(
    "space/pr_cycle_times.json",
    "org/backend-api"
)

print(f"Backend PRs: {len(backend_prs)}")
```

### Get File Statistics

```python
stats = store.get_stats("space/pr_cycle_times.json")
print(f"Record count: {stats['count']}")
print(f"Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
print(f"Source: {stats['source']}")
```

### Read Daily Snapshots

```python
# Get latest snapshot
latest = store.get_latest_snapshot()
space_metrics = latest["space"]
copilot_metrics = latest["copilot"]

print(f"Median PR cycle time: {space_metrics['pr_cycle_time_median_hours']}h")
print(f"Copilot acceptance rate: {copilot_metrics['acceptance_rate']:.1%}")

# List available snapshot dates
snapshots = store.list_snapshots(
    start_date="2025-01-01",
    end_date="2025-01-31"
)
print(f"Snapshots available: {len(snapshots)}")
```

---

## For Orchestration (Martinez)

### Docker Volume Mount

```yaml
# docker-compose.yml
services:
  devmetrics:
    volumes:
      - ./data:/app/data  # Persist data files
      - ./logs:/app/logs  # Persist logs
```

### Backup Strategy

```bash
# Simple file copy
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Or use Docker volume backup
docker run --rm -v devmetrics_data:/data -v $(pwd):/backup \
  alpine tar -czf /backup/data-backup.tar.gz /data
```

### Validate Data Integrity

```python
from storage import JSONStore

store = JSONStore("data")

files = [
    "space/pr_cycle_times.json",
    "space/review_turnaround.json",
    "space/rework_rates.json",
    "space/wip_counts.json",
    "copilot/usage_metrics.json",
    "copilot/acceptance_rates.json",
    "copilot/seat_utilization.json",
]

for filepath in files:
    is_valid = store.validate_structure(filepath)
    print(f"{filepath}: {'✅ VALID' if is_valid else '❌ INVALID'}")
```

---

## Available Data Files

| File | Schema | Description |
|------|--------|-------------|
| `space/pr_cycle_times.json` | `pr_cycle_times_schema.json` | PR open → merge durations |
| `space/review_turnaround.json` | `review_turnaround_schema.json` | Time to first review |
| `space/rework_rates.json` | `rework_rates_schema.json` | Weekly rework statistics |
| `space/wip_counts.json` | `wip_counts_schema.json` | Daily open PR counts |
| `copilot/usage_metrics.json` | `usage_metrics_schema.json` | Daily Copilot usage |
| `copilot/acceptance_rates.json` | `acceptance_rates_schema.json` | Daily acceptance rates |
| `copilot/seat_utilization.json` | `seat_utilization_schema.json` | Seat assignment & usage |
| `snapshots/YYYY-MM-DD.json` | `snapshot_schema.json` | Daily aggregated snapshot |

---

## Common Patterns

### Calculate Metrics from Raw Data

```python
# Median cycle time
cycle_times = [pr["cycle_time_hours"] for pr in data["data"]]
median = sorted(cycle_times)[len(cycle_times) // 2]

# Rework rate for last week
last_week = data["data"][-1]  # Assuming sorted by week_start
rework_rate = last_week["changes_requested"] / last_week["total_merged"]

# Acceptance rate
usage = store.read("copilot/usage_metrics.json")["data"][-1]
acceptance_rate = usage["total_code_acceptances"] / usage["total_code_suggestions"]
```

### Filter by Multiple Criteria

```python
from datetime import datetime

# Get PRs from specific repo in date range
recent_prs = store.query_by_date_range(
    "space/pr_cycle_times.json",
    start_date="2025-01-15",
    end_date="2025-01-22",
    date_field="merged_at"
)

backend_prs = [pr for pr in recent_prs if pr["repo"] == "org/backend-api"]
large_prs = [pr for pr in backend_prs if pr["lines_changed"] > 200]

print(f"Large backend PRs: {len(large_prs)}")
```

### Create Daily Snapshot

```python
from datetime import date

# Compute aggregations
all_prs = store.read("space/pr_cycle_times.json")["data"]
today_prs = [pr for pr in all_prs if pr["merged_at"].startswith(str(date.today()))]

cycle_times = sorted([pr["cycle_time_hours"] for pr in today_prs])
median_cycle = cycle_times[len(cycle_times) // 2] if cycle_times else 0

usage = store.read("copilot/usage_metrics.json")["data"][-1]

snapshot = {
    "date": str(date.today()),
    "metadata": {
        "captured_at": datetime.utcnow().isoformat() + "Z",
        "version": "1.0",
        "source": "github_api"
    },
    "space": {
        "pr_cycle_time_median_hours": median_cycle,
        "merged_prs_today": len(today_prs),
        # ... more metrics
    },
    "copilot": {
        "active_users": usage["total_active_users"],
        "acceptance_rate": usage["total_code_acceptances"] / usage["total_code_suggestions"],
        # ... more metrics
    }
}

store.write(f"snapshots/{date.today()}.json", snapshot)
```

---

## Troubleshooting

### File Not Found
```python
data = store.read("space/pr_cycle_times.json")
if data is None:
    # Initialize file if it doesn't exist
    store.initialize_file("space/pr_cycle_times.json")
```

### Invalid JSON
- Check file with `store.validate_structure(filepath)`
- Review schema in `schemas/*.json`
- Use backup: `store.backup(filepath)` before modifying

### Large File Performance
- Keep files under 10MB (rotate older data to archive)
- Use snapshots for historical queries (pre-aggregated)
- Filter early: `query_by_date_range()` before processing

---

## Reference Documentation

- **Full documentation:** `DATA_SCHEMAS.md`
- **Schema definitions:** `schemas/*.json`
- **Example data:** `data/space/*.json`, `data/copilot/*.json`
- **Storage API source:** `storage/json_store.py`
- **Architecture decision:** `.squad/decisions/inbox/johanssen-storage-architecture.md`
