"""Tests for link parameter metadata classification."""

from __future__ import annotations

from aiohomematic_config import (
    KeypressGroup,
    LinkParamCategory,
    TimeSelectorType,
    classify_link_parameter,
    decode_time_value,
    encode_time_value,
    get_time_presets,
)


class TestClassifyLinkParameter:
    """Tests for classify_link_parameter."""

    def test_action_type(self) -> None:
        """Test SHORT_PROFILE_ACTION_TYPE classification."""
        meta = classify_link_parameter(parameter_id="SHORT_PROFILE_ACTION_TYPE")
        assert meta.category == LinkParamCategory.ACTION
        assert meta.hidden_by_default is True
        assert meta.keypress_group == KeypressGroup.SHORT

    def test_common_param(self) -> None:
        """Test parameter without SHORT_/LONG_ prefix."""
        meta = classify_link_parameter(parameter_id="SOME_SETTING")
        assert meta.keypress_group == KeypressGroup.COMMON
        assert meta.category == LinkParamCategory.OTHER

    def test_common_time_param(self) -> None:
        """Test common time parameter without SHORT/LONG prefix."""
        meta = classify_link_parameter(parameter_id="ON_TIME_BASE")
        assert meta.category == LinkParamCategory.TIME
        assert meta.keypress_group == KeypressGroup.COMMON
        assert meta.time_pair_id == "ON_TIME"
        assert meta.time_selector_type == TimeSelectorType.TIME_ON_OFF

    def test_condition_transition(self) -> None:
        """Test SHORT_CT_ON classification."""
        meta = classify_link_parameter(parameter_id="SHORT_CT_ON")
        assert meta.category == LinkParamCategory.CONDITION
        assert meta.hidden_by_default is True
        assert meta.keypress_group == KeypressGroup.SHORT

    def test_dim_max_level(self) -> None:
        """Test LONG_DIM_MAX_LEVEL classification."""
        meta = classify_link_parameter(parameter_id="LONG_DIM_MAX_LEVEL")
        assert meta.category == LinkParamCategory.LEVEL
        assert meta.display_as_percent is True
        assert meta.keypress_group == KeypressGroup.LONG

    def test_dim_min_level(self) -> None:
        """Test SHORT_DIM_MIN_LEVEL classification."""
        meta = classify_link_parameter(parameter_id="SHORT_DIM_MIN_LEVEL")
        assert meta.category == LinkParamCategory.LEVEL
        assert meta.display_as_percent is True

    def test_jump_target(self) -> None:
        """Test SHORT_JT_ON classification."""
        meta = classify_link_parameter(parameter_id="SHORT_JT_ON")
        assert meta.category == LinkParamCategory.JUMP_TARGET
        assert meta.hidden_by_default is True
        assert meta.keypress_group == KeypressGroup.SHORT

    def test_level_param(self) -> None:
        """Test SHORT_ON_LEVEL classification."""
        meta = classify_link_parameter(parameter_id="SHORT_ON_LEVEL")
        assert meta.category == LinkParamCategory.LEVEL
        assert meta.display_as_percent is True
        assert meta.keypress_group == KeypressGroup.SHORT

    def test_long_jump_target(self) -> None:
        """Test LONG_JT_OFF classification."""
        meta = classify_link_parameter(parameter_id="LONG_JT_OFF")
        assert meta.category == LinkParamCategory.JUMP_TARGET
        assert meta.hidden_by_default is True
        assert meta.keypress_group == KeypressGroup.LONG

    def test_long_off_time_base(self) -> None:
        """Test LONG_OFF_TIME_BASE classification."""
        meta = classify_link_parameter(parameter_id="LONG_OFF_TIME_BASE")
        assert meta.category == LinkParamCategory.TIME
        assert meta.keypress_group == KeypressGroup.LONG
        assert meta.time_pair_id == "LONG_OFF_TIME"
        assert meta.time_selector_type == TimeSelectorType.TIME_ON_OFF

    def test_long_ondelay_time_factor(self) -> None:
        """Test LONG_ONDELAY_TIME_FACTOR classification."""
        meta = classify_link_parameter(parameter_id="LONG_ONDELAY_TIME_FACTOR")
        assert meta.category == LinkParamCategory.TIME
        assert meta.keypress_group == KeypressGroup.LONG
        assert meta.time_pair_id == "LONG_ONDELAY_TIME"
        assert meta.time_selector_type == TimeSelectorType.DELAY

    def test_multiexecute(self) -> None:
        """Test LONG_MULTIEXECUTE classification."""
        meta = classify_link_parameter(parameter_id="LONG_MULTIEXECUTE")
        assert meta.category == LinkParamCategory.ACTION
        assert meta.hidden_by_default is True
        assert meta.keypress_group == KeypressGroup.LONG

    def test_on_delay_time_variant(self) -> None:
        """Test ON_DELAY_TIME variant (underscore)."""
        meta = classify_link_parameter(parameter_id="SHORT_ON_DELAY_TIME_BASE")
        assert meta.category == LinkParamCategory.TIME
        assert meta.time_selector_type == TimeSelectorType.DELAY

    def test_rampoff_time_variant(self) -> None:
        """Test RAMPOFF_TIME variant (no underscore)."""
        meta = classify_link_parameter(parameter_id="SHORT_RAMPOFF_TIME_FACTOR")
        assert meta.category == LinkParamCategory.TIME
        assert meta.time_selector_type == TimeSelectorType.RAMP_ON_OFF

    def test_short_on_time_factor(self) -> None:
        """Test SHORT_ON_TIME_FACTOR classification."""
        meta = classify_link_parameter(parameter_id="SHORT_ON_TIME_FACTOR")
        assert meta.category == LinkParamCategory.TIME
        assert meta.keypress_group == KeypressGroup.SHORT
        assert meta.time_pair_id == "SHORT_ON_TIME"
        assert meta.time_selector_type == TimeSelectorType.TIME_ON_OFF

    def test_short_ramp_on_time_base(self) -> None:
        """Test SHORT_RAMP_ON_TIME_BASE classification."""
        meta = classify_link_parameter(parameter_id="SHORT_RAMP_ON_TIME_BASE")
        assert meta.category == LinkParamCategory.TIME
        assert meta.keypress_group == KeypressGroup.SHORT
        assert meta.time_selector_type == TimeSelectorType.RAMP_ON_OFF

    def test_short_time_base(self) -> None:
        """Test SHORT_ON_TIME_BASE classification."""
        meta = classify_link_parameter(parameter_id="SHORT_ON_TIME_BASE")
        assert meta.category == LinkParamCategory.TIME
        assert meta.keypress_group == KeypressGroup.SHORT
        assert meta.time_pair_id == "SHORT_ON_TIME"
        assert meta.time_selector_type == TimeSelectorType.TIME_ON_OFF


