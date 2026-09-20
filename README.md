# zotero-reader-skill
<<<<<<< HEAD
AI Agent Skill: Read and query local Zotero library - list literature, search papers, locate PDFs.
=======

An AI Agent Skill that reads and queries your local Zotero library — list literature, search by keyword, locate PDF files, browse tags and collections.

Works with any AI agent that supports skills (Doubao, Claude, Cursor, etc.).

## Features

- 📚 **List literature** — browse all items with PDF attachments
- 🔍 **Search by keyword** — find papers by title
- 📄 **Locate PDFs** — get full filesystem path to any paper's PDF
- 🏷️ **Browse tags** — see all tags and their counts
- 📁 **Browse collections** — list folders and their items
- 📊 **Library stats** — total items, PDF count, detected paths

## Quick Start

### 1. Install the Skill

Copy this folder into your agent's skills directory:

```bash
# Example for Doubao
cp -r zotero-reader-skill ~/.doubao/agent_mode/workspace/.user_skills/zotero-reader

# Example for Claude Code
cp -r zotero-reader-skill ~/.claude/skills/zotero-reader
```

### 2. Configure Zotero Path (optional)

The script auto-detects Zotero on Windows/macOS/Linux. If auto-detection fails, set the path:

**Option A — Environment variable (recommended):**
```bash
# Windows
setx ZOTERO_DIR "C:\Users\YourName\Zotero"

# macOS / Linux
export ZOTERO_DIR="/home/yourname/Zotero"
```

**Option B — Command line flag:**
```bash
python scripts/zotero_query.py --zotero-dir "/path/to/zotero" info
```

### 3. Verify Installation

```bash
python scripts/zotero_query.py info
```

You should see your Zotero directory path and library statistics.

## Usage

Once installed, just talk to your AI agent naturally:

| You say... | What happens |
|-------------|-------------|
| "How many papers are in my Zotero?" | Runs `info` command |
| "List my recent papers" | Runs `list --limit 10` |
| "Find papers about critical thinking" | Runs `search "critical thinking"` |
| "Read the AI ethics paper from my Zotero" | Finds the paper and locates its PDF |
| "What tags do I have?" | Runs `tags` command |
| "Show my collections" | Runs `collections` command |

## CLI Reference

```bash
# Show library stats and detected paths
python scripts/zotero_query.py info

# List all items with PDFs
python scripts/zotero_query.py list [--limit N]

# Search by title keyword
python scripts/zotero_query.py search "keyword" [--limit N]

# Get PDF path by item key or ID
python scripts/zotero_query.py get-pdf ABC123XYZ
python scripts/zotero_query.py get-pdf 42

# List all tags
python scripts/zotero_query.py tags

# List all collections
python scripts/zotero_query.py collections

# List items in a specific collection
python scripts/zotero_query.py collection-items "My Collection"
```

### Output Formats

Add `--format json` to any list/search command for machine-readable output:

```bash
python scripts/zotero_query.py search "AI literacy" --format json
```

## How It Works

- Reads `zotero.sqlite` directly in **read-only mode** (safe while Zotero is open)
- Resolves PDF paths from Zotero's storage layout: `<zotero_dir>/storage/<attachment_key>/<filename>.pdf`
- No additional Python packages required — uses only the standard library

## Requirements

- Python 3.7+ (standard library only, no pip install needed)
- A local Zotero installation with `zotero.sqlite`

## Project Structure

```
zotero-reader-skill/
├── SKILL.md              # Skill definition (for AI agents)
├── README.md             # This file
├── LICENSE               # MIT License
└── scripts/
    └── zotero_query.py   # Query script
```

## License

MIT
>>>>>>> 82b475c (Initial commit: zotero-reader skill - query Zotero library and locate PDFs)
