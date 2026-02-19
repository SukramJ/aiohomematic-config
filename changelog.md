# Version 2026.2.7 (2026-02-19)

- Add `async_get_profiles()` and `async_match_active_profile()` to `ProfileStore` for event-loop-safe usage
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
