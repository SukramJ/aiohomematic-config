#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Parse OCCU easymode TCL files and generate JSON profile definitions.

Parse TCL easymode profile files from a local OCCU checkout or a running
OpenCCU/RaspberryMatic instance and output structured JSON profile files
for use by the ProfileStore.

Usage:
    # From a running OpenCCU instance (preferred)
    CCU_URL=https://my-ccu.local python script/parse_easymode_profiles.py

    # From local OCCU checkout
    OCCU_PATH=/path/to/occu python script/parse_easymode_profiles.py

    # Both set: running instance is preferred, local as fallback
    OCCU_PATH=/path/to/occu CCU_URL=https://my-ccu.local python script/parse_easymode_profiles.py

    # Only specific receiver types
    OCCU_PATH=/path/to/occu RECEIVERS=DIMMER_VIRTUAL_RECEIVER,SWITCH_VIRTUAL_RECEIVER python script/parse_easymode_profiles.py

Environment Variables:
    OCCU_PATH   Path to local OCCU checkout
    CCU_URL     URL of a running OpenCCU/RaspberryMatic instance (preferred)
    RECEIVERS   Comma-separated list of receiver channel types to parse (optional, default: all)
    OUTPUT_DIR  Output directory (default: aiohomematic_config/profiles)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import ssl
import sys
from typing import Any
import urllib.request

# Regex patterns for TCL parsing
_PROFILES_MAP_RE = re.compile(r'set\s+PROFILES_MAP\((\d+)\)\s+"?\\?\$\{(\w+)\}"?')
_PROFILE_PARAM_RE = re.compile(r"set\s+PROFILE_(\d+)\((\w+)\)\s+(.*)")
_RANGE_RE = re.compile(r"\{([\d.]+)\s+range\s+([\d.]+)\s+-\s+([\d.]+)\}")
_LIST_RE = re.compile(r"^\{([\d.\s]+)\}$")
_LOC_RE = re.compile(r'"(\w+)"\s*:\s*"((?:[^"\\]|\\.)*)"')
# Internal TCL keys to skip
_SKIP_KEYS = frozenset(
    {
        "UI_HINT",
        "UI_DESCRIPTION",
        "UI_TEMPLATE",
        "UI_WHITELIST",
        "UI_BLACKLIST",
    }
)

# Directories within easymodes/ that are NOT receiver types
_SKIP_DIRS = frozenset({"etc", "hmip", "js", "MASTER_LANG"})

# TCL helper files within receiver directories that are NOT sender types
_SKIP_TCL_FILES = frozenset(
    {
        "getColorElement",
        "getColorTempElement",
        "getSoundSelector",
        "profiles",
        "profilesTunableWhite",
        "profiles_shutter",
        "signal_type",
    }
)

# Supported locales
_LOCALES = ("de", "en")

# Easymode base path within WebUI
_EASYMODE_BASE = "config/easymodes"

# Default output directory (relative to project root)
_DEFAULT_OUTPUT_DIR = "aiohomematic_config/profiles"

