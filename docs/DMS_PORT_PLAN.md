# Document Management System — Port Plan

## Goal

Full document management for EVERJUST.APP tenants: create docs, organize files in workspaces, manage spreadsheets — the Enterprise Documents + Knowledge experience on Community.

## What we're porting

### Phase 1 — Available NOW (OCA/knowledge 19.0)

Already ported, just install:

| Module | What it does |
|---|---|
| `document_page` | Wiki-style rich-text documents with categories, version history, diffs |
| `document_knowledge` | Base knowledge framework |
| `document_page_partner` | Link docs to partners/contacts |
| `document_url` | URL-based document references |
| `attachment_zipped_download` | Download attachments as ZIP |

### Phase 2 — Port from 18.0 (OCA/dms)

Full file management system. 7 modules, estimated 5-8 days.

| Module | Files | Difficulty | Est. time |
|---|---|---|---|
| `dms` (core) | 212 | Hard | 3-5 days |
| `dms_field` | 71 | Hard | 2-3 days |
| `dms_auto_classification` | 28 | Medium | 0.5-1 day |
| `dms_field_auto_classification` | 27 | Medium | 0.5 day |
| `web_editor_media_dialog_dms` | 20 | Hard | 1-2 days |
| `dms_user_role` | 20 | Low | 0.5 day |
| `hr_dms_field` | 25 | Medium | 1 day |

### Phase 3 — Port from 18.0 (OCA/spreadsheet)

Standalone spreadsheet creation. 4 modules, estimated 4-7 days.

| Module | Files | Difficulty | Est. time |
|---|---|---|---|
| `spreadsheet_oca` | 65 | Very Hard | 3-5 days |
| `spreadsheet_dashboard_oca` | 28 | Medium | 1-2 days |
| `spreadsheet_dashboard_purchase_oca` | 61 | Low | 0.5 day |
| `spreadsheet_dashboard_purchase_stock_oca` | 61 | Low | 0.5 day |

## Migration tool

Use `oca-port` (v0.22):
```bash
pipx install oca-port
pipx inject --include-deps oca-port git+https://github.com/OCA/odoo-module-migrator.git@master
oca-port origin/18.0 origin/19.0 <module> --verbose
```

## Key Odoo 18→19 breaking changes to handle

| Change | Impact |
|---|---|
| `_apply_ir_rules()` removed | Replace with `_search(domain, bypass_access=True)` |
| `type='json'` deprecated | Use `type='jsonrpc'` or `type='http'` |
| `web_editor` renamed to `html_builder` | Breaks `web_editor_media_dialog_dms` |
| `res.groups.category_id` → `privilege_id` | Security XML must be updated |
| `res.users.groups_id` → `group_ids` | Any code referencing user groups |
| `<kanban-box>` → `<card>` | Kanban view XML |
| `hr.contract` → `hr.version` | Impacts `hr_dms_field` |
| 130 model renames, 51 field renames | Check all foreign key references |

## Port order

1. **`dms` core** — everything depends on it. Build on existing OCA PR #474 or #475.
2. **`dms_field`** — next dependency layer
3. **`dms_auto_classification` + `dms_field_auto_classification`** — parallel
4. **`web_editor_media_dialog_dms`** — needs `html_builder` investigation
5. **`hr_dms_field` + `dms_user_role`** — parallel
6. **`spreadsheet_oca`** — independent, hardest JS work
7. **`spreadsheet_dashboard_*`** — depends on #6

## What tenants get when done

- **Documents app** — file workspaces, upload/organize, access control, portal sharing
- **Knowledge/Wiki** — rich-text articles, categories, version history (Phase 1 — ready now)
- **Spreadsheets** — create/edit Google Sheets-like spreadsheets in browser (Phase 3)
- **Custom fields** — attach document management to any Odoo record
- **Auto-classification** — automatic document categorization
