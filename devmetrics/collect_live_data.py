"""Collect live data from GitHub APIs and write to JSON store.

Runs CopilotCollector and SpaceCollector, saving results as JSON files
that the dashboards read at runtime.
"""

import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _save(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"Saved {path}")


def collect_copilot(data_dir: Path):
    from collectors.copilot_collector import CopilotCollector

    collector = CopilotCollector()
    copilot_dir = data_dir / "copilot"

    _save(copilot_dir / "usage_metrics.json", collector.collect_usage_metrics())
    _save(copilot_dir / "acceptance_rates.json", collector.collect_acceptance_rates())
    _save(copilot_dir / "seat_utilization.json", collector.collect_seat_utilization())


def collect_space(data_dir: Path):
    from collectors.github_client import GitHubClient
    from collectors.space_collector import SpaceCollector

    repos_env = os.getenv("GITHUB_REPOS", "")
    repos = [r.strip() for r in repos_env.split(",") if r.strip()]

    if not repos:
        logger.warning("GITHUB_REPOS not set — skipping SPACE metrics collection")
        return

    client = GitHubClient()
    collector = SpaceCollector(client, repos)
    space_dir = data_dir / "space"

    _save(space_dir / "pr_cycle_times.json", collector.collect_pr_cycle_times())
    _save(space_dir / "review_turnaround.json", collector.collect_review_turnaround())
    _save(space_dir / "rework_rates.json", collector.collect_rework_rates())
    _save(space_dir / "wip_counts.json", collector.collect_wip_counts())

    client.close()


def main():
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    logger.info("Starting live data collection...")

    try:
        collect_copilot(data_dir)
    except Exception:
        logger.exception("Copilot collection failed")

    try:
        collect_space(data_dir)
    except Exception:
        logger.exception("SPACE collection failed")

    logger.info("Live data collection complete")


if __name__ == "__main__":
    main()
