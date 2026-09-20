---
name: zotero-reader
description: Read and query local Zotero library - list literature, search by keyword, locate PDF files, browse tags and collections. Use when the user asks to read Zotero references, find papers in their Zotero library, access Zotero PDFs, search Zotero collections, or work with literature stored in local Zotero. Triggers on phrases like "Zotero里的文献", "我的Zotero", "从Zotero找论文", "读取Zotero PDF", "搜索我的文献库".
---

# Zotero Reader

Query the local Zotero database to list literature, search papers, and resolve PDF file paths. Works with a standard desktop Zotero installation.

## Quick Start

Run the bundled query script:

```bash
python <skill_dir>/scripts/zotero_query.py <command> [options]
```

The script auto-detects the Zotero data directory. If auto-detection fails, pass `--zotero-dir <path>`.

## Commands

### `info` — Show detected paths and library stats

```bash
python scripts/zotero_query.py info
```

Use this first to verify Zotero is detected and see library size.

### `list` — List all items with PDF attachments

```bash
python scripts/zotero_query.py list [--limit N]
```

Shows title, authors, date, and PDF path for each item.

### `search <keyword>` — Search items by title keyword

```bash
python scripts/zotero_query.py search "critical thinking" [--limit N]
```

Case-insensitive substring search on item titles.

### `get-pdf <item_ref>` — Get PDF path for a specific item

```bash
python scripts/zotero_query.py get-pdf EKVTVPSC   # by item key
python scripts/zotero_query.py get-pdf 5           # by numeric item ID
```

Returns the full filesystem path to the PDF file(s) for that item.

### `tags` — List all tags in the library

```bash
python scripts/zotero_query.py tags
```

### `collections` — List all collections

```bash
python scripts/zotero_query.py collections
```

## Typical Workflow

1. **Confirm Zotero is detected**: run `info` first.
2. **Find the paper**: use `search "<keyword>"` or `list --limit 20` to browse.
3. **Get the PDF path**: copy the `PDF:` path from list/search output, or run `get-pdf <key>`.
4. **Read the PDF**: pass the resolved path to the PDF processing skill / Read tool to extract content.

## Output Formats

- Default: human-readable text (good for quick browsing).
- `--format json`: machine-readable JSON array — use when you need to parse results programmatically.

## Notes

- The script opens the SQLite database read-only (`immutable=1`), so it is safe to run while Zotero is open.
- PDF paths follow the Zotero storage layout: `<zotero_dir>/storage/<attachment_key>/<filename>.pdf`.
- Only items with PDF attachments are shown by `list` and `search`. To see all items (including those without PDFs), query the database directly.
