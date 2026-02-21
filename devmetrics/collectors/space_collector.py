"""SPACE metrics collector for GitHub pull request data.

Collects metrics for:
- PR cycle time (open → merge duration)
- Review turnaround (open → first review)
- Rework rate (changes requested / PRs merged)
- WIP (work in progress) counts
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .github_client import GitHubClient

logger = logging.getLogger(__name__)


class SpaceCollector:
    """Collector for SPACE framework metrics from GitHub."""

    def __init__(self, client: GitHubClient, repos: List[str]):
        """Initialize SPACE collector.
        
        Args:
            client: Authenticated GitHubClient instance
            repos: List of repository names (format: "owner/repo")
        """
        self.client = client
        self.repos = repos
        logger.info(f"Initialized SpaceCollector for {len(repos)} repositories")

    def collect_pr_cycle_times(
        self, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict:
        """Collect PR cycle time data (open → merge duration).
        
        Args:
            since: Start date for data collection (default: 90 days ago)
            until: End date for data collection (default: now)
            
        Returns:
            dict: PR cycle time data with schema matching dummy_data_generator
        """
        if since is None:
            since = datetime.now() - timedelta(days=90)
        if until is None:
            until = datetime.now()
        
        logger.info(f"Collecting PR cycle times from {since.date()} to {until.date()}")
        
        prs = []
        
        for repo_name in self.repos:
            try:
                repo = self.client.get_repository(repo_name)
                
                # Fetch closed/merged PRs
                pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')
                
                for pr in pulls:
                    # Only include merged PRs
                    if not pr.merged_at:
                        continue
                    
                    # Filter by date range
                    if pr.created_at < since or pr.created_at > until:
                        continue
                    
                    cycle_time_hours = (pr.merged_at - pr.created_at).total_seconds() / 3600
                    
                    prs.append({
                        "repo": repo_name.split('/')[-1],
                        "pr_number": pr.number,
                        "created_at": pr.created_at.isoformat(),
                        "merged_at": pr.merged_at.isoformat(),
                        "cycle_time_hours": round(cycle_time_hours, 2),
                        "author": pr.user.login
                    })
                
                logger.info(f"Collected {len([p for p in prs if repo_name.endswith(p['repo'])])} PRs from {repo_name}")
                
            except Exception as e:
                logger.error(f"Error collecting PRs from {repo_name}: {e}")
                continue
        
        # Calculate summary statistics
        if prs:
            import numpy as np
            cycle_times = [pr["cycle_time_hours"] for pr in prs]
            summary = {
                "median_hours": round(float(np.median(cycle_times)), 2),
                "p95_hours": round(float(np.percentile(cycle_times, 95)), 2),
                "total_prs": len(prs)
            }
        else:
            summary = {"median_hours": 0.0, "p95_hours": 0.0, "total_prs": 0}
        
        return {
            "prs": prs,
            "summary": summary,
            "collected_at": datetime.now().isoformat(),
            "source": "github_api"
        }

    def collect_review_turnaround(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict:
        """Collect review turnaround time (PR open → first review).
        
        Args:
            since: Start date for data collection (default: 90 days ago)
            until: End date for data collection (default: now)
            
        Returns:
            dict: Review turnaround data with schema matching dummy_data_generator
        """
        if since is None:
            since = datetime.now() - timedelta(days=90)
        if until is None:
            until = datetime.now()
        
        logger.info(f"Collecting review turnaround from {since.date()} to {until.date()}")
        
        reviews = []
        
        for repo_name in self.repos:
            try:
                repo = self.client.get_repository(repo_name)
                pulls = repo.get_pulls(state='all', sort='updated', direction='desc')
                
                for pr in pulls:
                    if pr.created_at < since or pr.created_at > until:
                        continue
                    
                    # Get first review
                    pr_reviews = pr.get_reviews()
                    if pr_reviews.totalCount == 0:
                        continue
                    
                    first_review = list(pr_reviews)[0]
                    turnaround_hours = (first_review.submitted_at - pr.created_at).total_seconds() / 3600
                    
                    reviews.append({
                        "repo": repo_name.split('/')[-1],
                        "pr_number": pr.number,
                        "created_at": pr.created_at.isoformat(),
                        "first_review_at": first_review.submitted_at.isoformat(),
                        "turnaround_hours": round(turnaround_hours, 2)
                    })
                
                logger.info(f"Collected {len([r for r in reviews if repo_name.endswith(r['repo'])])} reviews from {repo_name}")
                
            except Exception as e:
                logger.error(f"Error collecting reviews from {repo_name}: {e}")
                continue
        
        # Calculate summary
        if reviews:
            import numpy as np
            turnaround_times = [r["turnaround_hours"] for r in reviews]
            summary = {
                "median_hours": round(float(np.median(turnaround_times)), 2),
                "p95_hours": round(float(np.percentile(turnaround_times, 95)), 2),
                "total_reviews": len(reviews)
            }
        else:
            summary = {"median_hours": 0.0, "p95_hours": 0.0, "total_reviews": 0}
        
        return {
            "reviews": reviews,
            "summary": summary,
            "collected_at": datetime.now().isoformat(),
            "source": "github_api"
        }

    def collect_rework_rates(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict:
        """Collect rework rate (PRs with changes requested / total merged).
        
        Args:
            since: Start date for data collection (default: 90 days ago)
            until: End date for data collection (default: now)
            
        Returns:
            dict: Rework rate data with schema matching dummy_data_generator
        """
        if since is None:
            since = datetime.now() - timedelta(days=90)
        if until is None:
            until = datetime.now()
        
        logger.info(f"Collecting rework rates from {since.date()} to {until.date()}")
        
        # Group by week
        weekly_data = {}
        
        for repo_name in self.repos:
            try:
                repo = self.client.get_repository(repo_name)
                pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')
                
                for pr in pulls:
                    if not pr.merged_at or pr.created_at < since or pr.created_at > until:
                        continue
                    
                    # Get week start
                    week_start = (pr.merged_at - timedelta(days=pr.merged_at.weekday())).date()
                    
                    if week_start not in weekly_data:
                        weekly_data[week_start] = {"total_merged": 0, "changes_requested": 0}
                    
                    weekly_data[week_start]["total_merged"] += 1
                    
                    # Check if changes were requested
                    reviews = pr.get_reviews()
                    has_changes_requested = any(
                        review.state == "CHANGES_REQUESTED" 
                        for review in reviews
                    )
                    
                    if has_changes_requested:
                        weekly_data[week_start]["changes_requested"] += 1
                
                logger.info(f"Processed rework data from {repo_name}")
                
            except Exception as e:
                logger.error(f"Error collecting rework data from {repo_name}: {e}")
                continue
        
        # Format weekly rates
        weekly_rates = []
        for week_start in sorted(weekly_data.keys()):
            data = weekly_data[week_start]
            rework_rate = data["changes_requested"] / data["total_merged"] if data["total_merged"] > 0 else 0.0
            
            weekly_rates.append({
                "week_start": week_start.isoformat(),
                "total_merged": data["total_merged"],
                "changes_requested": data["changes_requested"],
                "rework_rate": round(rework_rate, 3)
            })
        
        # Calculate trend
        if len(weekly_rates) >= 2:
            import numpy as np
            first_half = np.mean([w["rework_rate"] for w in weekly_rates[:len(weekly_rates)//2]])
            second_half = np.mean([w["rework_rate"] for w in weekly_rates[len(weekly_rates)//2:]])
            
            if second_half < first_half - 0.02:
                trend = "improving"
            elif second_half > first_half + 0.02:
                trend = "worsening"
            else:
                trend = "stable"
            
            overall_rate = np.mean([w["rework_rate"] for w in weekly_rates])
        else:
            trend = "unknown"
            overall_rate = 0.0
        
        return {
            "weekly_rates": weekly_rates,
            "summary": {
                "overall_rate": round(float(overall_rate), 3),
                "trend": trend
            },
            "collected_at": datetime.now().isoformat(),
            "source": "github_api"
        }

    def collect_wip_counts(self) -> Dict:
        """Collect current WIP (work in progress) counts - open PRs per repo.
        
        Returns:
            dict: WIP count data with schema matching dummy_data_generator
        """
        logger.info("Collecting current WIP counts")
        
        daily_wip = []
        current_date = datetime.now().date()
        
        for repo_name in self.repos:
            try:
                repo = self.client.get_repository(repo_name)
                open_prs = repo.get_pulls(state='open')
                
                daily_wip.append({
                    "date": current_date.isoformat(),
                    "repo": repo_name.split('/')[-1],
                    "open_prs": open_prs.totalCount
                })
                
                logger.info(f"{repo_name}: {open_prs.totalCount} open PRs")
                
            except Exception as e:
                logger.error(f"Error collecting WIP from {repo_name}: {e}")
                continue
        
        # Calculate summary
        if daily_wip:
            import numpy as np
            wip_counts = [d["open_prs"] for d in daily_wip]
            summary = {
                "avg_wip_per_repo": round(float(np.mean(wip_counts)), 2),
                "max_wip": int(np.max(wip_counts)),
                "total_snapshots": len(daily_wip)
            }
        else:
            summary = {"avg_wip_per_repo": 0.0, "max_wip": 0, "total_snapshots": 0}
        
        return {
            "daily_wip": daily_wip,
            "summary": summary,
            "collected_at": datetime.now().isoformat(),
            "source": "github_api"
        }
