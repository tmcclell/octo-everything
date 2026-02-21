**Phase 1: SPACE Metrics**

Streamlit page displaying trend charts for all SPACE metrics.

**Acceptance Criteria:**
- [ ] Page accessible at `/space_dashboard`
- [ ] Charts for PR cycle time trends (line/area chart)
- [ ] Charts for review turnaround (histogram + median line)
- [ ] Rework rate weekly trends (bar chart)
- [ ] WIP counts over time (line chart per repo)
- [ ] Interactive filters (date range, repo selection)
- [ ] Summary stats cards (median cycle time, avg turnaround, current WIP)

**Dependencies:**
All Phase 1 collectors must be complete (issues #1-5).

**Tech:**
- Streamlit multipage app structure
- Plotly for interactive charts
- Load data from `data/space/*.json`
