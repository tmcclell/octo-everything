**Phase 2: AI ROI (Copilot)**

Convert Copilot acceptances into estimated time/$ saved.

**Acceptance Criteria:**
- [ ] Configurable time-per-acceptance multiplier (default: 55 seconds)
- [ ] Configurable hourly developer rate (default: $75/hr)
- [ ] Calculates daily/weekly/monthly time saved (hours)
- [ ] Converts time saved → dollar value
- [ ] Stores results in `data/copilot/time_saved.json`
- [ ] UI inputs for adjusting multipliers

**Calculation:**
```
time_saved_hours = (acceptances * seconds_per_acceptance) / 3600
dollar_value = time_saved_hours * hourly_rate
```

**Data Schema:**
```json
{
  "date": "2024-01-15",
  "acceptances": 987,
  "time_saved_hours": 15.07,
  "dollar_value": 1130.25,
  "config": {
    "seconds_per_acceptance": 55,
    "hourly_rate": 75
  }
}
```
