"""Tests for JSONStore - read/write, schema validation, queries."""

import pytest
import json
from pathlib import Path
from datetime import datetime, date

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from storage.json_store import JSONStore


class TestJSONStoreInit:
    """Test JSONStore initialization."""

    def test_init_with_default_path(self, tmp_path, monkeypatch):
        """Test initialization with default data path."""
        monkeypatch.chdir(tmp_path)
        store = JSONStore()
        
        assert store.base_path == Path("data")

    def test_init_with_custom_path(self, tmp_path):
        """Test initialization with custom data path."""
        custom_path = tmp_path / "custom_data"
        store = JSONStore(base_path=str(custom_path))
        
        assert store.base_path == custom_path

    def test_init_creates_directories(self, tmp_path):
        """Test that initialization creates necessary directories."""
        store = JSONStore(base_path=str(tmp_path))
        
        assert (tmp_path / "space").exists()
        assert (tmp_path / "copilot").exists()
        assert (tmp_path / "snapshots").exists()
        assert (tmp_path / "logs").exists()


class TestJSONStoreReadWrite:
    """Test basic read and write operations."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore with temp directory."""
        return JSONStore(base_path=str(tmp_path))

    def test_write_json(self, store, tmp_path):
        """Test writing JSON data to file."""
        data = {"test": "data", "count": 42}
        store.write("test/data.json", data)
        
        file_path = tmp_path / "test" / "data.json"
        assert file_path.exists()
        
        with open(file_path) as f:
            loaded = json.load(f)
        
        assert loaded == data

    def test_read_existing_file(self, store, tmp_path):
        """Test reading existing JSON file."""
        data = {"test": "data"}
        store.write("test.json", data)
        
        loaded = store.read("test.json")
        
        assert loaded == data

    def test_read_nonexistent_file(self, store):
        """Test reading nonexistent file returns None."""
        result = store.read("nonexistent.json")
        
        assert result is None

    def test_read_invalid_json(self, store, tmp_path):
        """Test reading invalid JSON returns None."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("{ invalid json")
        
        result = store.read("invalid.json")
        
        assert result is None

    def test_write_creates_parent_dirs(self, store, tmp_path):
        """Test that write creates parent directories."""
        store.write("deep/nested/dir/data.json", {"test": "data"})
        
        assert (tmp_path / "deep" / "nested" / "dir" / "data.json").exists()


class TestJSONStoreInitializeFile:
    """Test file initialization."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore with temp directory."""
        return JSONStore(base_path=str(tmp_path))

    def test_initialize_file_structure(self, store):
        """Test that initialize creates proper structure."""
        result = store.initialize_file("test.json")
        
        assert "metadata" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert "last_updated" in result["metadata"]
        assert "version" in result["metadata"]
        assert "source" in result["metadata"]

    def test_initialize_file_creates_file(self, store, tmp_path):
        """Test that initialize creates the file."""
        store.initialize_file("test.json")
        
        assert (tmp_path / "test.json").exists()

    def test_initialize_file_custom_params(self, store):
        """Test initialize with custom parameters."""
        result = store.initialize_file(
            "test.json",
            schema_version="2.0",
            source="api"
        )
        
        assert result["metadata"]["version"] == "2.0"
        assert result["metadata"]["source"] == "api"


