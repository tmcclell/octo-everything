# DevMetrics Dashboard — v1 Plan

## Problem Statement

Build a lightweight developer metrics dashboard focused on two pillars from the executive metrics strategy:

1. **SPACE Mindset** — Cycle time trends, rework rates, context switching, collaboration signals
2. **AI ROI (Copilot)** — Adoption rate, active usage, acceptance rate, seat utilization, time saved → $

The tool should be simple, browser-based, Python-powered, and use GitHub's API/SDK as the primary data source.

---

## What GitHub Already Provides (No Code Needed)

### Copilot — Native Dashboards (Org + Enterprise level, public preview)

| Built-in Feature | What It Shows |
|-----------------|---------------|
| **Copilot Usage Metrics Dashboard** | 28-day adoption trends, DAU/WAU, acceptance rates, engagement by feature |
| **Code Generation Dashboard** | Code generation breakdown by users and agents |
| **PR Lifecycle Metrics** | PR creation/merge counts, median time to merge (Copilot vs all) |
| **NDJSON Export** | Raw telemetry data for Power BI, Looker, etc. |
| **Seat Management UI** | Seats assigned, last activity, CSV download |

> **Bottom line:** GitHub natively covers ~70% of AI ROI metrics (adoption, engagement, acceptance, PR lifecycle).

### Repository-Level Insights (per-repo only, not org-aggregate)

Pulse, Contributors, Traffic, Code frequency, Network — all per-repo, no cross-repo aggregation.

### What GitHub Does NOT Provide Natively

| Missing Metric | Why It Matters |
|---------------|---------------|
| **PR Cycle Time** (open → merge, across repos) | Core SPACE flow metric |
| **Time to First Review** | Bottleneck indicator |
| **Rework Rate** (changes requested %) | Quality signal |
| **WIP across repos** | Flow efficiency |
| **Time Saved → $ (ROI calculator)** | CFO needs dollar values, not usage charts |
| **Historical data beyond 28 days** | Trending requires local snapshots |
| **Context Switching / Developer Satisfaction** | SPACE dimensions not tracked |

---

## Where Our Custom Tool Adds Value

1. **SPACE metrics** — PR cycle time, review turnaround, rework rate, WIP aggregated across repos (**primary value-add**)
2. **$ ROI calculator** — Convert Copilot acceptance data into dollar-value time saved
3. **Historical trending** — Snapshot and store beyond the 28-day native window
4. **Unified view** — SPACE + AI ROI in one dashboard

---

## Proposed Approach

A minimal Python web app that pulls metrics from the GitHub API, stores snapshots in local JSON/CSV files, renders dashboards in the browser, and uses Playwright for automated event logging and error capture.

---

## GitHub API Coverage Analysis

### SPACE Metrics — All core metrics available via API

| Metric | API Endpoint | Status | Details |
|--------|-------------|--------|---------|
| **PR Cycle Time** | `GET /repos/{o}/{r}/pulls?state=closed` | ✅ YES | PR has `created_at` + `merged_at` → compute delta |
| **Time to First Review** | `GET /repos/{o}/{r}/pulls/{n}/reviews` | ✅ YES | Reviews have `submitted_at` → compare with PR `created_at` |
| **Rework Rate** | `GET /repos/{o}/{r}/pulls/{n}/reviews` | ✅ YES | Count reviews with `state: "CHANGES_REQUESTED"` vs total merged |
| **WIP (Open PRs)** | `GET /repos/{o}/{r}/pulls?state=open` | ✅ YES | Count of open PRs per repo |
| **Context Switching** | `GET /users/{user}/events` | ⚠️ APPROX | Count distinct repos/PRs per user per day |
| **Developer Satisfaction** | None | ❌ NO | Survey-based only — needs external tool (Google Form, etc.) |

### AI ROI (Copilot) — Fully available via API

| Metric | API Endpoint | Status | Details |
|--------|-------------|--------|---------|
| **Suggestions & Acceptances** | Enterprise reports | ✅ YES | `total_code_suggestions`, `total_code_acceptances`, per language/editor |
| **Active & Engaged Users** | Enterprise reports | ✅ YES | `total_active_users`, `total_engaged_users` per day |
| **Acceptance Rate** | Computed from above | ✅ YES | `acceptances / suggestions` |
| **Lines Suggested/Accepted** | Enterprise reports | ✅ YES | `total_code_lines_suggested`, `total_code_lines_accepted` |
| **Seat Utilization** | `GET /orgs/{org}/copilot/billing/seats` | ✅ YES | `total_seats` + per-seat `last_activity_at` |
| **Chat Usage (IDE + dotcom)** | Enterprise reports | ✅ YES | `total_chats`, insertion/copy events |
| **PR Summaries Created** | Enterprise reports | ✅ YES | `copilot_dotcom_pull_requests.total_pr_summaries_created` |
| **Per-User Daily Metrics** | `GET /enterprises/{ent}/copilot/metrics/reports/users-1-day?day=YYYY-MM-DD` | ✅ YES | User-level breakdown, 1 year history |
| **Time Saved → $** | Computed | ✅ YES | Configurable multiplier × acceptance count |

