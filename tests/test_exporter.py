"""Tests for configuration exporter."""

from __future__ import annotations

import json

import pytest

from aiohomematic_config import ExportedConfiguration, export_configuration, import_configuration


class TestExportConfiguration:
    """Test export_configuration function."""

    def test_export_contains_timestamp(self) -> None:
        result = export_configuration(
            device_address="0001D3C99C36D0",
            model="HmIP-eTRV-2",
            channel_address="0001D3C99C36D0:1",
            channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
            paramset_key="MASTER",
            values={},
        )
        data = json.loads(result)
        assert "exported_at" in data
        assert len(data["exported_at"]) > 0

    def test_export_returns_valid_json(self) -> None:
        result = export_configuration(
            device_address="0001D3C99C36D0",
            model="HmIP-eTRV-2",
            channel_address="0001D3C99C36D0:1",
            channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
            paramset_key="MASTER",
            values={"TEMPERATURE_OFFSET": 1.5},
        )
        data = json.loads(result)
        assert data["version"] == "1.0"
        assert data["model"] == "HmIP-eTRV-2"
        assert data["values"]["TEMPERATURE_OFFSET"] == 1.5


class TestImportConfiguration:
    """Test import_configuration function."""

    def test_import_invalid_json(self) -> None:
        with pytest.raises((ValueError, json.JSONDecodeError)):
            import_configuration(json_data="not json")

    def test_import_missing_version(self) -> None:
        data = json.dumps(
            {
                "exported_at": "2026-01-01T00:00:00",
                "device_address": "X",
                "model": "X",
                "channel_address": "X:1",
                "channel_type": "X",
                "paramset_key": "MASTER",
                "values": {},
            }
        )
        with pytest.raises(ValueError, match="Unsupported configuration version"):
            import_configuration(json_data=data)

    def test_import_non_object(self) -> None:
        with pytest.raises(TypeError, match="expected a JSON object"):
            import_configuration(json_data="[1, 2, 3]")

    def test_import_wrong_version(self) -> None:
        data = json.dumps(
            {
                "version": "99.0",
                "exported_at": "2026-01-01T00:00:00",
                "device_address": "X",
                "model": "X",
                "channel_address": "X:1",
                "channel_type": "X",
                "paramset_key": "MASTER",
                "values": {},
            }
        )
        with pytest.raises(ValueError, match="Unsupported configuration version"):
            import_configuration(json_data=data)

    def test_roundtrip(self) -> None:
        exported = export_configuration(
            device_address="0001D3C99C36D0",
            model="HmIP-eTRV-2",
            channel_address="0001D3C99C36D0:1",
            channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
            paramset_key="MASTER",
            values={"TEMPERATURE_OFFSET": 1.5, "BOOST_TIME_PERIOD": 10},
        )
        imported = import_configuration(json_data=exported)
        assert isinstance(imported, ExportedConfiguration)
        assert imported.model == "HmIP-eTRV-2"
        assert imported.values["TEMPERATURE_OFFSET"] == 1.5
        assert imported.values["BOOST_TIME_PERIOD"] == 10


class TestExportedConfiguration:
    """Test ExportedConfiguration model."""

    def test_model_fields(self) -> None:
        config = ExportedConfiguration(
            exported_at="2026-01-01T00:00:00",
            device_address="X",
            model="Y",
            channel_address="X:1",
            channel_type="Z",
            paramset_key="MASTER",
            values={"A": 1},
        )
        assert config.version == "1.0"
        assert config.device_address == "X"
        assert config.values == {"A": 1}
