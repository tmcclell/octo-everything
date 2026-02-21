## Project Started

**2025-01-22**: DevMetrics Dashboard project initialized. Responsible for GitHub API integration, data collectors for SPACE metrics (PR cycle time, reviews, rework, WIP) and Copilot metrics. Using PyGithub for GitHub REST API, requests for Enterprise API. Plan at `.github/plans/plan-devmetrics-v1.md`.

## Learnings

### 2026-02-21: Phase 1 Backend Infrastructure Built

**Architecture Decisions:**
- Created `devmetrics/collectors/` module structure for all data collection logic
- `github_client.py`: PyGithub wrapper with rate limit handling, authentication, error logging
- `space_collector.py`: Collects PR cycle time, review turnaround, rework rates, WIP counts from GitHub REST API
- `copilot_collector.py`: Stub for Enterprise API (usage, acceptance, seats) - ready for live data when access available
- `dummy_data_generator.py`: Deterministic data generator (seed=42) for 90 days of realistic SPACE + Copilot metrics

**Data Schema:**
- All collectors output JSON with consistent schema: `{data: [...], summary: {...}, collected_at, source}`
- SPACE metrics: `data/space/` (pr_cycle_times, review_turnaround, rework_rates, wip_counts)
- Copilot metrics: `data/copilot/` (usage_metrics, acceptance_rates, seat_utilization)
- Generated data includes realistic patterns: weekday spikes, log-normal distributions, gradual adoption curves

**Key Files:**
- `devmetrics/collectors/github_client.py` — GitHub auth & rate limiting
- `devmetrics/collectors/dummy_data_generator.py` — Generates 7 JSON files with 90 days history
- `devmetrics/collectors/space_collector.py` — SPACE metrics from GitHub API
- `devmetrics/collectors/copilot_collector.py` — Copilot metrics from Enterprise API (stub)
- `.env.example` — Configuration template for tokens & settings

**Patterns:**
- Rate limit checking before every API call (`handle_rate_limit()`)
- Structured logging throughout (module-level loggers)
- Deterministic dummy data (same seed = same output) for reproducible demos
- Schema compatibility: dummy data matches real collector output format
