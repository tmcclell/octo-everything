# JSON Schema Definitions

This directory contains JSON Schema (Draft 7) definitions for all data files in the DevMetrics Dashboard.

## Schemas

| Schema File | Data File | Description |
|------------|-----------|-------------|
| `pr_cycle_times_schema.json` | `data/space/pr_cycle_times.json` | PR open-to-merge durations |
| `review_turnaround_schema.json` | `data/space/review_turnaround.json` | Time to first review |
| `rework_rates_schema.json` | `data/space/rework_rates.json` | Weekly rework statistics |
| `wip_counts_schema.json` | `data/space/wip_counts.json` | Daily WIP snapshots |
| `usage_metrics_schema.json` | `data/copilot/usage_metrics.json` | Daily Copilot usage |
| `acceptance_rates_schema.json` | `data/copilot/acceptance_rates.json` | Daily acceptance rates |
| `seat_utilization_schema.json` | `data/copilot/seat_utilization.json` | Seat assignment and usage |
| `snapshot_schema.json` | `data/snapshots/YYYY-MM-DD.json` | Combined daily snapshots |

## Validation

These schemas can be used with any JSON Schema validator. Example with Python's `jsonschema` library:

```python
import json
from jsonschema import validate

# Load schema
with open("schemas/pr_cycle_times_schema.json") as f:
    schema = json.load(f)

# Load data
with open("data/space/pr_cycle_times.json") as f:
    data = json.load(f)

# Validate
validate(instance=data, schema=schema)
```

## Schema Structure

All schemas follow a common pattern:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "...",
  "description": "...",
  "type": "object",
  "required": ["metadata", "data"],
  "properties": {
    "metadata": { ... },
    "data": { ... }
  }
}
```

### Metadata Block

Every data file must include:
- `last_updated`: ISO 8601 timestamp (UTC)
- `version`: Schema version (semantic versioning pattern)
- `source`: Data source type ("github_api" or "dummy_data")

### Data Array

The `data` array contains metric records with strongly-typed fields.

## Adding New Schemas

When adding a new metric:

1. Create schema file in this directory: `{metric_name}_schema.json`
2. Define metadata and data structure
3. Add validation in `storage/json_store.py` if needed
4. Document in `DATA_SCHEMAS.md`
5. Create example data file in appropriate `data/` subdirectory
6. Update this README table

## References

- [JSON Schema specification](https://json-schema.org/draft-07/json-schema-release-notes.html)
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)
