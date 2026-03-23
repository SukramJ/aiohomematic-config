# Version 2026.3.4 (2026-03-23)

- Add easymode metadata enrichment to `FormSchemaGenerator`: conditional visibility (`visible_when`), option presets (`presets`, `allow_custom_value`), and subset membership (`subset_group_id`)
- Add `SubsetOption` and `SubsetGroup` models for combined parameter selection groups
- Add `sender_type` parameter to `FormSchemaGenerator.generate()` and `ParameterGrouper.group()`
- Add metadata-based parameter ordering in `ParameterGrouper` using easymode `parameter_order`
- Add cross-parameter validation via `validate_cross_parameters()` in `ConfigSession.validate()` and `ConfigSession.validate_changes()`
- Add `master_profile_store` module with `MasterProfileStore` and `ResolvedMasterProfile` for MASTER paramset easymode profiles

# Version 2026.3.3 (2026-03-21)

- Add `is_hmip` parameter to `FormSchemaGenerator.generate()` to resolve channel types for HmIP-specific translation lookups (e.g., `SHUTTER_CONTACT` → `SHUTTER_CONTACT_HMIP`)
- Use `resolve_channel_type()` from aiohomematic for HmIP channel type resolution
- Bump aiohomematic dependency to >=2026.3.11

# Version 2026.3.2 (2026-03-06)

- **Python 3.14 minimum**: Dropped Python 3.13 support
- Remove `from __future__ import annotations` required import (no longer needed with Python 3.14)
- Bump aiohomematic dependency to >=2026.3.2
- Update all tool configurations (ruff, mypy, pylint) to target Python 3.14

# Version 2026.3.1 (2026-03-05)

- Add `device_active_profile_index` field to `ClimateScheduleData` for active profile index from device
- Fix pre-commit branch protection to use `main` instead of `master`
- Bump aiohomematic dependency to >=2026.3.1

# Version 2026.3.0 (2026-03-01)

- Follow TCL `source` includes to resolve profiles defined in shared files (e.g. `profiles.tcl`, `profilesTunableWhite.tcl`)
- Strip trailing TCL comments (`;#`) from constraint values
- Add profiles for new receiver types: `AUTO_RELOCK_TRANSCEIVER`, `DOOR_LOCK_TRANSCEIVER`, `UNIVERSAL_LIGHT_RECEIVER_LSC`, `UNIVERSAL_LIGHT_RECEIVER_RGB(W)`, `UNIVERSAL_LIGHT_RECEIVER_RGBW_DALI`, `UNIVERSAL_LIGHT_RECEIVER_TW`
- Regenerate all profile JSON files

# Version 2026.2.15 (2026-03-01)

- Handle TCL `[subst {...}]` wrappers in easymode profile constraint parsing
- Regenerate all profile JSON files with `[subst]` support

# Version 2026.2.14 (2026-02-28)

- Resolve TCL `$variable` references in easymode profile constraints (e.g. `$NOP`, `$RAMP_ON`)
- Add `.env` support to `parse_easymode_profiles.py` via `python-dotenv`
- Regenerate all profile JSON files with improved constraint parsing

# Version 2026.2.13 (2026-02-28)

- Fix URL-encoded umlauts in profile names and descriptions (`%D6` → `Ö`) by adding `urllib.parse.unquote()` before `html.unescape()`
- Fix profile matching to prefer most specific profile when multiple profiles match (highest fixed-constraint count wins)

# Version 2026.2.12 (2026-02-27)

- Add `device_icon` field to `FormSchema` with icon filename from CCU device database
- Use `get_device_icon()` from aiohomematic to resolve device model icons
- Bump aiohomematic dependency to >=2026.2.30

# Version 2026.2.11 (2026-02-27)

- Add `description` field to `FormParameter` with Markdown-formatted parameter help text
- Use `get_parameter_help()` from aiohomematic to populate help texts (locale-aware, with LINK prefix stripping)
- Bump aiohomematic dependency to >=2026.2.29

# Version 2026.2.10 (2026-02-24)

- Use prefix matching for `channel_address` filter in `ConfigChangeLog.get_entries()` to match all channels of a device

