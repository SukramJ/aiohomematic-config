"""Tests for form schema generator."""

from typing import Any
from unittest.mock import patch

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType
from aiohomematic.easymode_data import (
    ChannelMetadata,
    OptionPresetDef,
    OptionPresetEntry,
    SenderTypeMetadata,
    SubsetDef,
)

from aiohomematic_config import FormParameter, FormSchema, FormSchemaGenerator, FormSection, WidgetType


class TestFormSchemaGenerator:
    """Test FormSchemaGenerator."""

    def test_channel_type_label(self) -> None:
        """channel_type_label should be resolved from upstream translations."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="SWITCH_VIRTUAL_RECEIVER",
        )
        assert schema.channel_type_label == "Switch actuator"

    def test_channel_type_label_de(self) -> None:
        """channel_type_label should use the correct locale."""
        generator = FormSchemaGenerator(locale="de")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="SWITCH_VIRTUAL_RECEIVER",
        )
        assert schema.channel_type_label == "Schaltaktor"

    def test_channel_type_label_empty(self) -> None:
        """channel_type_label should be empty when no channel_type is given."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
        )
        assert schema.channel_type_label == ""

    def test_channel_type_label_fallback(self) -> None:
        """channel_type_label should fall back to channel_type if no translation."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="NONEXISTENT_CHANNEL_TYPE",
        )
        assert schema.channel_type_label == "NONEXISTENT_CHANNEL_TYPE"

    def test_description_locale_de(
        self,
        permissive_generator_de: FormSchemaGenerator,
    ) -> None:
        """Description should use the correct locale."""
        descriptions: dict[str, ParameterData] = {
            "TEMPERATURE_OFFSET": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=-3.5,
                MAX=3.5,
                DEFAULT=0.0,
                UNIT="°C",
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema_de = permissive_generator_de.generate(
            descriptions=descriptions,
            current_values={"TEMPERATURE_OFFSET": 0.0},
        )
        param_de = schema_de.sections[0].parameters[0]
        assert param_de.description is not None

    def test_description_none_for_unknown_parameter(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Description should be None when no help text exists."""
        descriptions: dict[str, ParameterData] = {
            "FAKE_UNKNOWN_PARAM_Z": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=1.0,
                DEFAULT=0.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"FAKE_UNKNOWN_PARAM_Z": 0.0},
            require_translation=False,
        )
        param = schema.sections[0].parameters[0]
        assert param.description is None

    def test_description_populated_for_known_parameter(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Description should contain Markdown help text for known parameters."""
        descriptions: dict[str, ParameterData] = {
            "TEMPERATURE_OFFSET": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=-3.5,
                MAX=3.5,
                DEFAULT=0.0,
                UNIT="°C",
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"TEMPERATURE_OFFSET": 0.0},
        )
        param = schema.sections[0].parameters[0]
        assert param.description is not None
        assert len(param.description) > 0

    def test_device_icon(self) -> None:
        """device_icon should be resolved for known models."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            model="HmIP-SWDO",
        )
        assert schema.device_icon is not None
        assert schema.device_icon.endswith(".png")

    def test_device_icon_empty(self) -> None:
        """device_icon should be None when no model is given."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
        )
        assert schema.device_icon is None

    def test_device_icon_unknown_model(self) -> None:
        """device_icon should be None for unknown models."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            model="NONEXISTENT-MODEL",
        )
        assert schema.device_icon is None

    def test_empty_descriptions(self) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
        )
        assert schema.total_parameters == 0
        assert schema.writable_parameters == 0
        assert schema.sections == []

    def test_enum_options_included(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        descriptions: dict[str, ParameterData] = {
            "CHANNEL_OPERATION_MODE": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=2,
                DEFAULT="OFF",
                VALUE_LIST=["OFF", "MANUAL", "AUTO"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"CHANNEL_OPERATION_MODE": "OFF"},
        )
        param = schema.sections[0].parameters[0]
        assert param.options == ["OFF", "MANUAL", "AUTO"]

    def test_generate_thermostat_schema(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=thermostat_values,
            channel_address="0001D3C99C36D0:1",
            channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
        )
        assert isinstance(schema, FormSchema)
        assert schema.channel_address == "0001D3C99C36D0:1"
        assert schema.total_parameters > 0
        assert schema.writable_parameters > 0

    def test_invisible_parameters_excluded(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Parameters without VISIBLE flag should be excluded."""
        descriptions: dict[str, ParameterData] = {
            "TEMPERATURE_OFFSET": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=10.0,
                DEFAULT=5.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
            "INVISIBLE_PARAM": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=10.0,
                DEFAULT=5.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=0,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"TEMPERATURE_OFFSET": 5.0, "INVISIBLE_PARAM": 5.0},
        )
        all_param_ids = [p.id for s in schema.sections for p in s.parameters]
        assert "TEMPERATURE_OFFSET" in all_param_ids
        assert "INVISIBLE_PARAM" not in all_param_ids

    def test_model_description(self) -> None:
        """model_description should be resolved from upstream translations."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            model="HmIP-SWDO",
        )
        assert schema.model_description == "Homematic IP Window / Door Contact - optical"

    def test_model_description_de(self) -> None:
        """model_description should use the correct locale."""
        generator = FormSchemaGenerator(locale="de")
        schema = generator.generate(
            descriptions={},
            current_values={},
            model="HmIP-SWDO",
        )
        assert "Fenster" in schema.model_description

    def test_model_description_empty(self) -> None:
        """model_description should be empty when no model is given."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
        )
        assert schema.model_description == ""

    def test_model_description_fallback(self) -> None:
        """model_description should be empty when no translation is available."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            model="NONEXISTENT-MODEL",
        )
        assert schema.model_description == ""

    def test_modified_detection(
        self,
        thermostat_descriptions: dict[str, ParameterData],
    ) -> None:
        """Modified flag should be True when current != default."""
        generator = FormSchemaGenerator(locale="en")
        values = {
            "TEMPERATURE_OFFSET": 2.0,  # default is 0.0
            "TRANSMIT_TRY_MAX": 6,  # default is 6 (not modified)
            "CHANNEL_OPERATION_MODE": "NORMAL_MODE",
            "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": False,
            "LOCAL_RESET_DISABLED": False,
            "BRIGHTNESS_FILTER": 2.0,
        }
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=values,
        )
        all_params = [p for s in schema.sections for p in s.parameters]
        temp_offset = next(p for p in all_params if p.id == "TEMPERATURE_OFFSET")
        transmit_try = next(p for p in all_params if p.id == "TRANSMIT_TRY_MAX")
        assert temp_offset.modified is True
        assert transmit_try.modified is False

    def test_option_labels_de(
        self,
        permissive_generator_de: FormSchemaGenerator,
    ) -> None:
        """option_labels should use the correct locale."""
        descriptions: dict[str, ParameterData] = {
            "COLOR": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=1,
                DEFAULT="BLUE",
                VALUE_LIST=["BLUE", "RED"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_de.generate(
            descriptions=descriptions,
            current_values={"COLOR": "BLUE"},
        )
        param = schema.sections[0].parameters[0]
        assert param.option_labels is not None
        assert param.option_labels["BLUE"] == "Blau"
        assert param.option_labels["RED"] == "Rot"

    def test_option_labels_humanized_when_no_translations(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """option_labels should fall back to humanized values when no translations exist."""
        descriptions: dict[str, ParameterData] = {
            "XYZZY_FAKE_PARAM": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=2,
                DEFAULT="XYZZY_OPTION",
                VALUE_LIST=["XYZZY_OPTION", "QWERTY_OPTION", "ASDFG_OPTION"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"XYZZY_FAKE_PARAM": "XYZZY_OPTION"},
        )
        param = schema.sections[0].parameters[0]
        assert param.option_labels is not None
        assert param.option_labels["XYZZY_OPTION"] == "Xyzzy Option"
        assert param.option_labels["QWERTY_OPTION"] == "Qwerty Option"
        assert param.option_labels["ASDFG_OPTION"] == "Asdfg Option"

    def test_option_labels_populated(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """option_labels should map VALUE_LIST entries to upstream translations."""
        descriptions: dict[str, ParameterData] = {
            "COLOR": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=2,
                DEFAULT="BLUE",
                VALUE_LIST=["BLUE", "GREEN", "RED"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"COLOR": "BLUE"},
        )
        param = schema.sections[0].parameters[0]
        assert param.options == ["BLUE", "GREEN", "RED"]
        assert param.option_labels is not None
        assert param.option_labels["BLUE"] == "Blue"
        assert param.option_labels["GREEN"] == "Green"
        assert param.option_labels["RED"] == "Red"

    def test_parameters_have_labels(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=thermostat_values,
        )
        for section in schema.sections:
            for param in section.parameters:
                assert isinstance(param, FormParameter)
                assert len(param.label) > 0
                assert param.id

    def test_read_only_parameter(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Non-writable parameters should get READ_ONLY widget."""
        descriptions: dict[str, ParameterData] = {
            "ACTUAL_TEMPERATURE": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=100.0,
                DEFAULT=50.0,
                OPERATIONS=Operations.READ,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"ACTUAL_TEMPERATURE": 50.0},
        )
        param = schema.sections[0].parameters[0]
        assert param.widget == WidgetType.READ_ONLY
        assert param.writable is False

    def test_require_translation_false_includes_untranslated_params(self) -> None:
        """Parameters without CCU translations should be included when require_translation=False."""
        generator = FormSchemaGenerator(locale="en")
        descriptions: dict[str, ParameterData] = {
            "FAKE_UNKNOWN_PARAM_A": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=111600.0,
                DEFAULT=0.0,
                UNIT="s",
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
            "FAKE_UNKNOWN_PARAM_B": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=1.0,
                DEFAULT=1.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        # With require_translation=True (default), untranslated params are excluded
        schema_strict = generator.generate(
            descriptions=descriptions,
            current_values={"FAKE_UNKNOWN_PARAM_A": 0.0, "FAKE_UNKNOWN_PARAM_B": 1.0},
            require_translation=True,
        )
        assert schema_strict.total_parameters == 0

        # With require_translation=False, untranslated params are included
        schema_permissive = generator.generate(
            descriptions=descriptions,
            current_values={"FAKE_UNKNOWN_PARAM_A": 0.0, "FAKE_UNKNOWN_PARAM_B": 1.0},
            require_translation=False,
        )
        assert schema_permissive.total_parameters == 2
        all_param_ids = [p.id for s in schema_permissive.sections for p in s.parameters]
        assert "FAKE_UNKNOWN_PARAM_A" in all_param_ids
        assert "FAKE_UNKNOWN_PARAM_B" in all_param_ids

    def test_require_translation_false_uses_humanized_labels(self) -> None:
        """Parameters without translations should get humanized labels as fallback."""
        generator = FormSchemaGenerator(locale="en")
        descriptions: dict[str, ParameterData] = {
            "FAKE_UNKNOWN_PARAM_X": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=1.0,
                DEFAULT=0.05,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = generator.generate(
            descriptions=descriptions,
            current_values={"FAKE_UNKNOWN_PARAM_X": 0.05},
            require_translation=False,
        )
        param = schema.sections[0].parameters[0]
        assert param.label == "Fake Unknown Param X"

    def test_schedule_parameters_excluded(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Schedule parameters (XX_WP_* and WEEK_PROGRAM_*) should be excluded."""
        descriptions: dict[str, ParameterData] = {
            "TEMPERATURE_OFFSET": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=-3.5,
                MAX=3.5,
                DEFAULT=0.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
            "1_WP_ENDTIME_1": ParameterData(
                TYPE=ParameterType.INTEGER,
                MIN=0,
                MAX=1440,
                DEFAULT=360,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
            "WEEK_PROGRAM_POINTER": ParameterData(
                TYPE=ParameterType.INTEGER,
                MIN=0,
                MAX=5,
                DEFAULT=0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"TEMPERATURE_OFFSET": 0.0, "1_WP_ENDTIME_1": 360, "WEEK_PROGRAM_POINTER": 0},
        )
        all_param_ids = [p.id for s in schema.sections for p in s.parameters]
        assert "TEMPERATURE_OFFSET" in all_param_ids
        assert "1_WP_ENDTIME_1" not in all_param_ids
        assert "WEEK_PROGRAM_POINTER" not in all_param_ids

    def test_sections_are_populated(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=thermostat_values,
        )
        assert len(schema.sections) > 0
        for section in schema.sections:
            assert isinstance(section, FormSection)
            assert len(section.parameters) > 0

    def test_switch_descriptions(
        self,
        switch_descriptions: dict[str, ParameterData],
        switch_values: dict[str, Any],
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        schema = permissive_generator_en.generate(
            descriptions=switch_descriptions,
            current_values=switch_values,
        )
        assert schema.total_parameters == 3


class TestIsHmipChannelTypeResolution:
    """Test that is_hmip resolves channel types for HmIP-specific translations."""

    def test_hmip_channel_type_label_resolved(self) -> None:
        """Test that the channel type label uses the HmIP-specific translation."""
        generator = FormSchemaGenerator(locale="de")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="SHUTTER_CONTACT",
            is_hmip=True,
        )
        # SHUTTER_CONTACT_HMIP should have its own channel type label
        assert schema.channel_type_label != ""

    def test_hmip_parameter_labels_use_resolved_type(self) -> None:
        """Test that parameter labels use the resolved HmIP channel type."""
        msg_for_pos_a: ParameterData = {
            "TYPE": ParameterType.ENUM,
            "FLAGS": Flag.VISIBLE | Flag.SERVICE,
            "OPERATIONS": Operations.READ | Operations.WRITE,
            "DEFAULT": "NO_MSG",
            "VALUE_LIST": ["NO_MSG", "OPEN_MSG"],
            "MIN": "NO_MSG",
            "MAX": "OPEN_MSG",
        }
        generator = FormSchemaGenerator(locale="de")
        schema = generator.generate(
            descriptions={"MSG_FOR_POS_A": msg_for_pos_a},
            current_values={"MSG_FOR_POS_A": "NO_MSG"},
            channel_type="SHUTTER_CONTACT",
            is_hmip=True,
        )
        # Should have a section with MSG_FOR_POS_A using HmIP translation
        assert schema.total_parameters == 1
        param = schema.sections[0].parameters[0]
        assert param.id == "MSG_FOR_POS_A"
        # The label should be the HmIP variant ("offen" not "geschlossen")
        assert "offen" in param.label.lower()

    def test_hmip_resolves_channel_type(self) -> None:
        """Test that is_hmip=True resolves SHUTTER_CONTACT to SHUTTER_CONTACT_HMIP."""
        generator = FormSchemaGenerator(locale="de")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="SHUTTER_CONTACT",
            is_hmip=True,
        )
        # The resolved channel type should be stored in the schema
        assert schema.channel_type == "SHUTTER_CONTACT_HMIP"

    def test_non_hmip_keeps_channel_type(self) -> None:
        """Test that is_hmip=False keeps the original channel type."""
        generator = FormSchemaGenerator(locale="de")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="SHUTTER_CONTACT",
            is_hmip=False,
        )
        assert schema.channel_type == "SHUTTER_CONTACT"


def _make_writable_float(
    *,
    min_val: float = 0.0,
    max_val: float = 1.0,
    default: float = 0.0,
) -> ParameterData:
    return ParameterData(
        TYPE=ParameterType.FLOAT,
        MIN=min_val,
        MAX=max_val,
        DEFAULT=default,
        OPERATIONS=Operations.READ | Operations.WRITE,
        FLAGS=Flag.VISIBLE,
    )


class TestEasymodeEnrichment:
    """Test easymode metadata enrichment (presets, subsets, visibility)."""

    def test_option_presets_enriched(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Option presets should be attached to parameters when easymode metadata specifies them."""
        descriptions: dict[str, ParameterData] = {
            "LEVEL": _make_writable_float(),
        }
        preset_def = OptionPresetDef(
            presets=(
                OptionPresetEntry(value=0.0, label="Off"),
                OptionPresetEntry(value=1.0, label="Full"),
            ),
            allow_custom=True,
        )
        st_meta = SenderTypeMetadata(option_presets={"LEVEL": "TEST_PRESET"})
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with (
            patch("aiohomematic_config.form_schema.get_channel_metadata", return_value=ch_meta),
            patch("aiohomematic_config.form_schema.get_option_preset", return_value=preset_def),
        ):
            schema = permissive_generator_en.generate(
                descriptions=descriptions,
                current_values={"LEVEL": 0.5},
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        param = schema.sections[0].parameters[0]
        assert param.presets is not None
        assert len(param.presets) == 2
        assert param.presets[0]["value"] == 0.0
        assert param.presets[0]["label"] == "Off"
        assert param.allow_custom_value is True

    def test_subset_groups_built(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Subset groups should be built from easymode metadata."""
        descriptions: dict[str, ParameterData] = {
            "PARAM_A": _make_writable_float(),
            "PARAM_B": _make_writable_float(),
        }
        subset1 = SubsetDef(
            id=1,
            name_key="Option 1",
            member_params=("PARAM_A", "PARAM_B"),
            values={"PARAM_A": 0.0, "PARAM_B": 0.0},
        )
        subset2 = SubsetDef(
            id=2,
            name_key="Option 2",
            member_params=("PARAM_A", "PARAM_B"),
            values={"PARAM_A": 1.0, "PARAM_B": 1.0},
        )
        st_meta = SenderTypeMetadata(subsets=(subset1, subset2))
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.form_schema.get_channel_metadata", return_value=ch_meta):
            schema = permissive_generator_en.generate(
                descriptions=descriptions,
                current_values={"PARAM_A": 1.0, "PARAM_B": 1.0},
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert schema.subset_groups is not None
        assert len(schema.subset_groups) == 1
        group = schema.subset_groups[0]
        assert set(group.member_params) == {"PARAM_A", "PARAM_B"}
        assert len(group.options) == 2
        # Current values match subset2
        assert group.current_option_id == 2

    def test_subset_membership_on_param(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Parameters in a subset should have subset_group_id set."""
        descriptions: dict[str, ParameterData] = {
            "PARAM_A": _make_writable_float(),
        }
        subset = SubsetDef(
            id=1,
            name_key="Sub",
            member_params=("PARAM_A",),
            values={"PARAM_A": 0.0},
        )
        st_meta = SenderTypeMetadata(subsets=(subset,))
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.form_schema.get_channel_metadata", return_value=ch_meta):
            schema = permissive_generator_en.generate(
                descriptions=descriptions,
                current_values={"PARAM_A": 0.5},
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        param = schema.sections[0].parameters[0]
        assert param.subset_group_id is not None

    def test_subset_no_current_match(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """current_option_id should be None when no subset values match."""
        descriptions: dict[str, ParameterData] = {
            "PARAM_A": _make_writable_float(),
        }
        subset = SubsetDef(
            id=1,
            name_key="Sub",
            member_params=("PARAM_A",),
            values={"PARAM_A": 0.0},
        )
        st_meta = SenderTypeMetadata(subsets=(subset,))
        ch_meta = ChannelMetadata(
            channel_type="TEST_CH",
            sender_types={"SENDER": st_meta},
        )
        with patch("aiohomematic_config.form_schema.get_channel_metadata", return_value=ch_meta):
            schema = permissive_generator_en.generate(
                descriptions=descriptions,
                current_values={"PARAM_A": 0.5},
                channel_type="TEST_CH",
                sender_type="SENDER",
            )

        assert schema.subset_groups is not None
        assert schema.subset_groups[0].current_option_id is None
