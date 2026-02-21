# DevMetrics Dashboard

A lightweight developer metrics dashboard focused on two pillars from the executive metrics strategy:

1. **SPACE Mindset** — Cycle time trends, rework rates, context switching, collaboration signals
2. **AI ROI (Copilot)** — Adoption rate, active usage, acceptance rate, seat utilization, time saved → $

Built with Python, Streamlit, and the GitHub API.

## Features

### SPACE Metrics
- **PR Cycle Time** — Open → merge duration aggregated across repos
- **Time to First Review** — Bottleneck detection for review turnaround
- **Rework Rate** — Ratio of PRs with changes requested vs total merged
- **WIP Tracker** — Open PR counts per repo over time

### AI ROI (Copilot)
- **Copilot Usage Metrics** — Daily active users, suggestions, acceptances
- **Acceptance Rate Trends** — Suggestion acceptance % over time
- **Seat Utilization** — Active users vs assigned seats
- **Time Saved Estimator** — Configurable multiplier → estimated $ saved

### Monitoring
- **Playwright Health Checks** — Automated dashboard verification with screenshot capture on failure
- **Event Logger** — API errors, rate limits, and data anomalies logged to JSON

## Quick Start

```bash
# Clone the repo
git clone https://github.com/tmcclell/octo-ev1-metrics.git
cd octo-ev1-metrics

# Copy and configure environment
cp .env.example .env
# Edit .env with your GitHub token

# Run with Docker
docker compose up
```

The dashboard will be available at `http://localhost:8501`.

## Dummy Data

Since enterprise API access is not currently available, the project includes a data generator that produces realistic sample data for all metrics.

```bash
# Generate fresh dummy data
python -m collectors.dummy_data_generator
```

Generated data uses the same JSON schema as the real collectors, so the dashboard works identically with either source.

## Project Structure

```
devmetrics/
├── app.py                    # Streamlit entry point
├── pages/
│   ├── space_dashboard.py    # SPACE metrics page
│   └── copilot_dashboard.py  # AI ROI page
├── collectors/
│   ├── github_client.py      # PyGithub + enterprise API wrapper
│   ├── space_collector.py    # PR cycle time, review, rework, WIP
│   ├── copilot_collector.py  # Enterprise Copilot metrics API calls
│   └── dummy_data_generator.py # Generate realistic sample data
├── storage/
│   └── json_store.py         # Read/write JSON data files
├── monitoring/
│   ├── health_check.py       # Playwright dashboard verification
│   └── event_logger.py       # Structured event logging
├── data/                     # JSON data files (Docker volume)
├── logs/                     # Log files (Docker volume)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Dependencies

- Python 3.11+
- Streamlit ≥ 1.30
- PyGithub ≥ 2.1
- Plotly ≥ 5.18
- Playwright ≥ 1.40
- python-dotenv ≥ 1.0

## Documentation

See [.github/plans/plan-devmetrics-v1.md](.github/plans/plan-devmetrics-v1.md) for the full v1 plan, API coverage analysis, and architecture details.

## License

Private — internal use only.
