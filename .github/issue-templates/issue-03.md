**Phase 1: SPACE Metrics**

Calculate time from PR open to first review comment.

**Acceptance Criteria:**
- [ ] Collector fetches PR reviews via PyGithub
- [ ] Calculates time between PR `created_at` and first review `submitted_at`
- [ ] Stores results in `data/space/review_turnaround.json`
- [ ] Handles PRs with no reviews (null/NA value)
- [ ] Aggregates median turnaround time per repo

**API Endpoint:**
`GET /repos/{owner}/{repo}/pulls/{number}/reviews`

**Data Schema:**
```json
{
  "pr_id": 123,
  "repo": "owner/repo",
  "created_at": "2024-01-15T10:00:00Z",
  "first_review_at": "2024-01-15T14:20:00Z",
  "turnaround_hours": 4.33
}
```
