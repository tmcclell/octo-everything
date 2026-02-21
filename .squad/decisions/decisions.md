# Decisions Archive

**Project:** DevMetrics Dashboard — SPACE metrics + AI ROI for Copilot  
**Last Updated:** 2026-02-21  

---

## Decision 1: Storage Architecture Decision

**Date:** 2025-01-22  
**Author:** Johanssen (Data Engineer)  
**Status:** Implemented  

### Context
The DevMetrics Dashboard needs a data storage solution for SPACE metrics (PR cycle times, reviews, rework, WIP) and Copilot metrics (usage, acceptance, seats). Requirements:
1. Persistent storage across Docker restarts
2. Human-readable format for debugging and manual inspection
3. Schema validation to ensure data quality
4. Time-series query capabilities (date ranges, repository filters)
5. Simple enough to run locally without database setup
6. Append-only pattern for immutability

### Decision
**Adopted JSON file storage with schema validation and a storage abstraction layer.**

#### Architecture
```
data/
├── space/          # SPACE metrics (4 files)
├── copilot/        # Copilot metrics (3 files)
├── snapshots/      # Daily aggregations (1 file per day)
└── logs/           # Application logs

storage/
└── json_store.py   # Storage abstraction

schemas/
└── *.json          # JSON Schema definitions (8 schemas)
```

#### File Format
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

#### Storage API
```python
from storage import JSONStore

store = JSONStore("data")

# Initialize new file
store.initialize_file("space/pr_cycle_times.json", schema_version="1.0")

# Read data
data = store.read("space/pr_cycle_times.json")

# Append records (updates last_updated timestamp automatically)
store.append_data("space/pr_cycle_times.json", new_records)

# Query by date range
records = store.query_by_date_range(
    "space/pr_cycle_times.json",
    start_date="2025-01-15",
    end_date="2025-01-22"
)

# Query by repository
repo_records = store.query_by_repo("space/pr_cycle_times.json", "org/repo")

# Get statistics
stats = store.get_stats("space/pr_cycle_times.json")

# Validate structure
is_valid = store.validate_structure("space/pr_cycle_times.json")
```

### Rationale

**Why JSON over SQLite/PostgreSQL?**
- Simpler setup (no migrations, no ORM)
- Human-readable for debugging
- Git-friendly (can diff changes)
- Docker volume-friendly (plain files)
- Sufficient for 90-day retention at ~100 repos
- Easy backup and export

**Why schema validation?**
- Catch data quality issues early
- Self-documenting data contracts
- Enable safe schema evolution (versioning)
- Standard JSON Schema tooling

**Why append-only pattern?**
- Immutability ensures historical accuracy
- Simpler concurrency (no update conflicts)
- Audit trail preserved
- Aligns with event-sourcing principles

**Why daily snapshots?**
- Pre-aggregated data for fast dashboard loading
- Enables trending beyond GitHub API 28-day limits
- Single file per day simplifies date queries

### Trade-offs
| Aspect | JSON Files | Alternative (DB) |
|--------|-----------|------------------|
| Setup complexity | ✅ Zero config | ❌ Migrations, schema mgmt |
| Query performance | ⚠️ Read full file | ✅ Indexed queries |
| Scalability | ⚠️ ~10MB file limit | ✅ Unlimited |
| Debugging | ✅ Text editor | ❌ SQL client needed |
| Portability | ✅ Copy files | ⚠️ Export required |
| Backups | ✅ File copy | ⚠️ Dump + restore |

**Verdict:** For 90-day retention at ~100 repos, JSON files are simpler and sufficient. Migrate to DB if org scales to 1000+ repos or needs real-time queries.

### Impact on Team

**Watney (Collector Engineer)**
- Use: `JSONStore.append_data()` to persist fetched metrics
- Schema: Match exact structure in `schemas/*.json`
- Timestamp: All dates/times must be ISO 8601 with 'Z' suffix (UTC)

**Beck (Dashboard Engineer)**
- Use: `JSONStore.read()` and `query_by_date_range()` for data access
- Filter: Use `query_by_repo()` for per-repo breakdowns
- Snapshots: Use `data/snapshots/YYYY-MM-DD.json` for historical trends

**Martinez (Orchestrator)**
- Docker: Mount `data/` as volume for persistence
- Logs: Application logs go to `data/logs/app.log`
- Backup: Simple file copy or volume snapshot

