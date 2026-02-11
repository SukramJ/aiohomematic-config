"""
Human-readable label resolution for parameter IDs.

Maps technical Homematic parameter identifiers to user-friendly labels
with i18n support. Falls back to automatic formatting when no translation
is available.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

import inspect
import json
import logging
from pathlib import Path
from typing import Final

from aiohomematic_config.const import DEFAULT_LOCALE

_LOGGER: Final = logging.getLogger(__name__)

_TRANSLATIONS_DIR: Final = Path(__file__).parent / "translations"


class LabelResolver:
    """
    Resolve parameter IDs to human-readable labels.

    Loads translations from JSON files in the translations directory.
    Falls back to automatic formatting (split by underscore, title case)
    when no translation is found.
    """

    __slots__ = ("_labels", "_locale")

    def __init__(self, *, locale: str = DEFAULT_LOCALE) -> None:
        """Initialize the label resolver."""
        self._locale: Final = locale
        self._labels: Final[dict[str, str]] = self._load_translations(locale=locale)

    @staticmethod
    def _load_translations(*, locale: str) -> dict[str, str]:
        """Load translation file for the given locale."""
        translation_file = _TRANSLATIONS_DIR / f"{locale}.json"
        if not translation_file.exists():
            _LOGGER.warning("Translation file not found for locale '%s'", locale)  # i18n-log: ignore
            return {}
        with translation_file.open(encoding="utf-8") as f:
            data: dict[str, str] = json.load(f)
        return data

    @property
    def locale(self) -> str:
        """Return the current locale."""
        return self._locale

    def resolve(self, *, parameter_id: str) -> str:
        """
        Resolve a parameter ID to a human-readable label.

        Returns the translated label if available, otherwise applies
        automatic formatting: split by underscores, title case each word.
        """
        if (label := self._labels.get(parameter_id)) is not None:
            return label
        return _humanize_parameter_id(parameter_id=parameter_id)


def _humanize_parameter_id(*, parameter_id: str) -> str:
    """
    Convert a technical parameter ID to a human-readable label.

    Example: ``TEMPERATURE_OFFSET`` -> ``Temperature Offset``
    """
    return parameter_id.replace("_", " ").title()


__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