# Comprehensive list of known receiver types for remote-only discovery
_KNOWN_RECEIVER_TYPES = (
    "ACCESS_RECEIVER",
    "ACOUSTIC_SIGNAL_VIRTUAL_RECEIVER",
    "ACTOR_SECURITY",
    "ACTOR_WINDOW",
    "ALARMACTUATOR",
    "ALARM_COND_SWITCH_RECEIVER",
    "ALARM_SWITCH_VIRTUAL_RECEIVER",
    "ARMING",
    "AUTO_RELOCK_TRANSCEIVER",
    "BLIND",
    "BLIND_VIRTUAL_RECEIVER",
    "CLIMATECONTROL_FLOOR_PUMP_TRANSCEIVER",
    "CLIMATECONTROL_FLOOR_TRANSCEIVER",
    "CLIMATECONTROL_INPUT_RECEIVER",
    "CLIMATECONTROL_RECEIVER",
    "CLIMATECONTROL_RT_RECEIVER",
    "CLIMATECONTROL_VENT_DRIVE",
    "DDC",
    "DIMMER",
    "DIMMER_VIRTUAL_RECEIVER",
    "DIMMER_woLongKeyPress",
    "DOOR_LOCK_TRANSCEIVER",
    "DOOR_RECEIVER",
    "DUAL_WHITE_BRIGHTNESS",
    "DUAL_WHITE_COLOR",
    "HEATING_CLIMATECONTROL_CL_RECEIVER",
    "HEATING_CLIMATECONTROL_RECEIVER",
    "HEATING_KEY_RECEIVER",
    "HEATING_ROOM_TH_RECEIVER",
    "HMW_BLIND",
    "HMW_DIMMER",
    "HMW_INPUT_OUTPUT",
    "HMW_SWITCH",
    "JALOUSIE",
    "KEYMATIC",
    "REMOTECONTROL_RECEIVER",
    "RGBW_AUTOMATIC",
    "RGBW_COLOR",
    "SERVO_VIRTUAL_RECEIVER",
    "SHUTTER_VIRTUAL_RECEIVER",
    "SIGNAL_CHIME",
    "SIGNAL_CHIMEM",
    "SIGNAL_LED",
    "SIGNAL_LEDM",
    "SIMPLE_SWITCH_RECEIVER",
    "STATE_RESET_RECEIVER",
    "STATUS_INDICATOR",
    "SWITCH",
    "SWITCH_PANIC",
    "SWITCH_SENSOR",
    "SWITCH_VIRTUAL_RECEIVER",
    "UNIVERSAL_ACTOR",
    "UNIVERSAL_LIGHT_RECEIVER_LSC",
    "UNIVERSAL_LIGHT_RECEIVER_PWM",
    "UNIVERSAL_LIGHT_RECEIVER_RGB(W)",
    "UNIVERSAL_LIGHT_RECEIVER_RGBW_DALI",
    "UNIVERSAL_LIGHT_RECEIVER_TW",
    "VIRTUAL_DIMMER",
    "VIRTUAL_DUAL_WHITE_COLOR",
    "WATER_SWITCH_VIRTUAL_RECEIVER",
    "WEATHER_RECEIVER",
    "WINDOW_DRIVE_RECEIVER",
    "WINDOW_SWITCH_RECEIVER",
    "WINMATIC",
    "WS_TH",
)

# Comprehensive list of known sender types for remote probing
_KNOWN_SENDER_TYPES = (
    "ACCELERATION_TRANSCEIVER",
    "ACCESS_TRANSCEIVER",
    "ALARMACTUATOR_TRANSCEIVER",
    "CLIMATECONTROL_FLOOR_TRANSCEIVER",
    "CLIMATECONTROL_REGULATOR",
    "COND_SWITCH_TRANSMITTER",
    "KEY",
    "KEY_TRANSCEIVER",
    "MOTION_DETECTOR_TRANSCEIVER",
    "MULTI_MODE_INPUT_TRANSMITTER",
    "PASSAGE_DETECTOR_DIRECTION_TRANSMITTER",
    "PRESENCEDETECTOR_TRANSCEIVER",
    "PUSH_BUTTON_TRANSCEIVER",
    "RAIN_DETECTION_TRANSMITTER",
    "REMOTE_CONTROL_TRANSCEIVER",
    "ROTARY_HANDLE_TRANSCEIVER",
    "SENSOR",
    "SHUTTER_CONTACT",
    "SHUTTER_CONTACT_TRANSCEIVER",
    "SMOKE_DETECTOR_TRANSCEIVER",
    "SWITCH",
    "SWITCH_TRANSCEIVER",
    "TILT_TRANSCEIVER",
    "WATER_DETECTION_TRANSMITTER",
    "WEATHER_TRANSMITTER",
    "WINMATIC",
)


# ---------------------------------------------------------------------------
# Remote file access
# ---------------------------------------------------------------------------


def _fetch_remote_file(ccu_url: str, relative_path: str) -> str:
    """Fetch a file from a remote CCU via HTTP."""
    url = f"{ccu_url.rstrip('/')}/{relative_path}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(url, context=ctx) as response:  # nosec B310
        raw: bytes = response.read()
        try:
            result: str = raw.decode("utf-8")
        except UnicodeDecodeError:
            result = raw.decode("iso-8859-1")
        return result


