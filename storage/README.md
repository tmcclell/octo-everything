# Storage Module

Generic JSON file storage layer for DevMetrics Dashboard with schema validation and time-series query capabilities.

## Quick Start

```python
from storage import JSONStore

store = JSONStore("data")

# Initialize new file
store.initialize_file("space/pr_cycle_times.json", schema_version="1.0")

# Append data
store.append_data("space/pr_cycle_times.json", new_records)

# Query by date range
records = store.query_by_date_range(
    "space/pr_cycle_times.json",
    start_date="2025-01-15",
    end_date="2025-01-22"
)
```

## API Reference

### `JSONStore(base_path="data")`

Main storage class for reading, writing, and querying JSON data files.

#### Methods

**`read(filepath: str) -> Optional[Dict]`**  
Read JSON data from file. Returns None if file doesn't exist.

**`write(filepath: str, data: Dict, indent: int = 2)`**  
Write JSON data to file with pretty-printing.

**`append_data(filepath: str, new_records: List[Dict])`**  
Append records to existing data array. Auto-updates `metadata.last_updated`.

**`initialize_file(filepath: str, schema_version: str = "1.0", source: str = "dummy_data") -> Dict`**  
Create new file with standard metadata + data structure.

**`query_by_date_range(filepath: str, start_date: Union[str, date], end_date: Union[str, date], date_field: str = "date") -> List[Dict]`**  
Filter records within date range.

**`query_by_repo(filepath: str, repo: str) -> List[Dict]`**  
Filter records by repository name.

**`get_latest_snapshot() -> Optional[Dict]`**  
Get most recent daily snapshot from `snapshots/` directory.

**`list_snapshots(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[str]`**  
List available snapshot dates with optional filtering.

**`get_stats(filepath: str) -> Dict`**  
Get basic statistics (record count, date range, source).

**`validate_structure(filepath: str) -> bool`**  
Validate file has required metadata and data fields.

**`backup(filepath: str)`**  
Create timestamped backup of file.

## Convenience Functions

```python
from storage import get_space_store, get_copilot_store, get_snapshot_store

space_store = get_space_store()       # JSONStore("data") for SPACE metrics
copilot_store = get_copilot_store()   # JSONStore("data") for Copilot metrics
snapshot_store = get_snapshot_store() # JSONStore("data") for snapshots
```

## File Structure

All files follow this pattern:

```json
{
  "metadata": {
    "last_updated": "2025-01-22T14:30:00Z",
    "version": "1.0",
    "source": "github_api"
  },
  "data": [
    // Array of records
  ]
}
```

## Design Principles

- **Human-readable:** JSON with 2-space indentation
- **Immutable:** Append-only, no modifications to existing records
- **Queryable:** Consistent field names enable filtering
- **Self-describing:** Metadata tracks version and source
- **Portable:** Plain JSON files, no database required

## Dependencies

- Python 3.11+
- Standard library only (json, pathlib, datetime, logging)

## Documentation

- **Full documentation:** `DATA_SCHEMAS.md` (comprehensive guide to all schemas)
- **Quick start guide:** `STORAGE_QUICKSTART.md` (practical examples)
- **Schema definitions:** `schemas/*.json` (JSON Schema Draft 7 specs)
- **Architecture decision:** `.squad/decisions/inbox/johanssen-storage-architecture.md`

## Testing

```python
# Validate all data files
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
    assert store.validate_structure(filepath), f"Invalid: {filepath}"
    stats = store.get_stats(filepath)
    print(f"✅ {filepath}: {stats['count']} records")
```

## Performance

- Optimized for files < 10MB (~90 days of data at 100 repos)
- In-memory filtering (no database overhead)
- Daily snapshots for historical queries
- Backup operations are fast file copies

## Error Handling

- Returns `None` for missing files (use `initialize_file()` to create)
- Raises exceptions for write errors and invalid JSON
- Logs warnings and errors using Python's logging module
- Validates structure before operations

## Thread Safety

⚠️ **Not thread-safe.** Use file locking or async queues if multiple processes write to same file.

For Docker deployments with single writer process, this is not a concern.