### Migration Path
If JSON storage becomes insufficient:
1. Phase 1 (current): JSON files, 90-day retention
2. Phase 2 (future): Add SQLite for queries, keep JSON as source-of-truth
3. Phase 3 (scale): Migrate to PostgreSQL or TimescaleDB for time-series

Schema versioning (`metadata.version`) enables backward-compatible migrations.

### References
- JSON Schema spec: https://json-schema.org/draft-07/
- Storage implementation: `storage/json_store.py`
- Schema documentation: `DATA_SCHEMAS.md`
- Example data: `data/space/*.json`, `data/copilot/*.json`

### Review Notes
- Validated file format with example data for all 8 schemas
- Tested append, query, and statistics operations
- Documented API in `DATA_SCHEMAS.md` (400+ lines)
- Ready for collector and dashboard integration

---

## Decision 2: GitHub Issues Organization Strategy

**Date:** 2025-01-22  
**Decided by:** Lewis (Lead)  

### Context
Created 18 GitHub issues for the DevMetrics Dashboard project on `tmcclell/octo-ev1-metrics` repository. Needed to organize features from the plan into trackable work items.

### Decision
Organized issues into 4 labeled categories matching the plan phases:
- `phase-1`: SPACE Metrics (6 issues)
- `phase-2`: AI ROI/Copilot (5 issues)
- `phase-3`: Logging & Monitoring (3 issues)
- `cross-cutting`: Infrastructure/setup (4 issues)

Each issue includes:
- Phase designation in body
- Detailed acceptance criteria (checkboxes)
- Technical notes (API endpoints, data schemas, dependencies)
- File locations where applicable

### Rationale
1. **Phase-based labels** align with the plan structure and enable filtering by workstream
2. **Detailed acceptance criteria** make issues actionable without referring back to the plan
3. **Issue templates in .github/issue-templates/** preserve the structured content for reference and potential reuse
4. **Label color-coding** provides visual grouping (phase-1=green, phase-2=blue, phase-3=yellow, cross-cutting=red)

### Impact
- Team can now track work granularly via GitHub issues
- Specialists can be assigned to specific phase issues
- Progress is visible at repo level
- Cross-cutting issues (Docker, dependencies, dummy data) can be prioritized independently

### Notes
- Issue numbers were created non-sequentially due to parallel execution, but all 18 issues are present
- Labels were created before issues to ensure proper tagging
- Issue bodies are stored in .github/issue-templates/ for version control and future reference

---

## Decision 3: Phase 1 Backend Structure

**Date:** 2026-02-21  
**Decided by:** Watney (Backend Dev)  

### Context
Building Phase 1 infrastructure for DevMetrics dashboard

### Decision
Created `devmetrics/collectors/` module with four components:

1. **`github_client.py`** — PyGithub wrapper with rate limit handling
2. **`dummy_data_generator.py`** — Deterministic data generator (seed=42) for 90 days of metrics
3. **`space_collector.py`** — SPACE metrics collector (PR cycle time, reviews, rework, WIP)
4. **`copilot_collector.py`** — Copilot metrics collector (usage, acceptance, seats) - stub for future API access

### Rationale

- **Separation of concerns:** GitHub client handles auth/rate limits, collectors focus on metric logic
- **Dummy data first:** No enterprise API access yet, but dashboard can be built/tested immediately
- **Schema compatibility:** Dummy data output matches real collector schema (swap-ready)
- **Deterministic generation:** Same seed produces identical data for reproducible demos
- **Error resilience:** Rate limit handling, try/catch on per-repo basis (partial failures don't break entire collection)

### Data Storage
All metrics written to `devmetrics/data/`:
- `space/` — PR cycle times, review turnaround, rework rates, WIP counts
- `copilot/` — Usage metrics, acceptance rates, seat utilization
- `snapshots/` — Daily full snapshots for historical trending (future)

JSON format chosen for human-readable, version-controllable data files.

### Impact

- **Team:** Beck (Frontend) can now build Streamlit dashboard using dummy data
- **Team:** Johanssen (Data) has schema to design data models
- **Future:** When enterprise API access granted, swap `dummy_data_generator` for real collectors with no dashboard changes

### Configuration
`.env.example` created with required variables:
- `GITHUB_TOKEN` — Personal access token (repo scope for SPACE metrics)
- `GITHUB_ORG` — Organization name (for Copilot seat data)
- `GITHUB_ENTERPRISE` — Enterprise slug (for Copilot usage metrics)

**Status:** ✅ Implemented  
**Files modified:** Created `devmetrics/collectors/*.py`, `.env.example`

