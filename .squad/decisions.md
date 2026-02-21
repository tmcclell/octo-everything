# Decisions

All team decisions are recorded here. Append only — never edit past entries.

---

## 2025-01-22: Project Initialization

**Context:** Starting DevMetrics Dashboard project  
**Decision:** Build with Python 3.11+, Streamlit, PyGithub, Plotly, Playwright, Docker  
**Rationale:** Plan specified in `.github/plans/plan-devmetrics-v1.md` — user directive  
**Impact:** All code follows this tech stack

---

## 2025-01-22: Dummy Data First

**Context:** No access to enterprise GitHub API  
**Decision:** Use dummy data generator from day 1 for all metrics  
**Rationale:** Plan specifies dummy data to ensure immediate testability  
**Impact:** All dashboards must work with generated data before attempting live API
