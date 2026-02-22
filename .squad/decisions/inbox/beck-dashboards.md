# Dashboard Architecture & Chart Choices

**Date:** 2025-01-22  
**Agent:** Beck (Frontend Dev)  
**Context:** Building Streamlit dashboards for SPACE and Copilot metrics

## Decision: Data Access Layer Pattern

**Choice:** Created `storage/json_store.py` as an abstraction layer between data files and UI.

**Rationale:**
- Decouples data source from dashboard code
- Makes it easy to swap dummy data → live GitHub API later
- Centralizes data loading logic with caching
- Clean API: `store.load_pr_cycle_times()` vs. manual JSON parsing everywhere
- Single source of truth for data schemas

**Impact:**
- Dashboards import from `storage.json_store` instead of reading files directly
- Future: Replace JSONStore with APIStore without touching dashboard code
- Team: Watney/Johanssen can modify data format without breaking UI

---

## Decision: Plotly for All Charts

**Choice:** Used Plotly/Plotly Express for all visualizations, not Matplotlib/Seaborn.

**Rationale:**
- Interactive by default (hover tooltips, zoom, pan)
- Better UX for exploring data
- Consistent styling across all charts
- Built-in responsiveness
- Express API for common charts (box, area), Graph Objects for custom layouts

**Impact:**
- Users can hover over any data point for details
- No separate "details" views needed - charts are self-documenting
- Trade-off: Slightly larger bundle size, but worth it for interactivity

---

## Decision: KPI Cards Before Charts

**Choice:** Put summary KPI cards at the top of each dashboard.

**Rationale:**
- Quick "at-a-glance" view without scrolling
- Executives/managers want numbers first, then trends
- Matches industry dashboard patterns (Datadog, Grafana, etc.)
- Faster load: Simple metrics render before heavy charts

**Impact:**
- Users see key numbers immediately
- Can skip detailed charts if KPIs look good
- Makes dashboards useful even on mobile

---

## Decision: Date Range + Repo Filters

**Choice:** Added date range picker and multi-select repo filter on SPACE dashboard.

**Rationale:**
- Large teams need to focus on specific time periods
- Per-repo analysis essential (not just org-wide averages)
- Common use case: "Show me backend-api PRs from last month"
- Filtering is immediate with Streamlit reactivity

**Impact:**
- More flexible than hardcoded "last 30 days"
- Repo filter enables team-specific retrospectives
- Trade-off: More complex filtering logic, but worth the flexibility

---

## Decision: Moving Averages on Noisy Metrics

**Choice:** Added moving averages (7-day, 3-week) to acceptance rate and rework rate charts.

**Rationale:**
- Daily metrics are noisy - hard to see real trends
- Moving averages smooth out weekday/weekend variations
- Standard practice in time series analysis
- Keeps raw data visible (scatter/bars) + trend line overlay

**Impact:**
- Users can see both daily variance AND overall direction
- Easier to spot "improving" vs. "stable" vs. "worsening" trends
- Aligns with summary trend indicators ("improving", "declining")

---

## Decision: ROI Calculator with Configurable Parameters

**Choice:** Made ROI calculation transparent with editable hourly rate and seat cost inputs.

**Rationale:**
- Different orgs have different developer rates ($50/hr → $200/hr)
- Seat cost varies (individual vs. enterprise pricing)
- Transparent calculation builds trust (not a "black box" number)
- Users can model different scenarios

**Impact:**
- ROI numbers are customizable per viewer's context
- Explanation panel shows exact calculation method
- Defensible in exec presentations ("here's how we calculated this")

---

## Decision: Cumulative ROI Chart

**Choice:** Show cumulative value saved vs. cumulative cost over time, not just "total ROI".

**Rationale:**
- Shows ROI growth trajectory, not just endpoint
- Visual "break-even point" where value exceeds cost
- More compelling narrative: "We've saved $X since adoption"
- Easier to extrapolate future value

**Impact:**
- Stronger business case for Copilot investment
- Can point to specific dates when ROI turned positive
- Forecast: "At this rate, we'll save $Y by end of quarter"

---

## Team Impact

These decisions apply to **all future dashboards** in DevMetrics. Patterns established:
1. Data access layer (storage module)
2. Plotly for charts
3. KPI cards first
4. Date range filters
5. Moving averages for noisy data
6. Transparent calculations with configurable inputs

**Files:**
- Architecture documented in `devmetrics/DASHBOARDS_README.md`
- Reusable patterns in `storage/json_store.py` and both dashboard files