class TestJSONStoreAppendData:
    """Test appending data to files."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore with initialized file."""
        store = JSONStore(base_path=str(tmp_path))
        store.initialize_file("test.json")
        return store

    def test_append_data_success(self, store):
        """Test successful data append."""
        new_records = [
            {"id": 1, "value": "a"},
            {"id": 2, "value": "b"}
        ]
        
        store.append_data("test.json", new_records)
        
        data = store.read("test.json")
        assert len(data["data"]) == 2
        assert data["data"][0]["id"] == 1

    def test_append_data_nonexistent_file(self, store):
        """Test append to nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            store.append_data("nonexistent.json", [{"test": "data"}])

    def test_append_data_invalid_structure(self, store, tmp_path):
        """Test append to file without data array raises error."""
        store.write("invalid.json", {"no_data_array": []})
        
        with pytest.raises(ValueError):
            store.append_data("invalid.json", [{"test": "data"}])

    def test_append_updates_metadata(self, store):
        """Test that append updates last_updated timestamp."""
        initial = store.read("test.json")
        initial_time = initial["metadata"]["last_updated"]
        
        import time
        time.sleep(0.1)
        
        store.append_data("test.json", [{"test": "data"}])
        
        updated = store.read("test.json")
        assert updated["metadata"]["last_updated"] != initial_time


class TestJSONStoreQueryByDateRange:
    """Test date range queries."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore with test data."""
        store = JSONStore(base_path=str(tmp_path))
        store.initialize_file("test.json")
        
        records = [
            {"date": "2024-01-10", "value": 1},
            {"date": "2024-01-15", "value": 2},
            {"date": "2024-01-20", "value": 3},
            {"date": "2024-01-25", "value": 4}
        ]
        store.append_data("test.json", records)
        
        return store

    def test_query_by_date_range(self, store):
        """Test querying records within date range."""
        results = store.query_by_date_range(
            "test.json",
            "2024-01-12",
            "2024-01-22"
        )
        
        assert len(results) == 2
        assert results[0]["value"] == 2
        assert results[1]["value"] == 3

    def test_query_by_date_range_with_date_objects(self, store):
        """Test querying with date objects."""
        results = store.query_by_date_range(
            "test.json",
            date(2024, 1, 12),
            date(2024, 1, 22)
        )
        
        assert len(results) == 2

    def test_query_by_date_range_no_matches(self, store):
        """Test query with no matching records."""
        results = store.query_by_date_range(
            "test.json",
            "2024-02-01",
            "2024-02-28"
        )
        
        assert len(results) == 0

    def test_query_by_date_range_nonexistent_file(self, store):
        """Test query on nonexistent file returns empty list."""
        results = store.query_by_date_range(
            "nonexistent.json",
            "2024-01-01",
            "2024-01-31"
        )
        
        assert results == []


class TestJSONStoreQueryByRepo:
    """Test repository filtering."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore with test data."""
        store = JSONStore(base_path=str(tmp_path))
        store.initialize_file("test.json")
        
        records = [
            {"repo": "repo1", "value": 1},
            {"repo": "repo2", "value": 2},
            {"repo": "repo1", "value": 3}
        ]
        store.append_data("test.json", records)
        
        return store

    def test_query_by_repo(self, store):
        """Test filtering records by repository."""
        results = store.query_by_repo("test.json", "repo1")
        
        assert len(results) == 2
        assert all(r["repo"] == "repo1" for r in results)

    def test_query_by_repo_no_matches(self, store):
        """Test query with no matching repos."""
        results = store.query_by_repo("test.json", "repo3")
        
        assert len(results) == 0


class TestJSONStoreSnapshots:
    """Test snapshot operations."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore with snapshots."""
        store = JSONStore(base_path=str(tmp_path))
        
        # Create test snapshots
        for i in range(3):
            snapshot = {
                "date": f"2024-01-{i+10:02d}",
                "metadata": {},
                "space": {},
                "copilot": {}
            }
            store.write(f"snapshots/2024-01-{i+10:02d}.json", snapshot)
        
        return store

    def test_get_latest_snapshot(self, store):
        """Test getting most recent snapshot."""
        latest = store.get_latest_snapshot()
        
        assert latest is not None
        assert latest["date"] == "2024-01-12"

    def test_get_latest_snapshot_no_snapshots(self, tmp_path):
        """Test getting latest when no snapshots exist."""
        store = JSONStore(base_path=str(tmp_path))
        
        latest = store.get_latest_snapshot()
        
        assert latest is None

    def test_list_snapshots(self, store):
        """Test listing all snapshots."""
        snapshots = store.list_snapshots()
        
        assert len(snapshots) == 3
        assert "2024-01-10" in snapshots

    def test_list_snapshots_with_date_filter(self, store):
        """Test listing snapshots with date range."""
        snapshots = store.list_snapshots(
            start_date="2024-01-11",
            end_date="2024-01-12"
        )
        
        assert len(snapshots) == 2
        assert "2024-01-10" not in snapshots


