**Phase 2: AI ROI (Copilot)**

Pull metrics from GitHub Enterprise Copilot API.

**Acceptance Criteria:**
- [ ] Collector calls `/orgs/{org}/copilot/metrics` endpoint
- [ ] Fetches daily active users, suggestions, acceptances
- [ ] Stores results in `data/copilot/usage_metrics.json`
- [ ] Handles API lag (metrics available 3 days after event)
- [ ] Parses NDJSON response format

**API Endpoint:**
`GET /enterprises/{enterprise}/copilot/metrics/reports`

**Required Token Scope:**
`manage_billing:copilot` or `read:enterprise`

**Data Schema:**
```json
{
  "date": "2024-01-15",
  "total_active_users": 85,
  "total_engaged_users": 72,
  "total_code_suggestions": 3420,
  "total_code_acceptances": 987,
  "total_code_lines_suggested": 12450,
  "total_code_lines_accepted": 3890
}
```

**Note:** Uses dummy data generator for v1 (no enterprise API access).
