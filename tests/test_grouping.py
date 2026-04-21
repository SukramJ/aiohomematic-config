"""Tests for parameter grouping."""

from unittest.mock import patch

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType
from aiohomematic.easymode_data import ChannelMetadata, ParameterGroupDef, SenderTypeMetadata

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

    def test_locale_de_translates_titles(self) -> None:
        """Test that German locale produces translated section titles."""
        grouper = ParameterGrouper(locale="de")
        descriptions = {
            "TEMPERATURE_OFFSET": _simple_param(),
            "SOME_RANDOM_PARAM": _simple_param(),
        }
        result = grouper.group(descriptions=descriptions)
        titles = {g.id: g.title for g in result}
        assert titles["temperature"] == "Temperatur-Einstellungen"
        assert titles["other"] == "Sonstige Einstellungen"

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

    def test_unknown_locale_falls_back_to_english(self) -> None:
        """Test that unknown locale falls back to English titles."""
        grouper = ParameterGrouper(locale="fr")
        descriptions = {"TEMPERATURE_OFFSET": _simple_param()}
        result = grouper.group(descriptions=descriptions)
        assert result[0].title == "Temperature Settings"


class TestMetadataParameterGroups:
    """Test semantic parameter grouping from easymode metadata."""

    def test_fallback_to_single_group_without_parameter_groups(self) -> None:
        """Without parameter_groups, metadata should still produce a single ordered group."""
        grouper = ParameterGrouper(locale="en")
        descriptions = {
            "PARAM_B": _simple_param(),
            "PARAM_A": _simple_param(),
        }
        st_meta = SenderTypeMetadata(
            parameter_order=("PARAM_A", "PARAM_B"),
        )
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.grouping.get_channel_metadata", return_value=ch_meta):
            result = grouper.group(
                descriptions=descriptions,
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert len(result) == 1
        assert result[0].id == "all"
        assert result[0].parameters == ("PARAM_A", "PARAM_B")

    def test_group_without_label_key_or_label_falls_back_to_other_de(self) -> None:
        """Fallback label must respect the configured locale."""
        grouper = ParameterGrouper(locale="de")
        descriptions = {"PARAM_A": _simple_param()}
        group_defs = (
            ParameterGroupDef(
                id="group_5",
                label={},
                parameters=("PARAM_A",),
                label_key="",
            ),
        )
        st_meta = SenderTypeMetadata(
            parameter_order=("PARAM_A",),
            parameter_groups=group_defs,
        )
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.grouping.get_channel_metadata", return_value=ch_meta):
            result = grouper.group(
                descriptions=descriptions,
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert result[0].title == "Sonstige Einstellungen"

    def test_group_without_label_key_or_label_falls_back_to_other_en(self) -> None:
        """Raw group id must never leak to UI when both label_key and label are empty."""
        grouper = ParameterGrouper(locale="en")
        descriptions = {"PARAM_A": _simple_param()}
        group_defs = (
            ParameterGroupDef(
                id="group_5",
                label={},
                parameters=("PARAM_A",),
                label_key="",
            ),
        )
        st_meta = SenderTypeMetadata(
            parameter_order=("PARAM_A",),
            parameter_groups=group_defs,
        )
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.grouping.get_channel_metadata", return_value=ch_meta):
            result = grouper.group(
                descriptions=descriptions,
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert len(result) == 1
        assert result[0].id == "group_5"
        assert result[0].title == "Other Settings"
        assert result[0].title != "group_5"

    def test_groups_from_metadata(self) -> None:
        """parameter_groups from metadata should produce semantic groups."""
        grouper = ParameterGrouper(locale="en")
        descriptions = {
            "TEMP_MIN": _simple_param(),
            "TEMP_MAX": _simple_param(),
            "BRIGHTNESS": _simple_param(),
        }
        group_defs = (
            ParameterGroupDef(
                id="temp",
                label={"en": "Temperature", "de": "Temperatur-Einstellungen"},
                parameters=("TEMP_MIN", "TEMP_MAX"),
            ),
            ParameterGroupDef(
                id="light",
                label={"en": "Light", "de": "Licht"},
                parameters=("BRIGHTNESS",),
            ),
        )
        st_meta = SenderTypeMetadata(
            parameter_order=("TEMP_MIN", "TEMP_MAX", "BRIGHTNESS"),
            parameter_groups=group_defs,
        )
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.grouping.get_channel_metadata", return_value=ch_meta):
            result = grouper.group(
                descriptions=descriptions,
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert len(result) == 2
        assert result[0].id == "temp"
        assert result[0].title == "Temperature"
        assert result[0].parameters == ("TEMP_MIN", "TEMP_MAX")
        assert result[1].id == "light"
        assert result[1].title == "Light"
        assert result[1].parameters == ("BRIGHTNESS",)

    def test_groups_from_metadata_locale_de(self) -> None:
        """German locale should pick up de labels from metadata groups."""
        grouper = ParameterGrouper(locale="de")
        descriptions = {
            "PARAM_A": _simple_param(),
        }
        group_defs = (
            ParameterGroupDef(
                id="grp1",
                label={"en": "Group One", "de": "Gruppe Eins"},
                parameters=("PARAM_A",),
            ),
        )
        st_meta = SenderTypeMetadata(
            parameter_order=("PARAM_A",),
            parameter_groups=group_defs,
        )
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.grouping.get_channel_metadata", return_value=ch_meta):
            result = grouper.group(
                descriptions=descriptions,
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert result[0].title == "Gruppe Eins"

    def test_metadata_group_skips_missing_params(self) -> None:
        """Group definitions referencing missing parameters should skip them."""
        grouper = ParameterGrouper(locale="en")
        descriptions = {
            "PARAM_A": _simple_param(),
        }
        group_defs = (
            ParameterGroupDef(
                id="grp1",
                label={"en": "Group"},
                parameters=("PARAM_A", "PARAM_B_MISSING"),
            ),
        )
        st_meta = SenderTypeMetadata(
            parameter_order=("PARAM_A",),
            parameter_groups=group_defs,
        )
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.grouping.get_channel_metadata", return_value=ch_meta):
            result = grouper.group(
                descriptions=descriptions,
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert len(result) == 1
        assert result[0].parameters == ("PARAM_A",)

    def test_ungrouped_params_in_fallback(self) -> None:
        """Parameters not in any group should appear in 'other' fallback section."""
        grouper = ParameterGrouper(locale="en")
        descriptions = {
            "GROUPED": _simple_param(),
            "UNGROUPED": _simple_param(),
        }
        group_defs = (
            ParameterGroupDef(
                id="grp1",
                label={"en": "Group"},
                parameters=("GROUPED",),
            ),
        )
        st_meta = SenderTypeMetadata(
            parameter_order=("GROUPED", "UNGROUPED"),
            parameter_groups=group_defs,
        )
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.grouping.get_channel_metadata", return_value=ch_meta):
            result = grouper.group(
                descriptions=descriptions,
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert len(result) == 2
        assert result[0].id == "grp1"
        assert result[1].id == "other"
        assert "UNGROUPED" in result[1].parameters