> **Note:** Enterprise API access to `msft-demo-account-wEMU` is unavailable — dummy/sample data will be used instead (see "Dummy Data Generation" section below).

### Permissions Required

| Token Scope | Unlocks |
|-------------|---------|
| `repo` (classic PAT) or fine-grained "Pull requests: read" | All SPACE metrics (PRs, reviews) |
| `manage_billing:copilot` **or** `read:enterprise` | Enterprise Copilot metrics + seat data |
| Fine-grained "Enterprise Copilot metrics: read" | Enterprise usage metrics reports (new API) |
| `read:org` | User events for context switching |

> **Policy prerequisite:** Enterprise must have "Copilot usage metrics" policy set to **Enabled everywhere**.

### Known Gaps

| Gap | Workaround |
|-----|------------|
| **Developer satisfaction** not in any API | Link a survey from the dashboard; import CSV results |
| **~~Copilot metrics 28-day limit~~** | **RESOLVED:** Enterprise API provides 1 year history |
| **~~Per-user metrics unavailable~~** | **RESOLVED:** Enterprise user-level daily reports available |

---

## Technology Recommendations

### Frontend (Browser UI)

| Option | Why | Trade-off |
|--------|-----|-----------|
| **Streamlit** (Recommended) | Pure Python, zero JS needed, built-in charts (Plotly), runs in browser, rapid prototyping | Less customizable layout |
| Flask + Chart.js | More control over UI, lightweight | More code to write, need HTML/JS |
| Gradio | Python-native, good for dashboards | More ML-focused, less flexible for custom metrics |

**Recommendation → Streamlit.** Fastest path to a working dashboard with no frontend code. Supports interactive filters, tables, and Plotly/Altair charts out of the box.

### Backend / Data Layer

