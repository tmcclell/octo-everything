**Cross-Cutting**

Generate realistic sample data for all metrics.

**Acceptance Criteria:**
- [ ] Generator creates 90 days of historical data
- [ ] PR cycle times: normal distribution, median ~18hr, weekday-weighted
- [ ] Review turnaround: log-normal, median ~4hr
- [ ] Rework rate: 15-30% with slight downward trend
- [ ] WIP counts: random walk 3-15 per repo
- [ ] Copilot usage: gradual adoption curve (20→80% over 90 days)
- [ ] Acceptance rate: 25-35% with upward trend
- [ ] Seat utilization: 100 seats, active growing 40→85
- [ ] Time saved: derived from acceptances × 55s multiplier
- [ ] Deterministic with seed (reproducible data)
- [ ] Same schema as real collectors

**Script Location:**
`collectors/dummy_data_generator.py`

**Usage:**
```bash
python -m collectors.dummy_data_generator
```

**Output:**
Writes to all `data/` subdirectories using same JSON schemas.