# Version 2026.2.9 (2026-02-22)

- Use `schedule_domain` property from aiohomematic instead of local heuristic
- Remove `_get_schedule_domain()` helper and `ScheduleType` import from `schedule_facade`

# Version 2026.2.8 (2026-02-21)

- Add `schedule_facade` module for schedule management in the configuration panel
- Add `ScheduleDeviceInfo`, `ClimateScheduleData`, `DeviceScheduleData` dataclasses
- Add `list_schedule_devices()` for discovering devices with schedule support
- Add `get_climate_schedule()` / `set_climate_schedule_weekday()` / `set_climate_active_profile()` for climate schedules
- Add `get_device_schedule()` / `set_device_schedule()` for generic device schedules
- Export all schedule facade types and functions in public API
- Fix table formatting in API docs

# Version 2026.2.7 (2026-02-19)

- **Breaking**: `ProfileStore.get_profiles()` and `ProfileStore.match_active_profile()` are now async
- Fix blocking `read_text` / `open` calls inside the async event loop (uses `asyncio.to_thread`)

# Version 2026.2.6 (2026-02-19)

- Add `change_log` module for tracking paramset configuration changes
- Add `ConfigChangeLog` class with FIFO-capped storage, filtering, and serialization
- Add `ConfigChangeEntry` frozen dataclass for immutable change records
- Add `build_change_diff()` helper for computing old/new value diffs
- Export `ConfigChangeLog`, `ConfigChangeEntry`, `build_change_diff` in public API
- Bump aiohomematic dependency to >=2026.2.20

# Version 2026.2.5 (2026-02-17)

- Add `link_param_metadata` module for classifying link paramset parameters
- Add `LinkParamCategory`, `KeypressGroup`, `TimeSelectorType` enums
- Add `LinkParamMeta`, `TimePreset` dataclasses
- Add `classify_link_parameter()` for SHORT/LONG grouping, time pair detection, and category classification
- Add `get_time_presets()`, `decode_time_value()`, `encode_time_value()` for time base/factor handling
- Add time preset tables for on/off, delay, and ramp durations (extracted from OCCU)
- Add `enrich_link_metadata` parameter to `FormSchemaGenerator.generate()`
- Add optional link metadata fields to `FormParameter`: `keypress_group`, `category`, `display_as_percent`, `has_last_value`, `hidden_by_default`, `time_pair_id`, `time_selector_type`, `time_presets`

# Version 2026.2.4 (2026-02-13)

- Add locale-aware section titles to `ParameterGrouper` (German translations)
- Add `LabelResolver.has_translation()` to check for upstream translation availability
- Filter parameters without CCU translation in `FormSchemaGenerator` (matches CCU WebUI easymode behavior)
- Always populate `option_labels` on VALUE_LIST parameters with humanized fallback
- Pass locale from `FormSchemaGenerator` to `ParameterGrouper`
- Bump aiohomematic dependency to >=2026.2.12

# Version 2026.2.3 (2026-02-13)

- Replace local translation files with upstream CCU translations from aiohomematic
- Add `channel_type` parameter to `LabelResolver.resolve()` for context-aware labels
- Add `option_labels` field on `FormParameter` for translated VALUE_LIST entries
- Add `model_description` and `channel_type_label` fields on `FormSchema`
- Add `model` and `sub_model` parameters to `FormSchemaGenerator.generate()`
- Remove `strings.json`, `translations/` directory, and `check_i18n_catalogs.py`

# Version 2026.2.2 (2026-02-11)

- Rename `device_type` to `model` in ExportedConfiguration to align with aiohomematic
- Fix linter and type checker compliance (ruff, mypy, pylint, bandit, yamllint)
- Use public API imports in tests

# Version 2026.2.1 (2026-02-11)

- Initial release
- FormSchemaGenerator: Generate UI form schemas from paramset descriptions
- ParameterGrouper: Group parameters into logical sections
- LabelResolver: Translate parameter IDs to human-readable labels (en/de)
- ConfigSession: Change tracking with undo/redo and validation
- ConfigExporter: Export/import device configurations as JSON
- WidgetType mapping: Type-aware widget selection
