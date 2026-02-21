**Phase 2: AI ROI (Copilot)**

Streamlit page displaying Copilot adoption and ROI metrics.

**Acceptance Criteria:**
- [ ] Page accessible at `/copilot_dashboard`
- [ ] Active users trend chart (line chart over time)
- [ ] Seat utilization % (gauge + time series)
- [ ] Acceptance rate trends (line chart)
- [ ] Time saved chart (hours + $ value, bar chart by week/month)
- [ ] Summary cards (total acceptances, total $ saved, avg acceptance rate)
- [ ] Interactive filters (date range)
- [ ] Config controls for ROI multipliers

**Dependencies:**
All Phase 2 collectors must be complete (issues #7-10).

**Tech:**
- Streamlit multipage app
- Plotly for charts (gauges, line, bar)
- Load data from `data/copilot/*.json`
