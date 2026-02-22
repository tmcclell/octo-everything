# Data Schemas Specification

## Overview

This specification defines the JSON data schemas used by the DevMetrics Dashboard for all metrics collection, storage, and visualization.

> **Canonical reference:** See [`DATA_SCHEMAS.md`](../../../DATA_SCHEMAS.md) in the repository root for the full schema definitions.

---

## Schema Summary

### SPACE Metrics

| Schema | File | Description |
|--------|------|-------------|
| PR Cycle Time | `data/pr_cycle_time.json` | Open-to-merge durations per PR |
| Time to First Review | `data/review_turnaround.json` | First review timestamp per PR |
| Rework Rate | `data/rework_rate.json` | Changes-requested ratio per repo |
| WIP Tracker | `data/wip_count.json` | Open PR counts per repo over time |

### AI ROI (Copilot)

| Schema | File | Description |
|--------|------|-------------|
| Copilot Usage | `data/copilot_usage.json` | Daily active users, suggestions, acceptances |
| Seat Utilization | `data/copilot_seats.json` | Active vs assigned seat counts |

---

## Schema Conventions

- All timestamps use ISO 8601 format (`YYYY-MM-DDTHH:mm:ssZ`)
- Numeric metrics are stored as floats (not strings)
- Each JSON file is an array of records, newest first
- Schema validation is defined in `schemas/` directory using JSON Schema draft-07

---

## Storage

Data files are stored in `devmetrics/data/` (Docker volume mount) and `data/` (repo-level dummy data). See [`STORAGE_QUICKSTART.md`](../../../STORAGE_QUICKSTART.md) for details.
