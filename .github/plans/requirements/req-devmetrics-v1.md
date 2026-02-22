# DevMetrics v1 — Requirements

## Overview

Requirements for the DevMetrics Dashboard v1 release, covering SPACE metrics and AI ROI (Copilot) tracking.

---

## REQ-001: PR Cycle Time Dashboard

**Priority:** P1-High  
**Area:** SPACE  
**Status:** Implemented

### User Story

> As a **engineering manager**, I want to see **PR cycle time trends** across repositories so that I can **identify bottlenecks in our delivery pipeline**.

### Acceptance Criteria

- [ ] Dashboard shows open-to-merge duration aggregated across configured repos
- [ ] Time period is selectable (7d, 30d, 90d)
- [ ] Data refreshes on page load from stored JSON
- [ ] Chart uses Plotly for interactive visualization

---

## REQ-002: Time to First Review

**Priority:** P1-High  
**Area:** SPACE  
**Status:** Implemented

### User Story

> As an **engineering manager**, I want to track **time to first review** so that I can **detect review turnaround bottlenecks**.

### Acceptance Criteria

- [ ] Shows median and P90 time-to-first-review per repo
- [ ] Highlights repos exceeding SLA threshold (configurable)
- [ ] Trend line over time

---

## REQ-003: Copilot Usage Metrics

**Priority:** P1-High  
**Area:** Copilot  
**Status:** Implemented

### User Story

> As a **technology leader**, I want to see **Copilot adoption and usage metrics** so that I can **measure AI ROI and justify seat investment**.

### Acceptance Criteria

- [ ] Daily active users trend
- [ ] Suggestion count and acceptance rate
- [ ] Seat utilization (active vs assigned)
- [ ] Time saved estimator with configurable multiplier

---

## REQ-004: Rework Rate Tracking

**Priority:** P2-Medium  
**Area:** SPACE  
**Status:** Implemented

### User Story

> As a **team lead**, I want to see **rework rate** (PRs with changes requested vs total merged) so that I can **improve code quality practices**.

### Acceptance Criteria

- [ ] Ratio displayed as percentage
- [ ] Trend over configurable time period
- [ ] Breakdown by repository

---

## REQ-005: Health Check Monitoring

**Priority:** P2-Medium  
**Area:** Infrastructure  
**Status:** Implemented

### User Story

> As an **SRE**, I want **automated health checks** on the dashboard so that I can **detect outages before users report them**.

### Acceptance Criteria

- [ ] Playwright-based dashboard verification
- [ ] Screenshot capture on failure
- [ ] Event logging for API errors and rate limits
