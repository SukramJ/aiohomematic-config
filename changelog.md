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
