**Phase 2: AI ROI (Copilot)**

Track active users vs total assigned Copilot seats.

**Acceptance Criteria:**
- [ ] Collector fetches seat assignment data
- [ ] Calculates utilization % (active/total seats)
- [ ] Stores time-series data in `data/copilot/seat_utilization.json`
- [ ] Identifies inactive seats (no activity in 30+ days)
- [ ] Charts utilization trends over time

**API Endpoint:**
`GET /orgs/{org}/copilot/billing/seats`

**Data Schema:**
```json
{
  "date": "2024-01-15",
  "total_seats": 100,
  "active_seats": 85,
  "utilization_pct": 85.0,
  "inactive_30d": 15
}
```
