**Phase 2: AI ROI (Copilot)**

Track Copilot suggestion acceptance rate over time.

**Acceptance Criteria:**
- [ ] Calculates daily acceptance rate: `acceptances / suggestions * 100`
- [ ] Stores results in `data/copilot/acceptance_rates.json`
- [ ] Charts acceptance % trends (line chart)
- [ ] Breakdown by language/editor (if data available)
- [ ] Identifies adoption patterns (improving/declining trends)

**Calculation:**
`acceptance_rate = (total_code_acceptances / total_code_suggestions) * 100`

**Data Schema:**
```json
{
  "date": "2024-01-15",
  "suggestions": 3420,
  "acceptances": 987,
  "acceptance_rate_pct": 28.86,
  "language": "python",
  "editor": "vscode"
}
```
