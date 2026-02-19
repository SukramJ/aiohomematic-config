"""Tests for configuration change log."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from aiohomematic_config import ConfigChangeEntry, ConfigChangeLog, build_change_diff


class TestBuildChangeDiff:
    """Tests for the build_change_diff function."""

    def test_changed_value(self) -> None:
        """Test diff detects changed value."""
        result = build_change_diff(
            old_values={"PARAM_A": 10},
            new_values={"PARAM_A": 20},
        )
        assert result == {"PARAM_A": {"old": 10, "new": 20}}

    def test_empty_values(self) -> None:
        """Test diff with empty dicts."""
        result = build_change_diff(old_values={}, new_values={})
        assert result == {}

    def test_identical_values(self) -> None:
        """Test diff with identical values."""
        values = {"PARAM_A": 10, "PARAM_B": "hello"}
        result = build_change_diff(old_values=values, new_values=values)
        assert result == {}

    def test_multiple_changes(self) -> None:
        """Test diff with multiple changed parameters."""
        result = build_change_diff(
            old_values={"A": 1, "B": 2, "C": 3},
            new_values={"A": 1, "B": 99, "C": 100},
        )
        assert result == {
            "B": {"old": 2, "new": 99},
            "C": {"old": 3, "new": 100},
        }

    def test_new_param_in_new_values(self) -> None:
        """Test diff detects parameter added in new values."""
        result = build_change_diff(
            old_values={},
            new_values={"PARAM_A": 42},
        )
        assert result == {"PARAM_A": {"old": None, "new": 42}}

    def test_old_only_params_not_reported(self) -> None:
        """Test that parameters only in old_values are not reported."""
        result = build_change_diff(
            old_values={"A": 1, "B": 2},
            new_values={"A": 1},
        )
        assert result == {}


class TestConfigChangeEntry:
    """Tests for the ConfigChangeEntry dataclass."""

    def test_field_access(self) -> None:
        """Test field access on ConfigChangeEntry."""
        entry = ConfigChangeEntry(
            timestamp="2026-01-01T00:00:00+00:00",
            entry_id="entry1",
            interface_id="iface1",
            channel_address="VCU:1",
            device_name="Device",
            device_model="Model",
            paramset_key="MASTER",
            changes={"P": {"old": 1, "new": 2}},
            source="manual",
        )
        assert entry.timestamp == "2026-01-01T00:00:00+00:00"
        assert entry.entry_id == "entry1"
        assert entry.interface_id == "iface1"
        assert entry.channel_address == "VCU:1"
        assert entry.device_name == "Device"
        assert entry.device_model == "Model"
        assert entry.paramset_key == "MASTER"
        assert entry.changes == {"P": {"old": 1, "new": 2}}
        assert entry.source == "manual"

    def test_frozen(self) -> None:
        """Test that ConfigChangeEntry is frozen."""
        entry = ConfigChangeEntry(
            timestamp="t",
            entry_id="e",
            interface_id="i",
            channel_address="c",
            device_name="d",
            device_model="m",
            paramset_key="MASTER",
            changes={},
            source="s",
        )
        with pytest.raises(FrozenInstanceError):
            entry.timestamp = "new"  # type: ignore[misc]


class TestConfigChangeLog:
    """Tests for the ConfigChangeLog class."""

    def test_add_and_get(self) -> None:
        """Test adding and retrieving entries."""
        log = ConfigChangeLog()
        log.add(
            entry_id="e1",
            interface_id="iface1",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={"P": {"old": 1, "new": 2}},
            source="manual",
        )
        entries, total = log.get_entries()
        assert total == 1
        assert len(entries) == 1
        assert entries[0].entry_id == "e1"

    def test_clear_by_entry_id(self) -> None:
        """Test clearing entries by entry_id."""
        log = ConfigChangeLog()
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="manual",
        )
        log.add(
            entry_id="e2",
            interface_id="iface",
            channel_address="VCU:2",
            device_name="Dev2",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="manual",
        )
        cleared = log.clear_by_entry_id(entry_id="e1")
        assert cleared == 1
        entries, total = log.get_entries()
        assert total == 1
        assert entries[0].entry_id == "e2"

    def test_clear_by_entry_id_none_matching(self) -> None:
        """Test clearing when no entries match."""
        log = ConfigChangeLog()
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="manual",
        )
        cleared = log.clear_by_entry_id(entry_id="e99")
        assert cleared == 0
        _, total = log.get_entries()
        assert total == 1

    def test_default_max_entries(self) -> None:
        """Test default max_entries is 500."""
        log = ConfigChangeLog()
        assert log.max_entries == 500

    def test_fifo_eviction(self) -> None:
        """Test FIFO eviction when max_entries exceeded."""
        log = ConfigChangeLog(max_entries=3)
        for i in range(5):
            log.add(
                entry_id=f"e{i}",
                interface_id="iface",
                channel_address="VCU:1",
                device_name="Dev",
                device_model="Mod",
                paramset_key="MASTER",
                changes={},
                source="manual",
            )
        entries, total = log.get_entries(limit=10)
        assert total == 3
        # Only the last 3 entries should remain
        entry_ids = [e.entry_id for e in entries]
        # Most recent first
        assert entry_ids == ["e4", "e3", "e2"]

    def test_get_entries_filter_channel_address(self) -> None:
        """Test filtering by channel_address."""
        log = ConfigChangeLog()
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="manual",
        )
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:2",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="manual",
        )
        entries, total = log.get_entries(channel_address="VCU:2")
        assert total == 1
        assert entries[0].channel_address == "VCU:2"

    def test_get_entries_filter_entry_id(self) -> None:
        """Test filtering by entry_id."""
        log = ConfigChangeLog()
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="manual",
        )
        log.add(
            entry_id="e2",
            interface_id="iface",
            channel_address="VCU:2",
            device_name="Dev2",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="manual",
        )
        entries, total = log.get_entries(entry_id="e1")
        assert total == 1
        assert entries[0].entry_id == "e1"

    def test_get_entries_limit(self) -> None:
        """Test limiting returned entries."""
        log = ConfigChangeLog()
        for i in range(10):
            log.add(
                entry_id="e1",
                interface_id="iface",
                channel_address="VCU:1",
                device_name="Dev",
                device_model="Mod",
                paramset_key="MASTER",
                changes={},
                source=f"s{i}",
            )
        entries, total = log.get_entries(limit=3)
        assert total == 10
        assert len(entries) == 3
        # Most recent first
        assert entries[0].source == "s9"
        assert entries[1].source == "s8"
        assert entries[2].source == "s7"

    def test_load_entries(self) -> None:
        """Test loading entries from serialized dicts."""
        log = ConfigChangeLog()
        raw = [
            {
                "timestamp": "2026-01-01T00:00:00+00:00",
                "entry_id": "e1",
                "interface_id": "iface",
                "channel_address": "VCU:1",
                "device_name": "Dev",
                "device_model": "Mod",
                "paramset_key": "MASTER",
                "changes": {"P": {"old": 1, "new": 2}},
                "source": "manual",
            }
        ]
        log.load_entries(raw_entries=raw)
        entries, total = log.get_entries()
        assert total == 1
        assert entries[0].entry_id == "e1"
        assert entries[0].changes == {"P": {"old": 1, "new": 2}}

    def test_load_entries_missing_fields_default(self) -> None:
        """Test that missing fields in raw entries default to empty strings."""
        log = ConfigChangeLog()
        log.load_entries(raw_entries=[{}])
        entries, total = log.get_entries()
        assert total == 1
        assert entries[0].timestamp == ""
        assert entries[0].entry_id == ""
        assert entries[0].changes == {}

    def test_load_entries_replaces_existing(self) -> None:
        """Test that load_entries replaces existing entries."""
        log = ConfigChangeLog()
        log.add(
            entry_id="old",
            interface_id="iface",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="manual",
        )
        log.load_entries(
            raw_entries=[
                {
                    "timestamp": "t",
                    "entry_id": "new",
                    "interface_id": "i",
                    "channel_address": "c",
                    "device_name": "d",
                    "device_model": "m",
                    "paramset_key": "MASTER",
                    "changes": {},
                    "source": "s",
                }
            ]
        )
        entries, total = log.get_entries()
        assert total == 1
        assert entries[0].entry_id == "new"

    def test_load_entries_respects_max(self) -> None:
        """Test that load_entries respects max_entries."""
        log = ConfigChangeLog(max_entries=2)
        raw = [
            {
                "timestamp": f"t{i}",
                "entry_id": f"e{i}",
                "interface_id": "i",
                "channel_address": "c",
                "device_name": "d",
                "device_model": "m",
                "paramset_key": "MASTER",
                "changes": {},
                "source": "s",
            }
            for i in range(5)
        ]
        log.load_entries(raw_entries=raw)
        _, total = log.get_entries()
        assert total == 2

    def test_max_entries_property(self) -> None:
        """Test max_entries property returns configured value."""
        log = ConfigChangeLog(max_entries=100)
        assert log.max_entries == 100

    def test_most_recent_first_ordering(self) -> None:
        """Test entries are returned most recent first."""
        log = ConfigChangeLog()
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="first",
        )
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={},
            source="second",
        )
        entries, _ = log.get_entries()
        assert entries[0].source == "second"
        assert entries[1].source == "first"

    def test_to_dicts_roundtrip(self) -> None:
        """Test serialization roundtrip via to_dicts and load_entries."""
        log = ConfigChangeLog()
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:1",
            device_name="Dev",
            device_model="Mod",
            paramset_key="MASTER",
            changes={"P": {"old": 1, "new": 2}},
            source="manual",
        )
        log.add(
            entry_id="e1",
            interface_id="iface",
            channel_address="VCU:2",
            device_name="Dev2",
            device_model="Mod2",
            paramset_key="VALUES",
            changes={"Q": {"old": "a", "new": "b"}},
            source="import",
        )

        serialized = log.to_dicts()
        assert len(serialized) == 2

        log2 = ConfigChangeLog()
        log2.load_entries(raw_entries=serialized)
        entries, total = log2.get_entries()
        assert total == 2
        assert entries[0].entry_id == "e1"
        assert entries[0].channel_address == "VCU:2"
        assert entries[1].channel_address == "VCU:1"
