"""
JSON Storage Layer for DevMetrics Dashboard

Provides generic JSON file operations with schema validation,
time-series data management, and query helpers.
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSONStore:
    """Generic JSON file storage with schema validation and query capabilities."""

    def __init__(self, base_path: str = "data"):
        """
        Initialize JSON store.

        Args:
            base_path: Root directory for all data files
        """
        self.base_path = Path(base_path)
        self.schemas_path = Path("schemas")
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directory structure if it doesn't exist."""
        directories = [
            self.base_path / "space",
            self.base_path / "copilot",
            self.base_path / "snapshots",
            self.base_path / "logs",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def read(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Read JSON data from file.

        Args:
            filepath: Path to JSON file (relative to base_path)

        Returns:
            Parsed JSON data or None if file doesn't exist
        """
        full_path = self.base_path / filepath
        if not full_path.exists():
            logger.warning(f"File not found: {full_path}")
            return None

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Read {full_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {full_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading {full_path}: {e}")
            return None

    def write(self, filepath: str, data: Dict[str, Any], indent: int = 2):
        """
        Write JSON data to file.

        Args:
            filepath: Path to JSON file (relative to base_path)
            data: Data to write
            indent: JSON indentation level
        """
        full_path = self.base_path / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
            logger.info(f"Wrote {full_path}")
        except Exception as e:
            logger.error(f"Error writing {full_path}: {e}")
            raise

    def append_data(self, filepath: str, new_records: List[Dict[str, Any]]):
        """
        Append records to existing JSON data array.

        Args:
            filepath: Path to JSON file
            new_records: List of records to append to data array
        """
        existing = self.read(filepath)
        if existing is None:
            logger.error(f"Cannot append to non-existent file: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")

        if "data" not in existing:
            logger.error(f"File {filepath} has no 'data' array")
            raise ValueError(f"Invalid structure in {filepath}")

        existing["data"].extend(new_records)
        existing["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"

        self.write(filepath, existing)
        logger.info(f"Appended {len(new_records)} records to {filepath}")

    def initialize_file(
        self,
        filepath: str,
        schema_version: str = "1.0",
        source: str = "dummy_data",
    ) -> Dict[str, Any]:
        """
        Create a new data file with standard structure.

        Args:
            filepath: Path to JSON file
            schema_version: Version of the schema
            source: Data source type

        Returns:
            Initial data structure
        """
        initial_data = {
            "metadata": {
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "version": schema_version,
                "source": source,
            },
            "data": [],
        }

        self.write(filepath, initial_data)
        logger.info(f"Initialized {filepath}")
        return initial_data

    def query_by_date_range(
        self,
        filepath: str,
        start_date: Union[str, date],
        end_date: Union[str, date],
        date_field: str = "date",
    ) -> List[Dict[str, Any]]:
        """
        Query records within a date range.

        Args:
            filepath: Path to JSON file
            start_date: Start date (YYYY-MM-DD or date object)
            end_date: End date (YYYY-MM-DD or date object)
            date_field: Name of the date field to filter on

        Returns:
            Filtered list of records
        """
        data = self.read(filepath)
        if not data or "data" not in data:
            return []

        # Convert dates to strings if needed
        if isinstance(start_date, date):
            start_date = start_date.isoformat()
        if isinstance(end_date, date):
            end_date = end_date.isoformat()

        filtered = [
            record
            for record in data["data"]
            if date_field in record
            and start_date <= record[date_field][:10] <= end_date
        ]

        logger.info(
            f"Query {filepath}: {len(filtered)} records between {start_date} and {end_date}"
        )
        return filtered

    def query_by_repo(self, filepath: str, repo: str) -> List[Dict[str, Any]]:
        """
        Filter records by repository name.

        Args:
            filepath: Path to JSON file
            repo: Repository name to filter on

        Returns:
            Filtered list of records
        """
        data = self.read(filepath)
        if not data or "data" not in data:
            return []

        filtered = [record for record in data["data"] if record.get("repo") == repo]

        logger.info(f"Query {filepath}: {len(filtered)} records for repo {repo}")
        return filtered

    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent daily snapshot.

        Returns:
            Latest snapshot data or None if no snapshots exist
        """
        snapshots_dir = self.base_path / "snapshots"
        if not snapshots_dir.exists():
            return None

        snapshot_files = sorted(snapshots_dir.glob("*.json"), reverse=True)
        if not snapshot_files:
            return None

        return self.read(f"snapshots/{snapshot_files[0].name}")

    def list_snapshots(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[str]:
        """
        List available snapshot dates.

        Args:
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)

        Returns:
            List of snapshot dates (YYYY-MM-DD format)
        """
        snapshots_dir = self.base_path / "snapshots"
        if not snapshots_dir.exists():
            return []

        snapshot_files = [f.stem for f in sorted(snapshots_dir.glob("*.json"))]

        if start_date or end_date:
            filtered = []
            for snapshot_date in snapshot_files:
                if start_date and snapshot_date < start_date:
                    continue
                if end_date and snapshot_date > end_date:
                    continue
                filtered.append(snapshot_date)
            return filtered

        return snapshot_files

    def get_stats(self, filepath: str) -> Dict[str, Any]:
        """
        Get basic statistics about a data file.

        Args:
            filepath: Path to JSON file

        Returns:
            Dictionary with count, date range, etc.
        """
        data = self.read(filepath)
        if not data or "data" not in data:
            return {"count": 0, "error": "No data found"}

        records = data["data"]
        stats = {
            "count": len(records),
            "last_updated": data["metadata"].get("last_updated"),
            "source": data["metadata"].get("source"),
        }

        # Try to determine date range
        date_fields = ["date", "opened_at", "merged_at", "week_start"]
        for field in date_fields:
            if records and field in records[0]:
                dates = [r[field][:10] for r in records if field in r]
                if dates:
                    stats["date_range"] = {"start": min(dates), "end": max(dates)}
                break

        return stats

    def validate_structure(self, filepath: str) -> bool:
        """
        Validate that a file has required metadata and data structure.
        
        Snapshots have a different structure (single object, not array).

        Args:
            filepath: Path to JSON file

        Returns:
            True if structure is valid, False otherwise
        """
        data = self.read(filepath)
        if not data:
            return False

        # Snapshots have different structure
        if "snapshots/" in filepath:
            required_fields = ["date", "metadata", "space", "copilot"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"{filepath}: Missing '{field}' field")
                    return False
            logger.info(f"{filepath}: Snapshot structure valid")
            return True

        # Regular metrics files
        if "metadata" not in data:
            logger.error(f"{filepath}: Missing 'metadata' field")
            return False

        if "data" not in data:
            logger.error(f"{filepath}: Missing 'data' field")
            return False

        metadata = data["metadata"]
        required_meta = ["last_updated", "version"]
        for field in required_meta:
            if field not in metadata:
                logger.error(f"{filepath}: Missing metadata.{field}")
                return False

        if not isinstance(data["data"], list):
            logger.error(f"{filepath}: 'data' must be an array")
            return False

        logger.info(f"{filepath}: Structure valid")
        return True

    def backup(self, filepath: str):
        """
        Create a timestamped backup of a data file.

        Args:
            filepath: Path to JSON file
        """
        full_path = self.base_path / filepath
        if not full_path.exists():
            logger.warning(f"Cannot backup non-existent file: {filepath}")
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = full_path.with_suffix(f".{timestamp}.json.bak")

        try:
            import shutil

            shutil.copy2(full_path, backup_path)
            logger.info(f"Backed up {filepath} to {backup_path.name}")
        except Exception as e:
            logger.error(f"Error backing up {filepath}: {e}")
            raise


# Convenience functions for common file paths
def get_space_store() -> JSONStore:
    """Get JSONStore instance for SPACE metrics."""
    return JSONStore("data")


def get_copilot_store() -> JSONStore:
    """Get JSONStore instance for Copilot metrics."""
    return JSONStore("data")


def get_snapshot_store() -> JSONStore:
    """Get JSONStore instance for daily snapshots."""
    return JSONStore("data")