# ---------------------------------------------------------------------------
# TCL / Localization parsing
# ---------------------------------------------------------------------------


def _parse_constraint(raw_value: str) -> dict[str, Any] | None:
    """Parse a TCL constraint value into a JSON-serializable dict."""
    raw_value = raw_value.strip()

    # Range constraint: {default range min - max}
    m = _RANGE_RE.match(raw_value)
    if m:
        return {
            "constraint_type": "range",
            "default": float(m.group(1)),
            "min_value": float(m.group(2)),
            "max_value": float(m.group(3)),
        }

    # List constraint: {val1 val2 ...} (numbers only, no 'range')
    m = _LIST_RE.match(raw_value)
    if m:
        values = [float(v) for v in m.group(1).split()]
        if len(values) > 1:
            return {"constraint_type": "list", "values": values}
        if len(values) == 1:
            return {"constraint_type": "fixed", "value": values[0]}

    # Single numeric value
    try:
        val = float(raw_value)
    except ValueError:
        return None
    else:
        return {"constraint_type": "fixed", "value": val}


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HTML_ENTITIES = {
    "&quot;": '"',
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&nbsp;": " ",
    "&szlig;": "ß",
    "&auml;": "ä",
    "&ouml;": "ö",
    "&uuml;": "ü",
    "&Auml;": "Ä",
    "&Ouml;": "Ö",
    "&Uuml;": "Ü",
}


def _strip_html(text: str) -> str:
    """Strip HTML tags and decode common entities."""
    text = text.replace('\\"', '"')
    text = _HTML_TAG_RE.sub("", text)
    for entity, char in _HTML_ENTITIES.items():
        text = text.replace(entity, char)
    return text.strip()


def _parse_loc_content(content: str) -> dict[str, str]:
    """Parse localization text content and return key-value pairs."""
    result: dict[str, str] = {}
    for match in _LOC_RE.finditer(content):
        value = match.group(2)
        # Strip HTML from description values
        if value.startswith("<") or "\\" in value:
            value = _strip_html(value)
        result[match.group(1)] = value
    return result


def _parse_tcl_profiles(
    *,
    tcl_content: str,
    loc_en: dict[str, str],
    loc_de: dict[str, str],
) -> list[dict[str, Any]]:
    """Parse TCL content into profile definitions."""
    # Extract profile map (id -> localization key)
    profile_map: dict[int, str] = {}
    for match in _PROFILES_MAP_RE.finditer(tcl_content):
        profile_id = int(match.group(1))
        loc_key = match.group(2)
        profile_map[profile_id] = loc_key

    # Extract profile parameters
    profile_params: dict[int, dict[str, dict[str, Any]]] = {}
    for match in _PROFILE_PARAM_RE.finditer(tcl_content):
        profile_id = int(match.group(1))
        param_name = match.group(2)
        raw_value = match.group(3)

        if param_name in _SKIP_KEYS:
            continue

        constraint = _parse_constraint(raw_value)
        if constraint is not None:
            if profile_id not in profile_params:
                profile_params[profile_id] = {}
            profile_params[profile_id][param_name] = constraint

    # Build profile definitions
    profiles: list[dict[str, Any]] = []

    # Always add Expert profile (id=0) first
    profiles.append(
        {
            "id": 0,
            "name": {"en": "Expert", "de": "Experte"},
            "description": {"en": "", "de": ""},
        }
    )

    for profile_id in sorted(profile_map.keys()):
        if profile_id == 0:
            continue

        loc_key = profile_map[profile_id]
        name_en = loc_en.get(loc_key, f"Profile {profile_id}")
        name_de = loc_de.get(loc_key, name_en)

        desc_key = f"description_{profile_id}"
        desc_en = loc_en.get(desc_key, "")
        desc_de = loc_de.get(desc_key, desc_en)

        profile: dict[str, Any] = {
            "id": profile_id,
            "name": {"en": name_en, "de": name_de},
            "description": {"en": desc_en, "de": desc_de},
        }
        if profile_id in profile_params:
            profile["params"] = profile_params[profile_id]

        profiles.append(profile)

    return profiles


# ---------------------------------------------------------------------------
# Auto-discovery
# ---------------------------------------------------------------------------


