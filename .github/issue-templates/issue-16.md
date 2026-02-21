**Cross-Cutting**

Containerize the application for single-command startup.

**Acceptance Criteria:**
- [ ] `Dockerfile` builds Python 3.11+ image with all dependencies
- [ ] Playwright browser (chromium) installed in image
- [ ] `docker-compose.yml` defines service with volume mounts
- [ ] Volumes for `data/` and `logs/` persist across restarts
- [ ] Port 8501 (Streamlit default) exposed
- [ ] `.env` file loaded into container
- [ ] `docker compose up` starts dashboard
- [ ] Health check endpoint configured (Streamlit `/healthz`)

**Project Structure:**
```
devmetrics/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app.py
```

**Startup Command:**
```bash
docker compose up
# Dashboard accessible at http://localhost:8501
```
