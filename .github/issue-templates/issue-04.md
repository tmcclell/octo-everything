**Phase 1: SPACE Metrics**

Calculate ratio of PRs with 'changes requested' reviews vs total merged.

**Acceptance Criteria:**
- [ ] Collector counts PRs with at least one review state = `CHANGES_REQUESTED`
- [ ] Computes weekly rework rate percentage
- [ ] Stores results in `data/space/rework_rates.json`
- [ ] Handles PRs with multiple reviews (any changes_requested = rework)

**API Endpoint:**
`GET /repos/{owner}/{repo}/pulls/{number}/reviews`

**Calculation:**
`rework_rate = (PRs_with_changes_requested / total_merged_PRs) * 100`

**Data Schema:**
```json
{
  "week": "2024-W03",
  "repo": "owner/repo",
  "total_merged": 42,
  "with_rework": 9,
  "rework_rate_pct": 21.4
}
```
