"""
Parameter grouping for configuration forms.

Groups a flat list of parameters into logical sections using
prefix-based heuristics and curated category mappings.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import inspect
import re
from typing import Final

from aiohomematic.const import ParameterData


@dataclass(frozen=True)
class ParameterGroup:
    """A logical group of parameters."""

    id: str
    title: str
    parameters: tuple[str, ...]


# Curated group definitions: (group_id, title, regex patterns)
_GROUP_DEFINITIONS: Final[tuple[tuple[str, str, tuple[str, ...]], ...]] = (
    (
        "temperature",
        "Temperature Settings",
        (r"TEMPERATURE_.*", r".*_TEMP_.*", r"FROST_.*", r"COMFORT_.*", r"ECO_.*"),
    ),
    (
        "timing",
        "Timing & Duration",
        (r".*_TIME_.*", r".*_DURATION_.*", r".*_DELAY_.*", r".*_INTERVAL_.*", r".*_TIMEOUT_.*"),
    ),
    (
        "display",
        "Display Settings",
        (r"SHOW_.*", r"DISPLAY_.*", r"BACKLIGHT_.*", r"LED_.*"),
    ),
    (
        "transmission",
        "Transmission & Communication",
        (r"TRANSMIT_.*", r"TX_.*", r"SIGNAL_.*", r"DUTYCYCLE_.*", r"COND_TX_.*"),
    ),
    (
        "powerup",
        "Power-Up Behavior",
        (r"POWERUP_.*",),
    ),
    (
        "boost",
        "Boost Settings",
        (r"BOOST_.*",),
    ),
    (
        "button",
        "Button Behavior",
        (r"BUTTON_.*", r"LOCAL_.*"),
    ),
    (
        "threshold",
        "Thresholds & Conditions",
        (r".*_THRESHOLD_.*", r".*_DECISION_.*", r".*_FILTER.*"),
    ),
    (
        "status",
        "Status & Reporting",
        (r"STATUSINFO_.*", r"STATUS_.*"),
    ),
)


@dataclass
class _GroupCollector:
    """Mutable collector for building parameter groups."""

    id: str
    title: str
    patterns: tuple[re.Pattern[str], ...]
    parameters: list[str] = field(default_factory=list)


class ParameterGrouper:
    """
    Group parameters into logical sections.

    Applies pattern-based heuristics to organize flat parameter lists.
    """

    __slots__ = ("_collectors",)

    def __init__(self) -> None:
        """Initialize the parameter grouper."""
        self._collectors: tuple[_GroupCollector, ...] = tuple(
            _GroupCollector(
                id=gid,
                title=title,
                patterns=tuple(re.compile(p) for p in patterns),
            )
            for gid, title, patterns in _GROUP_DEFINITIONS
        )

    def group(
        self,
        *,
        descriptions: Mapping[str, ParameterData],
        channel_type: str = "",
    ) -> tuple[ParameterGroup, ...]:
        """
        Group parameters into logical sections.

        Args:
            descriptions: Parameter descriptions to group.
            channel_type: Optional channel type for context-aware grouping.

        Returns:
            Tuple of ParameterGroup instances.

        """
        # Reset collectors
        for collector in self._collectors:
            collector.parameters.clear()

        ungrouped: list[str] = []

        for param_id in sorted(descriptions.keys()):
            matched = False
            for collector in self._collectors:
                if any(pattern.fullmatch(param_id) for pattern in collector.patterns):
                    collector.parameters.append(param_id)
                    matched = True
                    break
            if not matched:
                ungrouped.append(param_id)

        groups: list[ParameterGroup] = [
            ParameterGroup(
                id=collector.id,
                title=collector.title,
                parameters=tuple(collector.parameters),
            )
            for collector in self._collectors
            if collector.parameters
        ]

        if ungrouped:
            groups.append(
                ParameterGroup(
                    id="other",
                    title="Other Settings",
                    parameters=tuple(ungrouped),
                )
            )

        return tuple(groups)


__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