def _discover_receiver_types_local(occu_path: Path) -> list[str]:
    """Discover all receiver type directories from a local OCCU checkout."""
    base = occu_path / "WebUI" / "www" / _EASYMODE_BASE
    if not base.exists():
        print(f"  WARNING: Easymodes directory not found: {base}", file=sys.stderr)
        return []

    receiver_types: list[str] = []
    for entry in sorted(base.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in _SKIP_DIRS:
            continue
        if any(entry.glob("*.tcl")):
            receiver_types.append(entry.name)

    return receiver_types


# ---------------------------------------------------------------------------
# Local OCCU source loading
# ---------------------------------------------------------------------------


def _load_localization_local(
    *,
    occu_base: Path,
    receiver_type: str,
    sender_type: str,
    locale: str,
) -> dict[str, str]:
    """Load and merge localization strings from local OCCU files."""
    strings: dict[str, str] = {}

    # 1. Generic strings
    generic_file = occu_base / "etc" / "localization" / locale / "GENERIC.txt"
    if generic_file.exists():
        strings.update(_parse_loc_content(generic_file.read_text(encoding="utf-8", errors="replace")))

    # 2. Receiver-specific generic strings
    receiver_generic = occu_base / receiver_type / "localization" / locale / "GENERIC.txt"
    if receiver_generic.exists():
        strings.update(_parse_loc_content(receiver_generic.read_text(encoding="utf-8", errors="replace")))

    # 3. Sender-specific strings
    sender_file = occu_base / receiver_type / "localization" / locale / f"{sender_type}.txt"
    if sender_file.exists():
        strings.update(_parse_loc_content(sender_file.read_text(encoding="utf-8", errors="replace")))

    return strings


def _parse_receiver_local(
    *,
    occu_path: Path,
    receiver_type: str,
) -> dict[str, Any]:
    """Parse all sender profiles for a receiver type from local OCCU."""
    result: dict[str, Any] = {}
    base = occu_path / "WebUI" / "www" / _EASYMODE_BASE
    receiver_dir = base / receiver_type

    if not receiver_dir.exists():
        print(f"  WARNING: Directory not found: {receiver_dir}", file=sys.stderr)
        return result

    for tcl_file in sorted(receiver_dir.glob("*.tcl")):
        sender_type = tcl_file.stem
        # Skip helper TCL files (e.g. getColorElement, profiles, signal_type)
        if sender_type in _SKIP_TCL_FILES:
            continue
        tcl_content = tcl_file.read_text(encoding="utf-8", errors="replace")

        loc_en = _load_localization_local(
            occu_base=base,
            receiver_type=receiver_type,
            sender_type=sender_type,
            locale="en",
        )
        loc_de = _load_localization_local(
            occu_base=base,
            receiver_type=receiver_type,
            sender_type=sender_type,
            locale="de",
        )

        profiles = _parse_tcl_profiles(
            tcl_content=tcl_content,
            loc_en=loc_en,
            loc_de=loc_de,
        )

        if profiles:
            result[sender_type] = {"profiles": profiles}
            print(f"  {sender_type}: {len(profiles)} profiles")

    return result


# ---------------------------------------------------------------------------
# Remote CCU source loading
# ---------------------------------------------------------------------------


def _load_localization_remote(
    *,
    ccu_url: str,
    receiver_type: str,
    sender_type: str,
    locale: str,
) -> dict[str, str]:
    """Load and merge localization strings from a remote CCU."""
    strings: dict[str, str] = {}
    base = _EASYMODE_BASE

    loc_files = [
        f"{base}/etc/localization/{locale}/GENERIC.txt",
        f"{base}/{receiver_type}/localization/{locale}/GENERIC.txt",
        f"{base}/{receiver_type}/localization/{locale}/{sender_type}.txt",
    ]

    for rel_path in loc_files:
        try:
            content = _fetch_remote_file(ccu_url, rel_path)
            strings.update(_parse_loc_content(content))
        except Exception:
            pass  # Localization files are optional

    return strings


def _list_sender_tcl_files_remote(
    *,
    ccu_url: str,
    receiver_type: str,
) -> list[str]:
    """
    List available TCL sender files from a remote CCU.

    Since directory listing is not always available, probe a comprehensive
    set of known sender types and check which files exist.
    """
    found: list[str] = []
    base = _EASYMODE_BASE

    for sender_type in _KNOWN_SENDER_TYPES:
        try:
            _fetch_remote_file(ccu_url, f"{base}/{receiver_type}/{sender_type}.tcl")
            found.append(sender_type)
        except Exception:
            pass

    return found


def _parse_receiver_remote(
    *,
    ccu_url: str,
    receiver_type: str,
) -> dict[str, Any]:
    """Parse all sender profiles for a receiver type from a remote CCU."""
    result: dict[str, Any] = {}

    sender_types = _list_sender_tcl_files_remote(ccu_url=ccu_url, receiver_type=receiver_type)
    if not sender_types:
        return result

    base = _EASYMODE_BASE
    for sender_type in sender_types:
        try:
            tcl_content = _fetch_remote_file(ccu_url, f"{base}/{receiver_type}/{sender_type}.tcl")
        except Exception as err:
            print(f"  WARNING: Failed to fetch {sender_type}.tcl: {err}", file=sys.stderr)
            continue

        loc_en = _load_localization_remote(
            ccu_url=ccu_url,
            receiver_type=receiver_type,
            sender_type=sender_type,
            locale="en",
        )
        loc_de = _load_localization_remote(
            ccu_url=ccu_url,
            receiver_type=receiver_type,
            sender_type=sender_type,
            locale="de",
        )

        profiles = _parse_tcl_profiles(
            tcl_content=tcl_content,
            loc_en=loc_en,
            loc_de=loc_de,
        )

        if profiles:
            result[sender_type] = {"profiles": profiles}
            print(f"  {sender_type}: {len(profiles)} profiles")

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Parse easymode profiles from OCCU source."""
    occu_path = os.environ.get("OCCU_PATH")
    ccu_url = os.environ.get("CCU_URL")
    receivers_str = os.environ.get("RECEIVERS")
    output_dir_str = os.environ.get("OUTPUT_DIR", _DEFAULT_OUTPUT_DIR)

    if not occu_path and not ccu_url:
        print(
            "ERROR: Set OCCU_PATH (local checkout) or CCU_URL (running OpenCCU) environment variable.",
            file=sys.stderr,
        )
        return 1

    # Resolve output directory relative to project root
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / output_dir_str
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine source: prefer running CCU instance over local checkout
    use_remote = bool(ccu_url)
    if use_remote:
        print(f"Using running OpenCCU instance: {ccu_url}")
        if occu_path:
            print(f"  (local OCCU at {occu_path} available as fallback)")
    else:
        print(f"Using local OCCU checkout: {occu_path}")

    # Determine receiver types to parse
    if receivers_str:
        receivers = [r.strip() for r in receivers_str.split(",") if r.strip()]
        print(f"\nParsing {len(receivers)} specified receiver type(s)...")
    elif occu_path:
        receivers = _discover_receiver_types_local(Path(occu_path))
        print(f"\nAuto-discovered {len(receivers)} receiver type(s) from local OCCU.")
    else:
        receivers = list(_KNOWN_RECEIVER_TYPES)
        print(f"\nUsing {len(receivers)} known receiver type(s) for remote discovery.")

    if not receivers:
        print("ERROR: No receiver types found.", file=sys.stderr)
        return 1

    total_written = 0
    for receiver_type in receivers:
        print(f"\nParsing {receiver_type}...")

        data: dict[str, Any] = {}

        if use_remote:
            data = _parse_receiver_remote(ccu_url=ccu_url, receiver_type=receiver_type)
            # Fall back to local if remote yields nothing and local is available
            if not data and occu_path:
                print("  Remote yielded no results, falling back to local OCCU...")
                data = _parse_receiver_local(occu_path=Path(occu_path), receiver_type=receiver_type)
        elif occu_path:
            data = _parse_receiver_local(occu_path=Path(occu_path), receiver_type=receiver_type)

        if data:
            out_file = output_dir / f"{receiver_type}.json"
            out_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"  -> Written to {out_file}")
            total_written += 1
        else:
            print(f"  No profiles found for {receiver_type}")

    print(f"\nDone. {total_written} profile file(s) written to {output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