class TestJSONStoreGetStats:
    """Test statistics operations."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore with test data."""
        store = JSONStore(base_path=str(tmp_path))
        store.initialize_file("test.json", source="test_source")
        
        records = [
            {"date": "2024-01-10", "value": 1},
            {"date": "2024-01-20", "value": 2}
        ]
        store.append_data("test.json", records)
        
        return store

    def test_get_stats(self, store):
        """Test getting file statistics."""
        stats = store.get_stats("test.json")
        
        assert stats["count"] == 2
        assert stats["source"] == "test_source"
        assert "last_updated" in stats
        assert "date_range" in stats
        assert stats["date_range"]["start"] == "2024-01-10"
        assert stats["date_range"]["end"] == "2024-01-20"

    def test_get_stats_nonexistent_file(self, store):
        """Test stats for nonexistent file."""
        stats = store.get_stats("nonexistent.json")
        
        assert stats["count"] == 0
        assert "error" in stats


class TestJSONStoreValidation:
    """Test schema validation."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore."""
        return JSONStore(base_path=str(tmp_path))

    def test_validate_structure_valid_file(self, store):
        """Test validation of valid file structure."""
        store.initialize_file("test.json")
        
        result = store.validate_structure("test.json")
        
        assert result is True

    def test_validate_structure_missing_metadata(self, store):
        """Test validation fails for missing metadata."""
        store.write("test.json", {"data": []})
        
        result = store.validate_structure("test.json")
        
        assert result is False

    def test_validate_structure_missing_data(self, store):
        """Test validation fails for missing data array."""
        store.write("test.json", {"metadata": {}})
        
        result = store.validate_structure("test.json")
        
        assert result is False

    def test_validate_structure_snapshot(self, store):
        """Test validation of snapshot structure."""
        snapshot = {
            "date": "2024-01-10",
            "metadata": {},
            "space": {},
            "copilot": {}
        }
        store.write("snapshots/2024-01-10.json", snapshot)
        
        result = store.validate_structure("snapshots/2024-01-10.json")
        
        assert result is True

    def test_validate_structure_invalid_snapshot(self, store):
        """Test validation fails for invalid snapshot."""
        store.write("snapshots/bad.json", {"date": "2024-01-10"})
        
        result = store.validate_structure("snapshots/bad.json")
        
        assert result is False

    def test_validate_structure_nonexistent_file(self, store):
        """Test validation of nonexistent file returns False."""
        result = store.validate_structure("nonexistent.json")
        
        assert result is False


class TestJSONStoreBackup:
    """Test backup functionality."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore with test file."""
        store = JSONStore(base_path=str(tmp_path))
        store.write("test.json", {"test": "data"})
        return store, tmp_path

    def test_backup_creates_file(self, store):
        """Test that backup creates backup file."""
        store_obj, tmp_path = store
        
        store_obj.backup("test.json")
        
        # Find backup file
        backup_files = list(tmp_path.glob("test.*.json.bak"))
        assert len(backup_files) == 1

    def test_backup_preserves_content(self, store):
        """Test that backup preserves file content."""
        store_obj, tmp_path = store
        
        store_obj.backup("test.json")
        
        # Read backup
        backup_files = list(tmp_path.glob("test.*.json.bak"))
        with open(backup_files[0]) as f:
            backup_data = json.load(f)
        
        assert backup_data == {"test": "data"}

    def test_backup_nonexistent_file(self, store):
        """Test backup of nonexistent file does nothing."""
        store_obj, tmp_path = store
        
        # Should not raise error
        store_obj.backup("nonexistent.json")


class TestJSONStoreEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create JSONStore."""
        return JSONStore(base_path=str(tmp_path))

    def test_empty_data_array(self, store):
        """Test handling empty data arrays."""
        store.initialize_file("test.json")
        
        stats = store.get_stats("test.json")
        
        assert stats["count"] == 0

    def test_unicode_content(self, store):
        """Test handling unicode content."""
        data = {"message": "Hello 世界 🌍"}
        store.write("test.json", data)
        
        loaded = store.read("test.json")
        
        assert loaded == data

    def test_nested_objects(self, store):
        """Test handling deeply nested objects."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }
        store.write("test.json", data)
        
        loaded = store.read("test.json")
        
        assert loaded["level1"]["level2"]["level3"]["value"] == "deep"

    def test_date_field_variations(self, store):
        """Test query with different date field names."""
        store.initialize_file("test.json")
        records = [
            {"opened_at": "2024-01-10", "value": 1},
            {"opened_at": "2024-01-20", "value": 2}
        ]
        store.append_data("test.json", records)
        
        results = store.query_by_date_range(
            "test.json",
            "2024-01-01",
            "2024-01-15",
            date_field="opened_at"
        )
        
        assert len(results) == 1
