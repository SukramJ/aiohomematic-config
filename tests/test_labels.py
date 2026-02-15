"""Tests for label resolution."""

from __future__ import annotations

from aiohomematic_config import LabelResolver


class TestLabelResolver:
    """Test LabelResolver."""

    def test_channel_type_empty_string(self) -> None:
        resolver = LabelResolver(locale="en")
        # Empty string should behave like no channel_type
        result = resolver.resolve(parameter_id="TEMPERATURE_OFFSET", channel_type="")
        assert result == "Temperature Offset"

    def test_channel_type_parameter(self) -> None:
        resolver = LabelResolver(locale="en")
        result = resolver.resolve(
            parameter_id="TEMPERATURE_OFFSET",
            channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
        )
        assert result == "Temperature Offset"

    def test_default_locale_is_en(self) -> None:
        resolver = LabelResolver()
        assert resolver.locale == "en"

    def test_fallback_humanization(self) -> None:
        resolver = LabelResolver(locale="en")
        result = resolver.resolve(parameter_id="SOME_UNKNOWN_PARAMETER")
        assert result == "Some Unknown Parameter"

    def test_fallback_single_word(self) -> None:
        resolver = LabelResolver(locale="en")
        # BRIGHTNESS has an upstream translation
        result = resolver.resolve(parameter_id="BRIGHTNESS")
        assert result == "Brightness"

    def test_has_translation_false(self) -> None:
        resolver = LabelResolver(locale="en")
        assert resolver.has_translation(parameter_id="XYZZY_UNKNOWN_PARAM") is False

    def test_has_translation_true(self) -> None:
        resolver = LabelResolver(locale="en")
        assert resolver.has_translation(parameter_id="TEMPERATURE_OFFSET") is True

    def test_known_translation_de(self) -> None:
        resolver = LabelResolver(locale="de")
        assert resolver.resolve(parameter_id="TEMPERATURE_OFFSET") == "Temperaturverschiebung"

    def test_known_translation_en(self) -> None:
        resolver = LabelResolver(locale="en")
        assert resolver.resolve(parameter_id="TEMPERATURE_OFFSET") == "Temperature Offset"

    def test_locale_property(self) -> None:
        resolver = LabelResolver(locale="de")
        assert resolver.locale == "de"

    def test_missing_locale_falls_back_to_en(self) -> None:
        # Upstream normalizes unsupported locales to "en"
        resolver = LabelResolver(locale="fr")
        result = resolver.resolve(parameter_id="TEMPERATURE_OFFSET")
        assert result == "Temperature Offset"

    def test_unknown_parameter_humanized(self) -> None:
        resolver = LabelResolver(locale="de")
        # No upstream translation -> falls back to humanization
        assert resolver.resolve(parameter_id="XYZZY_UNKNOWN_PARAM") == "Xyzzy Unknown Param"

    def test_upstream_translation_de(self) -> None:
        resolver = LabelResolver(locale="de")
        assert resolver.resolve(parameter_id="FROST_PROTECTION") == "Frostschutz"

    def test_upstream_translation_en(self) -> None:
        resolver = LabelResolver(locale="en")
        assert resolver.resolve(parameter_id="FROST_PROTECTION") == "Frost Protection"
