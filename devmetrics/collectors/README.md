# DevMetrics Collectors

Backend data collection infrastructure for SPACE metrics and Copilot usage analytics.

## Quick Start

### Generate Dummy Data

```bash
# From project root
python -m devmetrics.collectors.dummy_data_generator
```

This creates 90 days of realistic sample data in `devmetrics/data/`:
- **SPACE metrics**: PR cycle times, review turnaround, rework rates, WIP counts
- **Copilot metrics**: Usage, acceptance rates, seat utilization

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required for live API collection:
```
GITHUB_TOKEN=ghp_your_token_here
GITHUB_ORG=your-org-name
GITHUB_ENTERPRISE=your-enterprise-slug
```

## Module Structure

```
collectors/
├── __init__.py
├── github_client.py          # PyGithub wrapper with auth & rate limiting
├── space_collector.py        # SPACE metrics from GitHub REST API
├── copilot_collector.py      # Copilot metrics from Enterprise API
└── dummy_data_generator.py   # Realistic sample data generator
```

## Usage

### Dummy Data Generation (No API Required)

```python
from devmetrics.collectors.dummy_data_generator import DummyDataGenerator

# Generate data
generator = DummyDataGenerator(seed=42, data_dir="devmetrics/data")
generator.generate_all()
```

### Live SPACE Metrics Collection

```python
from devmetrics.collectors.github_client import GitHubClient
from devmetrics.collectors.space_collector import SpaceCollector

# Initialize
client = GitHubClient(token="ghp_...")
collector = SpaceCollector(
    client=client,
    repos=["owner/repo1", "owner/repo2"]
)

# Collect metrics
pr_data = collector.collect_pr_cycle_times()
review_data = collector.collect_review_turnaround()
rework_data = collector.collect_rework_rates()
wip_data = collector.collect_wip_counts()
```

### Live Copilot Metrics Collection

```python
from devmetrics.collectors.copilot_collector import CopilotCollector

# Initialize (requires enterprise/org access)
collector = CopilotCollector(
    token="ghp_...",
    enterprise="my-enterprise",
    org="my-org"
)

# Collect metrics
usage_data = collector.collect_usage_metrics()
acceptance_data = collector.collect_acceptance_rates()
seat_data = collector.collect_seat_utilization()
```

## Data Schema

All collectors return data in a consistent format:

```json
{
  "data": [...],           // Metric-specific data points
  "summary": {...},        // Aggregated statistics
  "collected_at": "ISO timestamp",
  "source": "github_api | dummy"
}
```

### SPACE Metrics

**PR Cycle Times** (`space/pr_cycle_times.json`):
```json
{
  "prs": [
    {
      "repo": "backend-api",
      "pr_number": 1234,
      "created_at": "2025-11-23T10:00:00",
      "merged_at": "2025-11-24T14:30:00",
      "cycle_time_hours": 28.5,
      "author": "dev1"
    }
  ],
  "summary": {
    "median_hours": 18.88,
    "p95_hours": 72.5,
    "total_prs": 389
  }
}
```

**Review Turnaround** (`space/review_turnaround.json`):
```json
{
  "reviews": [
    {
      "repo": "frontend-web",
      "pr_number": 1235,
      "created_at": "2025-11-23T10:00:00",
      "first_review_at": "2025-11-23T14:00:00",
      "turnaround_hours": 4.0
    }
  ],
  "summary": {
    "median_hours": 3.85,
    "p95_hours": 24.2,
    "total_reviews": 370
  }
}
```

### Copilot Metrics

**Usage Metrics** (`copilot/usage_metrics.json`):
```json
{
  "daily_usage": [
    {
      "date": "2025-11-23",
      "active_users": 18,
      "engaged_users": 14,
      "suggestions": 1250,
      "acceptances": 375,
      "lines_suggested": 6250,
      "lines_accepted": 1875
    }
  ],
  "summary": {
    "total_suggestions": 78500,
    "total_acceptances": 23852,
    "avg_active_users": 18.5
  }
}
```

## Features

### Rate Limit Handling

The GitHub client automatically:
- Checks rate limits before each API call
- Sleeps until reset if limit is low (< 100 remaining)
- Logs rate limit status on initialization

### Error Resilience

- Per-repository try/catch blocks (one failing repo doesn't break entire collection)
- Structured logging for all errors
- Graceful degradation (returns partial results)

### Deterministic Dummy Data

- Same seed produces identical output (reproducible demos)
- Realistic patterns:
  - Weekday activity spikes
  - Log-normal distributions for cycle times
  - Gradual adoption curves for Copilot metrics
  - 15-30% rework rates with slight improvement trend
  - 25-35% acceptance rates with upward trend

## Dependencies

```
PyGithub>=2.1        # GitHub REST API client
requests>=2.31       # HTTP for Enterprise API
python-dotenv>=1.0   # Environment variable management
numpy>=1.24          # Statistical calculations
```

## Logging

All collectors use Python's built-in logging module:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Logs include:
- Authentication status & rate limits
- Collection progress (per-repo)
- Errors with context
- Summary statistics

## Future Enhancements

- [ ] Incremental data collection (append new data to existing files)
- [ ] Historical snapshot storage for trending
- [ ] Webhook-based real-time updates
- [ ] Multi-org aggregation
- [ ] DORA metrics (deployment frequency, MTTR)
- [ ] Quality metrics (escaped defects, vulnerability trends)
