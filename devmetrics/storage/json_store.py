"""JSON data store for loading DevMetrics data files."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class JSONStore:
    """Load and cache JSON data files for DevMetrics."""
    
    def __init__(self, data_dir: str = "devmetrics/data"):
        """Initialize JSON store.
        
        Args:
            data_dir: Base directory for data files (relative to project root)
        """
        self.data_dir = Path(data_dir)
        self.space_dir = self.data_dir / "space"
        self.copilot_dir = self.data_dir / "copilot"
        self._cache = {}
        
    def _load_json(self, path: Path) -> Dict:
        """Load JSON file with caching."""
        cache_key = str(path)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self._cache[cache_key] = data
            logger.debug(f"Loaded {path}")
            return data
        except FileNotFoundError:
            logger.error(f"Data file not found: {path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
            return {}
    
    def clear_cache(self):
        """Clear cached data to force reload."""
        self._cache.clear()
    
    # SPACE Metrics
    
    def load_pr_cycle_times(self) -> Dict:
        """Load PR cycle time data.
        
        Returns:
            {
                "prs": [...],
                "summary": {
                    "median_hours": float,
                    "p95_hours": float,
                    "total_prs": int
                },
                "generated_at": str
            }
        """
        return self._load_json(self.space_dir / "pr_cycle_times.json")
    
    def load_review_turnaround(self) -> Dict:
        """Load review turnaround data.
        
        Returns:
            {
                "reviews": [...],
                "summary": {
                    "median_hours": float,
                    "p95_hours": float,
                    "total_reviews": int
                },
                "generated_at": str
            }
        """
        return self._load_json(self.space_dir / "review_turnaround.json")
    
    def load_rework_rates(self) -> Dict:
        """Load rework rate data.
        
        Returns:
            {
                "weekly_rates": [...],
                "summary": {
                    "overall_rate": float,
                    "trend": str
                },
                "generated_at": str
            }
        """
        return self._load_json(self.space_dir / "rework_rates.json")
    
    def load_wip_counts(self) -> Dict:
        """Load WIP count data.
        
        Returns:
            {
                "daily_wip": [...],
                "summary": {
                    "avg_wip_per_repo": float,
                    "max_wip": int,
                    "total_snapshots": int
                },
                "generated_at": str
            }
        """
        return self._load_json(self.space_dir / "wip_counts.json")
    
    # Copilot Metrics
    
    def load_copilot_usage(self) -> Dict:
        """Load Copilot usage metrics.
        
        Returns:
            {
                "daily_usage": [...],
                "summary": {
                    "total_suggestions": int,
                    "total_acceptances": int,
                    "avg_active_users": float
                },
                "generated_at": str
            }
        """
        return self._load_json(self.copilot_dir / "usage_metrics.json")
    
    def load_acceptance_rates(self) -> Dict:
        """Load Copilot acceptance rate data.
        
        Returns:
            {
                "daily_rates": [...],
                "summary": {
                    "overall_rate": float,
                    "trend": str
                },
                "generated_at": str
            }
        """
        return self._load_json(self.copilot_dir / "acceptance_rates.json")
    
    def load_seat_utilization(self) -> Dict:
        """Load Copilot seat utilization data.
        
        Returns:
            {
                "daily_utilization": [...],
                "summary": {
                    "current_utilization": float,
                    "avg_utilization": float,
                    "total_seats": int
                },
                "generated_at": str
            }
        """
        return self._load_json(self.copilot_dir / "seat_utilization.json")
    
    def get_data_timestamp(self, data: Dict) -> Optional[datetime]:
        """Extract generated_at timestamp from data."""
        if "generated_at" in data:
            try:
                return datetime.fromisoformat(data["generated_at"])
            except (ValueError, TypeError):
                return None
        return None
