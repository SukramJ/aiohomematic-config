"""Tests for label resolution."""

from __future__ import annotations

from aiohomematic_config import LabelResolver


class TestLabelResolver:
    """Test LabelResolver."""

    def test_default_locale_is_en(self) -> None:
        resolver = LabelResolver()
        assert resolver.locale == "en"

    def test_fallback_humanization(self) -> None:
        resolver = LabelResolver(locale="en")
        result = resolver.resolve(parameter_id="SOME_UNKNOWN_PARAMETER")
        assert result == "Some Unknown Parameter"

    def test_fallback_single_word(self) -> None:
        resolver = LabelResolver(locale="en")
        result = resolver.resolve(parameter_id="BRIGHTNESS")
        assert result == "Brightness"

    def test_known_translation_de(self) -> None:
        resolver = LabelResolver(locale="de")
        assert resolver.resolve(parameter_id="TEMPERATURE_OFFSET") == "Temperatur-Offset"

    def test_known_translation_en(self) -> None:
        resolver = LabelResolver(locale="en")
        assert resolver.resolve(parameter_id="TEMPERATURE_OFFSET") == "Temperature Offset"

    def test_locale_property(self) -> None:
        resolver = LabelResolver(locale="de")
        assert resolver.locale == "de"

    def test_missing_locale_falls_back(self) -> None:
        resolver = LabelResolver(locale="fr")
        # No French translation file, should fall back to humanization
        result = resolver.resolve(parameter_id="TEMPERATURE_OFFSET")
        assert result == "Temperature Offset"

    def test_multiple_known_translations_de(self) -> None:
        resolver = LabelResolver(locale="de")
        assert resolver.resolve(parameter_id="BOOST_TIME_PERIOD") == "Boost-Dauer"
        assert resolver.resolve(parameter_id="FROST_PROTECTION") == "Frostschutz"
        assert resolver.resolve(parameter_id="SHOW_WEEKDAY") == "Wochentag anzeigen"

    def test_multiple_known_translations_en(self) -> None:
        resolver = LabelResolver(locale="en")
        assert resolver.resolve(parameter_id="BOOST_TIME_PERIOD") == "Boost Duration"
        assert resolver.resolve(parameter_id="FROST_PROTECTION") == "Frost Protection"
        assert resolver.resolve(parameter_id="SHOW_WEEKDAY") == "Display Weekday"