| Component | Choice | Why |
|-----------|--------|-----|
| **Language** | Python 3.11+ | User preference, rich ecosystem |
| **GitHub SDK** | [`PyGithub`](https://github.com/PyGithub/PyGithub) | Mature, well-documented Python SDK for GitHub REST API v3 |
| **Enterprise Copilot API** | `requests` | Enterprise usage metrics endpoints (NDJSON reports) |
| **Data storage** | **JSON files** (Docker volume) | Text-based, human-readable, persisted via volume mount |
| **Container** | **Docker + docker-compose** | Single `docker compose up`, reproducible, portable |
| **Scheduling** | `schedule` library or container cron | Periodic data collection for SPACE metrics |

### Logging & Monitoring

| Component | Choice | Why |
|-----------|--------|-----|
| **Playwright** (Python) | `playwright` pip package | Automated browser-based event logging, error capture, screenshots |
| **Python logging** | `logging` stdlib | Structured log output to file for app events |
| **Error tracking** | Playwright + logging → JSON log file | Key events (API failures, rate limits, data anomalies) captured with timestamps |

### Playwright Usage Strategy

Playwright serves two purposes in this project:

1. **Dashboard health monitoring** — Automated scripts that load the dashboard, verify charts render, capture screenshots on failure, and log errors to `logs/events.json`
2. **Data collection fallback** — For GitHub UI-only metrics not available via API, Playwright can scrape and log values (e.g., certain Copilot dashboard widgets)

---

## Data Architecture

```
data/
├── space/
│   ├── pr_cycle_times.json       # PR open → merge durations
│   ├── review_turnaround.json    # Time to first review
│   ├── rework_rates.json         # Changes requested / PRs merged
│   └── wip_counts.json           # Open PRs over time
├── copilot/
│   ├── usage_metrics.json        # Daily Copilot usage snapshots
│   ├── acceptance_rates.json     # Suggestion acceptance %
│   └── seat_utilization.json     # Active vs total seats
├── snapshots/
│   └── YYYY-MM-DD.json           # Daily full snapshot for trending
└── logs/
    ├── app.log                   # Python logging output
    └── events.json               # Playwright-captured events & errors
```

---

## Feature Scope — v1

### Phase 1: SPACE Metrics

| # | Feature | Description |
|---|---------|-------------|
| 1 | **GitHub Auth** | PAT or GitHub App token configuration via `.env` file |
| 2 | **PR Cycle Time Collector** | Fetch closed/merged PRs, compute open→merge duration, store in JSON |
| 3 | **Review Turnaround** | Time from PR open to first review comment |
| 4 | **Rework Rate** | Ratio of PRs with "changes requested" reviews vs total merged |
| 5 | **WIP Tracker** | Count of open PRs per repo over time |
| 6 | **SPACE Dashboard Page** | Streamlit page with trend charts for all SPACE metrics |

### Phase 2: AI ROI (Copilot)

| # | Feature | Description |
|---|---------|-------------|
| 7 | **Copilot Metrics Collector** | Pull from `/orgs/{org}/copilot/metrics` endpoint |
| 8 | **Seat Utilization** | Active users vs total assigned seats |
| 9 | **Acceptance Rate Trends** | Copilot suggestion acceptance % over time |
| 10 | **Time Saved Estimator** | Configurable multiplier (e.g., 55s per accepted suggestion) → $ saved |
| 11 | **AI ROI Dashboard Page** | Streamlit page with Copilot adoption & ROI charts |

### Phase 3: Logging & Monitoring

| # | Feature | Description |
|---|---------|-------------|
| 12 | **Playwright Health Checks** | Automated script that loads dashboard, verifies render, captures errors |
| 13 | **Event Logger** | All API errors, rate limits, data anomalies logged to `logs/events.json` |
| 14 | **Screenshot on Failure** | Playwright captures screenshot when dashboard check fails |

---

## Project Structure

```
devmetrics/
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Single-command startup
├── app.py                    # Streamlit entry point
├── pages/
│   ├── space_dashboard.py    # SPACE metrics page
│   └── copilot_dashboard.py  # AI ROI page
├── collectors/
│   ├── github_client.py      # PyGithub + enterprise API wrapper
│   ├── space_collector.py    # PR cycle time, review, rework, WIP
│   ├── copilot_collector.py  # Enterprise Copilot metrics API calls
│   └── dummy_data_generator.py # Generate realistic sample data for all metrics
├── storage/
│   └── json_store.py         # Read/write JSON data files
├── monitoring/
│   ├── health_check.py       # Playwright dashboard verification
│   └── event_logger.py       # Structured event logging
├── data/                     # JSON data files (Docker volume)
├── logs/                     # Log files (Docker volume)
├── .env.example              # Template for config
├── .env                      # GitHub token config (gitignored)
├── requirements.txt          # Python dependencies
└── README.md                 # Setup & usage docs
```

---

## Key Dependencies

```
streamlit>=1.30
PyGithub>=2.1
requests>=2.31
plotly>=5.18
playwright>=1.40
python-dotenv>=1.0
schedule>=1.2
```

---

## Notes & Considerations

- **Enterprise data unavailable**: Access to `msft-demo-account-wEMU` enterprise API is not available. All metrics will use generated dummy data for v1.
- **Dummy data is realistic**: Generated data should mimic real-world patterns (weekday spikes, gradual adoption curves, realistic distributions).
- **Container deployment**: `docker compose up` to run. Data persists in Docker volumes across restarts.
- **Rate limits**: GitHub API has 5,000 req/hr for authenticated users. Collectors should paginate efficiently.
- **Data freshness**: Copilot usage metrics have ~3 day lag (processed by end of 3rd UTC day).
- **Security**: Never commit `.env` or tokens. `.env.example` provided as template.
- **Playwright install**: Handled automatically in Dockerfile (`playwright install chromium`).
- **SPACE metrics still need local storage**: PR data has no historical API — must collect and store in JSON.

---

## Dummy Data Generation

Since enterprise API access is unavailable, the project will include a data generator that produces realistic sample data for all metrics. This ensures the dashboard is fully functional and demonstrable without live API access.

### Generator: `collectors/dummy_data_generator.py`

| Data Category | What It Generates | Approach |
|---------------|-------------------|----------|
| **PR Cycle Time** | 90 days of merged PRs across 5 repos | Random durations (hours–days), weekday-weighted, normal distribution around 18hr median |
| **Review Turnaround** | First review times for each PR | Log-normal distribution, median ~4hrs, some outliers at 24hr+ |
| **Rework Rate** | Changes-requested ratio per week | 15–30% baseline with slight downward trend |
| **WIP Counts** | Daily open PR counts per repo | Random walk between 3–15 per repo |
| **Copilot Usage** | Daily active users, suggestions, acceptances | Gradual adoption curve (20→80% over 90 days), weekday patterns |
| **Acceptance Rate** | Daily acceptance % | 25–35% range with slight upward trend |
| **Seat Utilization** | Assigned vs active seats over time | 100 seats, active growing from 40→85 |
| **Time Saved** | Estimated hours/$ saved per day | Derived from acceptance counts × configurable multiplier (55s/acceptance) |

### Usage

```bash
# Generate fresh dummy data (writes to data/ directory)
python -m collectors.dummy_data_generator

# Or via make/script
make generate-data
```

### Design Principles

- **Deterministic with seed** — Same seed produces identical data for reproducible demos
- **Configurable** — Number of repos, team size, date range, and trends adjustable via CLI args or `.env`
- **Same schema as real collectors** — Dummy data uses identical JSON structure so the dashboard works unchanged
- **Swap-ready** — When live API access becomes available, switch from dummy generator to real collectors with no dashboard changes

---

## Not in Scope (v1)

- DORA metrics (deployment frequency, MTTR) — needs CI/CD integration
- Quality/security metrics (escaped defects, vulnerability trends) — needs GHAS data
- User authentication on the dashboard
- Production deployment to cloud (this runs locally in a container for v1)