class TestTimePresets:
    """Tests for time preset functions."""

    def test_decode_time_value(self) -> None:
        """Test time value decoding."""
        assert decode_time_value(base=7, factor=1) == 3600.0
        assert decode_time_value(base=1, factor=5) == 5.0
        assert decode_time_value(base=0, factor=0) == 0.0

    def test_decode_time_value_100ms(self) -> None:
        """Test 100ms time base decoding."""
        assert decode_time_value(base=0, factor=1) == 0.1

    def test_decode_time_value_minutes(self) -> None:
        """Test minute time base decoding."""
        assert decode_time_value(base=4, factor=2) == 120.0

    def test_delay_presets_count(self) -> None:
        """Test delay presets count."""
        presets = get_time_presets(selector_type=TimeSelectorType.DELAY, locale="en")
        assert len(presets) == 10

    def test_encode_time_value(self) -> None:
        """Test encoding 1 hour."""
        base, factor = encode_time_value(seconds=3600.0, selector_type=TimeSelectorType.TIME_ON_OFF)
        assert base == 7
        assert factor == 1

    def test_encode_time_value_5s(self) -> None:
        """Test encoding 5 seconds."""
        base, factor = encode_time_value(seconds=5.0, selector_type=TimeSelectorType.DELAY)
        assert base == 2
        assert factor == 1

    def test_encode_time_value_closest_match(self) -> None:
        """Test encoding finds closest preset."""
        base, factor = encode_time_value(seconds=7.0, selector_type=TimeSelectorType.TIME_ON_OFF)
        # Closest is either 5s (base=2,factor=1) or 10s (base=3,factor=1)
        # 5s diff=2, 10s diff=3 -> 5s wins
        assert base == 2
        assert factor == 1

    def test_get_time_presets_de(self) -> None:
        """Test German delay presets."""
        presets = get_time_presets(selector_type=TimeSelectorType.DELAY, locale="de")
        assert presets[0]["label"] == "Nicht aktiv"

    def test_get_time_presets_en(self) -> None:
        """Test English time on/off presets."""
        presets = get_time_presets(selector_type=TimeSelectorType.TIME_ON_OFF, locale="en")
        assert len(presets) == 21
        assert presets[0]["label"] == "Not active"
        assert presets[-1]["label"] == "Permanent"

    def test_ramp_presets(self) -> None:
        """Test ramp on/off presets."""
        presets = get_time_presets(selector_type=TimeSelectorType.RAMP_ON_OFF, locale="en")
        assert len(presets) == 9
        assert presets[1]["label"] == "200 ms"
