---
name: zotero-reader
description: Read and query local Zotero library - list literature, search papers, locate PDF files, extract PDF full text, browse tags and collections. Use when the user asks to read Zotero references, find papers in their Zotero library, access Zotero PDFs, read Zotero paper content, search Zotero collections, or work with literature stored in local Zotero. Triggers on phrases like "Zotero里的文献", "我的Zotero", "从Zotero找论文", "读取Zotero PDF", "读Zotero论文", "搜索我的文献库".
---

# Zotero Reader

Query the local Zotero database to list literature, search papers, resolve PDF file paths, and extract full text from PDFs. Works with a standard desktop Zotero installation.

## Quick Start

### 1. Query library metadata

```bash
python <skill_dir>/scripts/zotero_query.py <command> [options]
```

### 2. Extract PDF text content

```bash
python <skill_dir>/scripts/extract_pdf_text.py <pdf_path> [--pages 1-10]
```

The query script auto-detects the Zotero data directory. If auto-detection fails, pass `--zotero-dir <path>` or set `ZOTERO_DIR` environment variable.

## Commands

### `info` — Show detected paths and library stats

```bash
python scripts/zotero_query.py info
```

### `list` — List all items with PDF attachments

```bash
python scripts/zotero_query.py list [--limit N]
```

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

### `tags` — List all tags in the library

```bash
python scripts/zotero_query.py tags
```

### `collections` — List all collections

```bash
python scripts/zotero_query.py collections
```

### `collection-items <name>` — List items in a specific collection

```bash
python scripts/zotero_query.py collection-items "层累" [--limit N]
```

## Reading PDF Full Text (End-to-End Workflow)

This is the most common workflow: **search → locate PDF → extract text**.

### Step-by-step

1. **Search for the paper** by keyword:
   ```bash
   python scripts/zotero_query.py search "AI literacy" --limit 5
   ```
   Copy the `PDF:` path from the output.

2. **Extract PDF text** using the extracted path:
   ```bash
   # Extract all pages
   python scripts/extract_pdf_text.py "E:\path\to\paper.pdf"

   # Extract specific page range
   python scripts/extract_pdf_text.py "E:\path\to\paper.pdf" --pages 1-5

   # Save to file
   python scripts/extract_pdf_text.py "E:\path\to\paper.pdf" --output abstract.txt
   ```

### What the AI agent should do

When the user asks to **read** or **summarize** a Zotero paper:

1. Run `search "<keyword>"` to find the matching paper(s)
2. Extract the PDF path from the output
3. Run `extract_pdf_text.py <path>` (first ~5 pages for abstract/intro, or all pages if needed)
4. Analyze and summarize the extracted text for the user

## Output Formats

- Default: human-readable text (good for quick browsing).
- `--format json`: machine-readable JSON array — use when you need to parse results programmatically.

## Notes

- The query script opens the SQLite database read-only (`immutable=1`), so it is safe to run while Zotero is open.
- PDF paths follow the Zotero storage layout: `<zotero_dir>/storage/<attachment_key>/<filename>.pdf`.
- PDF text extraction requires PyMuPDF (`pip install pymupdf`).
- Only items with PDF attachments are shown by `list` and `search`.