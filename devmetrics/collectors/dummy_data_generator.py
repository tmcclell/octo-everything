"""Generate realistic dummy data for SPACE and Copilot metrics.

This module creates sample data that mimics real-world patterns for development
metrics when live GitHub API access is unavailable.
"""

import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import numpy as np

logger = logging.getLogger(__name__)


class DummyDataGenerator:
    """Generate realistic dummy data for all DevMetrics dashboard metrics."""

    def __init__(self, seed: int = 42, data_dir: str = "data"):
        """Initialize generator with deterministic seed.
        
        Args:
            seed: Random seed for reproducible data generation
            data_dir: Base directory for data output (relative to project root)
        """
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.data_dir = Path(data_dir)
        self.space_dir = self.data_dir / "space"
        self.copilot_dir = self.data_dir / "copilot"
        self.snapshots_dir = self.data_dir / "snapshots"
        
        # Configuration
        self.repos = ["backend-api", "frontend-web", "mobile-app", "data-pipeline", "infra-config"]
        self.team_size = 25
        self.days_history = 90
        self.end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.start_date = self.end_date - timedelta(days=self.days_history)
        
        logger.info(f"Initialized DummyDataGenerator with seed={seed}, {self.days_history} days history")

    def generate_all(self):
        """Generate all dummy data files."""
        logger.info("Starting dummy data generation...")
        
        self._ensure_directories()
        
        # SPACE metrics
        self.generate_pr_cycle_times()
        self.generate_review_turnaround()
        self.generate_rework_rates()
        self.generate_wip_counts()
        
        # Copilot metrics
        self.generate_copilot_usage()
        self.generate_acceptance_rates()
        self.generate_seat_utilization()
        
        logger.info("Dummy data generation complete")

    def _ensure_directories(self):
        """Create data directories if they don't exist."""
        self.space_dir.mkdir(parents=True, exist_ok=True)
        self.copilot_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def _is_weekday(self, date: datetime) -> bool:
        """Check if date is a weekday (Mon-Fri)."""
        return date.weekday() < 5

    def _generate_dates(self) -> List[datetime]:
        """Generate list of dates in history range."""
        return [self.start_date + timedelta(days=i) for i in range(self.days_history)]

    def generate_pr_cycle_times(self):
        """Generate PR cycle time data (open → merge duration).
        
        Schema:
        {
            "prs": [
                {
                    "repo": str,
                    "pr_number": int,
                    "created_at": ISO timestamp,
                    "merged_at": ISO timestamp,
                    "cycle_time_hours": float,
                    "author": str
                }
            ],
            "summary": {
                "median_hours": float,
                "p95_hours": float,
                "total_prs": int
            }
        }
        """
        logger.info("Generating PR cycle time data...")
        
        prs = []
        pr_id = 1000
        
        for date in self._generate_dates():
            # More PRs on weekdays
            if self._is_weekday(date):
                num_prs = random.randint(3, 8)
            else:
                num_prs = random.randint(0, 2)
            
            for _ in range(num_prs):
                repo = random.choice(self.repos)
                
                # Cycle time: log-normal distribution, median ~18 hours
                cycle_time_hours = np.random.lognormal(mean=2.89, sigma=0.8)
                cycle_time_hours = max(1.0, min(cycle_time_hours, 168.0))  # 1hr to 7 days
                
                created_at = date + timedelta(hours=random.uniform(8, 18))
                merged_at = created_at + timedelta(hours=cycle_time_hours)
                
                prs.append({
                    "repo": repo,
                    "pr_number": pr_id,
                    "created_at": created_at.isoformat(),
                    "merged_at": merged_at.isoformat(),
                    "cycle_time_hours": round(cycle_time_hours, 2),
                    "author": f"dev{random.randint(1, self.team_size)}"
                })
                pr_id += 1
        
        cycle_times = [pr["cycle_time_hours"] for pr in prs]
        data = {
            "prs": prs,
            "summary": {
                "median_hours": round(float(np.median(cycle_times)), 2),
                "p95_hours": round(float(np.percentile(cycle_times, 95)), 2),
                "total_prs": len(prs)
            },
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed
        }
        
        self._write_json(self.space_dir / "pr_cycle_times.json", data)
        logger.info(f"Generated {len(prs)} PRs with median cycle time {data['summary']['median_hours']}hrs")

    def generate_review_turnaround(self):
        """Generate review turnaround time data (PR open → first review).
        
        Schema:
        {
            "reviews": [
                {
                    "repo": str,
                    "pr_number": int,
                    "created_at": ISO timestamp,
                    "first_review_at": ISO timestamp,
                    "turnaround_hours": float
                }
            ],
            "summary": {
                "median_hours": float,
                "p95_hours": float,
                "total_reviews": int
            }
        }
        """
        logger.info("Generating review turnaround data...")
        
        reviews = []
        pr_id = 1000
        
        for date in self._generate_dates():
            if self._is_weekday(date):
                num_prs = random.randint(3, 8)
            else:
                num_prs = random.randint(0, 2)
            
            for _ in range(num_prs):
                repo = random.choice(self.repos)
                
                # Review turnaround: log-normal, median ~4 hours
                turnaround_hours = np.random.lognormal(mean=1.4, sigma=0.9)
                turnaround_hours = max(0.5, min(turnaround_hours, 72.0))  # 30min to 3 days
                
                created_at = date + timedelta(hours=random.uniform(8, 18))
                first_review_at = created_at + timedelta(hours=turnaround_hours)
                
                reviews.append({
                    "repo": repo,
                    "pr_number": pr_id,
                    "created_at": created_at.isoformat(),
                    "first_review_at": first_review_at.isoformat(),
                    "turnaround_hours": round(turnaround_hours, 2)
                })
                pr_id += 1
        
        turnaround_times = [r["turnaround_hours"] for r in reviews]
        data = {
            "reviews": reviews,
            "summary": {
                "median_hours": round(float(np.median(turnaround_times)), 2),
                "p95_hours": round(float(np.percentile(turnaround_times, 95)), 2),
                "total_reviews": len(reviews)
            },
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed
        }
        
        self._write_json(self.space_dir / "review_turnaround.json", data)
        logger.info(f"Generated {len(reviews)} reviews with median turnaround {data['summary']['median_hours']}hrs")

    def generate_rework_rates(self):
        """Generate rework rate data (changes requested / PRs merged).
        
        Schema:
        {
            "weekly_rates": [
                {
                    "week_start": ISO date,
                    "total_merged": int,
                    "changes_requested": int,
                    "rework_rate": float (0-1)
                }
            ],
            "summary": {
                "overall_rate": float,
                "trend": str ("improving" | "stable" | "worsening")
            }
        }
        """
        logger.info("Generating rework rate data...")
        
        weekly_rates = []
        current_date = self.start_date
        
        while current_date < self.end_date:
            week_start = current_date
            total_merged = random.randint(15, 35)
            
            # Rework rate with slight downward trend (improvement over time)
            weeks_elapsed = (current_date - self.start_date).days // 7
            base_rate = 0.25 - (weeks_elapsed * 0.01)  # Start at 25%, improve by 1% per week
            base_rate = max(0.15, base_rate)  # Floor at 15%
            
            rework_rate = base_rate + random.uniform(-0.05, 0.05)
            changes_requested = int(total_merged * rework_rate)
            
            weekly_rates.append({
                "week_start": week_start.date().isoformat(),
                "total_merged": total_merged,
                "changes_requested": changes_requested,
                "rework_rate": round(rework_rate, 3)
            })
            
            current_date += timedelta(days=7)
        
        overall_rate = np.mean([w["rework_rate"] for w in weekly_rates])
        first_half = np.mean([w["rework_rate"] for w in weekly_rates[:len(weekly_rates)//2]])
        second_half = np.mean([w["rework_rate"] for w in weekly_rates[len(weekly_rates)//2:]])
        
        if second_half < first_half - 0.02:
            trend = "improving"
        elif second_half > first_half + 0.02:
            trend = "worsening"
        else:
            trend = "stable"
        
        data = {
            "weekly_rates": weekly_rates,
            "summary": {
                "overall_rate": round(float(overall_rate), 3),
                "trend": trend
            },
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed
        }
        
        self._write_json(self.space_dir / "rework_rates.json", data)
        logger.info(f"Generated {len(weekly_rates)} weeks of rework data, overall rate {data['summary']['overall_rate']:.1%}")

    def generate_wip_counts(self):
        """Generate WIP (work in progress) counts - daily open PRs per repo.
        
        Schema:
        {
            "daily_wip": [
                {
                    "date": ISO date,
                    "repo": str,
                    "open_prs": int
                }
            ],
            "summary": {
                "avg_wip_per_repo": float,
                "max_wip": int,
                "total_snapshots": int
            }
        }
        """
        logger.info("Generating WIP count data...")
        
        daily_wip = []
        
        # Initialize WIP for each repo (random walk)
        repo_wip = {repo: random.randint(5, 10) for repo in self.repos}
        
        for date in self._generate_dates():
            for repo in self.repos:
                # Random walk: +/- 0-3 PRs per day, constrained to 2-20 range
                change = random.randint(-3, 3)
                repo_wip[repo] = max(2, min(20, repo_wip[repo] + change))
                
                daily_wip.append({
                    "date": date.date().isoformat(),
                    "repo": repo,
                    "open_prs": repo_wip[repo]
                })
        
        wip_counts = [d["open_prs"] for d in daily_wip]
        data = {
            "daily_wip": daily_wip,
            "summary": {
                "avg_wip_per_repo": round(float(np.mean(wip_counts)), 2),
                "max_wip": int(np.max(wip_counts)),
                "total_snapshots": len(daily_wip)
            },
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed
        }
        
        self._write_json(self.space_dir / "wip_counts.json", data)
        logger.info(f"Generated {len(daily_wip)} WIP snapshots, avg {data['summary']['avg_wip_per_repo']} per repo")

    def generate_copilot_usage(self):
        """Generate Copilot usage metrics (daily active users, suggestions, acceptances).
        
        Schema:
        {
            "daily_usage": [
                {
                    "date": ISO date,
                    "active_users": int,
                    "engaged_users": int,
                    "suggestions": int,
                    "acceptances": int,
                    "lines_suggested": int,
                    "lines_accepted": int
                }
            ],
            "summary": {
                "total_suggestions": int,
                "total_acceptances": int,
                "avg_active_users": float
            }
        }
        """
        logger.info("Generating Copilot usage data...")
        
        daily_usage = []
        
        # Gradual adoption curve: start at 40% active, grow to 85%
        for i, date in enumerate(self._generate_dates()):
            progress = i / self.days_history
            
            # Active users grow over time
            base_active = 10 + int(15 * progress)
            
            # Weekday has more activity
            if self._is_weekday(date):
                active_users = base_active + random.randint(0, 3)
                engaged_users = int(active_users * random.uniform(0.7, 0.9))
                suggestions = random.randint(800, 1500)
            else:
                active_users = int(base_active * 0.3) + random.randint(0, 2)
                engaged_users = int(active_users * random.uniform(0.6, 0.8))
                suggestions = random.randint(100, 400)
            
            # Acceptance rate improves slightly over time (25% → 35%)
            acceptance_rate = 0.25 + (progress * 0.10) + random.uniform(-0.03, 0.03)
            acceptances = int(suggestions * acceptance_rate)
            
            daily_usage.append({
                "date": date.date().isoformat(),
                "active_users": active_users,
                "engaged_users": engaged_users,
                "suggestions": suggestions,
                "acceptances": acceptances,
                "lines_suggested": suggestions * random.randint(3, 8),
                "lines_accepted": acceptances * random.randint(3, 8)
            })
        
        data = {
            "daily_usage": daily_usage,
            "summary": {
                "total_suggestions": sum(d["suggestions"] for d in daily_usage),
                "total_acceptances": sum(d["acceptances"] for d in daily_usage),
                "avg_active_users": round(float(np.mean([d["active_users"] for d in daily_usage])), 2)
            },
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed
        }
        
        self._write_json(self.copilot_dir / "usage_metrics.json", data)
        logger.info(
            f"Generated {len(daily_usage)} days of Copilot usage, "
            f"{data['summary']['total_acceptances']} total acceptances"
        )

    def generate_acceptance_rates(self):
        """Generate Copilot acceptance rate trends.
        
        Schema:
        {
            "daily_rates": [
                {
                    "date": ISO date,
                    "acceptance_rate": float (0-1),
                    "suggestions": int,
                    "acceptances": int
                }
            ],
            "summary": {
                "overall_rate": float,
                "trend": str ("improving" | "stable" | "declining")
            }
        }
        """
        logger.info("Generating Copilot acceptance rate data...")
        
        daily_rates = []
        
        for i, date in enumerate(self._generate_dates()):
            progress = i / self.days_history
            
            # Base acceptance rate improves over time
            base_rate = 0.25 + (progress * 0.10)
            acceptance_rate = base_rate + random.uniform(-0.03, 0.03)
            acceptance_rate = max(0.15, min(0.45, acceptance_rate))
            
            if self._is_weekday(date):
                suggestions = random.randint(800, 1500)
            else:
                suggestions = random.randint(100, 400)
            
            acceptances = int(suggestions * acceptance_rate)
            
            daily_rates.append({
                "date": date.date().isoformat(),
                "acceptance_rate": round(acceptance_rate, 3),
                "suggestions": suggestions,
                "acceptances": acceptances
            })
        
        overall_rate = np.mean([d["acceptance_rate"] for d in daily_rates])
        first_half = np.mean([d["acceptance_rate"] for d in daily_rates[:len(daily_rates)//2]])
        second_half = np.mean([d["acceptance_rate"] for d in daily_rates[len(daily_rates)//2:]])
        
        if second_half > first_half + 0.02:
            trend = "improving"
        elif second_half < first_half - 0.02:
            trend = "declining"
        else:
            trend = "stable"
        
        data = {
            "daily_rates": daily_rates,
            "summary": {
                "overall_rate": round(float(overall_rate), 3),
                "trend": trend
            },
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed
        }
        
        self._write_json(self.copilot_dir / "acceptance_rates.json", data)
        logger.info(f"Generated {len(daily_rates)} days of acceptance rates, overall {data['summary']['overall_rate']:.1%}")

    def generate_seat_utilization(self):
        """Generate Copilot seat utilization data.
        
        Schema:
        {
            "daily_utilization": [
                {
                    "date": ISO date,
                    "total_seats": int,
                    "active_seats": int,
                    "utilization_rate": float (0-1)
                }
            ],
            "summary": {
                "current_utilization": float,
                "avg_utilization": float,
                "total_seats": int
            }
        }
        """
        logger.info("Generating Copilot seat utilization data...")
        
        daily_utilization = []
        total_seats = 100
        
        for i, date in enumerate(self._generate_dates()):
            progress = i / self.days_history
            
            # Active seats grow from 40 to 85
            base_active = 40 + int(45 * progress)
            active_seats = base_active + random.randint(-3, 3)
            active_seats = max(30, min(total_seats, active_seats))
            
            utilization_rate = active_seats / total_seats
            
            daily_utilization.append({
                "date": date.date().isoformat(),
                "total_seats": total_seats,
                "active_seats": active_seats,
                "utilization_rate": round(utilization_rate, 3)
            })
        
        avg_utilization = np.mean([d["utilization_rate"] for d in daily_utilization])
        current_utilization = daily_utilization[-1]["utilization_rate"]
        
        data = {
            "daily_utilization": daily_utilization,
            "summary": {
                "current_utilization": round(float(current_utilization), 3),
                "avg_utilization": round(float(avg_utilization), 3),
                "total_seats": total_seats
            },
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed
        }
        
        self._write_json(self.copilot_dir / "seat_utilization.json", data)
        logger.info(
            f"Generated {len(daily_utilization)} days of seat utilization, "
            f"current {data['summary']['current_utilization']:.1%}"
        )

    def _write_json(self, path: Path, data: dict):
        """Write data to JSON file with pretty formatting."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Wrote {path}")


def main():
    """CLI entry point for data generation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    generator = DummyDataGenerator(seed=42, data_dir="devmetrics/data")
    generator.generate_all()
    
    print("\n✅ Dummy data generation complete!")
    print(f"📁 Data written to: {generator.data_dir.resolve()}")
    print("\nGenerated files:")
    print("  - space/pr_cycle_times.json")
    print("  - space/review_turnaround.json")
    print("  - space/rework_rates.json")
    print("  - space/wip_counts.json")
    print("  - copilot/usage_metrics.json")
    print("  - copilot/acceptance_rates.json")
    print("  - copilot/seat_utilization.json")


if __name__ == "__main__":
    main()
