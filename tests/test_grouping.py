"""Tests for parameter grouping."""

from __future__ import annotations

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType

from aiohomematic_config import ParameterGroup, ParameterGrouper


def _simple_param() -> ParameterData:
    """Create a minimal ParameterData for grouping tests."""
    return ParameterData(
        TYPE=ParameterType.FLOAT,
        MIN=0.0,
        MAX=100.0,
        DEFAULT=0.0,
        OPERATIONS=Operations.READ | Operations.WRITE,
        FLAGS=Flag.VISIBLE,
    )


class TestParameterGrouper:
    """Test ParameterGrouper."""

    def test_all_group_categories(self) -> None:
        """Test that all curated group categories can match."""
        grouper = ParameterGrouper()
        descriptions = {
            "TEMPERATURE_OFFSET": _simple_param(),
            "BOOST_POSITION": _simple_param(),
            "SHOW_WEEKDAY": _simple_param(),
            "TRANSMIT_TRY_MAX": _simple_param(),
            "POWERUP_ONTIME": _simple_param(),
            "BUTTON_RESPONSE": _simple_param(),
            "STATUSINFO_MINDELAY": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        group_ids = {g.id for g in result}
        assert "temperature" in group_ids
        assert "boost" in group_ids
        assert "display" in group_ids
        assert "transmission" in group_ids
        assert "powerup" in group_ids
        assert "button" in group_ids
        assert "status" in group_ids

    def test_boost_group(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "BOOST_POSITION": _simple_param(),
            "BOOST_MODE": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        assert len(result) == 1
        assert result[0].id == "boost"

    def test_button_group(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": _simple_param(),
            "LOCAL_RESET_DISABLED": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        assert len(result) == 1
        assert result[0].id == "button"

    def test_display_group(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "SHOW_WEEKDAY": _simple_param(),
            "LED_SLEEP_MODE": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        assert len(result) == 1
        assert result[0].id == "display"

    def test_empty_input(self) -> None:
        grouper = ParameterGrouper()
        result = grouper.group(descriptions={})
        assert result == ()

    def test_mixed_grouped_and_ungrouped(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "TEMPERATURE_OFFSET": _simple_param(),
            "UNKNOWN_PARAM": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        group_ids = {g.id for g in result}
        assert "temperature" in group_ids
        assert "other" in group_ids

    def test_multiple_groups(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "TEMPERATURE_OFFSET": _simple_param(),
            "BOOST_POSITION": _simple_param(),
            "POWERUP_ONTIME": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        group_ids = {g.id for g in result}
        assert "temperature" in group_ids
        assert "boost" in group_ids
        assert "powerup" in group_ids

    def test_parameter_group_frozen(self) -> None:
        pg = ParameterGroup(id="test", title="Test", parameters=("A", "B"))
        assert pg.id == "test"
        assert pg.title == "Test"
        assert pg.parameters == ("A", "B")

    def test_parameters_are_sorted(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "TEMPERATURE_Z": _simple_param(),
            "TEMPERATURE_A": _simple_param(),
            "TEMPERATURE_M": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        assert result[0].parameters == ("TEMPERATURE_A", "TEMPERATURE_M", "TEMPERATURE_Z")

    def test_reuse_grouper(self) -> None:
        """Grouper should be reusable without state leaking."""
        grouper = ParameterGrouper()
        desc1 = {"TEMPERATURE_OFFSET": _simple_param()}
        desc2 = {"BOOST_POSITION": _simple_param()}

        result1 = grouper.group(descriptions=desc1)
        result2 = grouper.group(descriptions=desc2)

        assert len(result1) == 1
        assert result1[0].id == "temperature"
        assert len(result2) == 1
        assert result2[0].id == "boost"

    def test_status_group(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "STATUSINFO_MINDELAY": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        assert len(result) == 1
        assert result[0].id == "status"

    def test_temperature_group(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "TEMPERATURE_OFFSET": _simple_param(),
            "TEMPERATURE_WINDOW_OPEN": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        assert len(result) == 1
        assert result[0].id == "temperature"
        assert result[0].title == "Temperature Settings"
        assert "TEMPERATURE_OFFSET" in result[0].parameters
        assert "TEMPERATURE_WINDOW_OPEN" in result[0].parameters

    def test_transmission_group(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "TRANSMIT_TRY_MAX": _simple_param(),
            "COND_TX_THRESHOLD_HI": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        group_ids = {g.id for g in result}
        assert "transmission" in group_ids

    def test_ungrouped_fallback(self) -> None:
        grouper = ParameterGrouper()
        descriptions = {
            "SOME_RANDOM_PARAM": _simple_param(),
            "ANOTHER_UNKNOWN": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        assert len(result) == 1
        assert result[0].id == "other"
        assert result[0].title == "Other Settings"
