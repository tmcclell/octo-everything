**Phase 1: SPACE Metrics**

Setup GitHub authentication via PAT or GitHub App token.

**Acceptance Criteria:**
- [ ] `.env.example` template created with `GITHUB_TOKEN` variable
- [ ] `.env` file loading implemented (gitignored)
- [ ] Token validation on app startup
- [ ] Clear error message if token missing/invalid

**Technical Notes:**
- Use `python-dotenv` for environment variable management
- Support both classic PAT and fine-grained tokens
- Required scopes: `repo`, `read:org` for SPACE metrics
