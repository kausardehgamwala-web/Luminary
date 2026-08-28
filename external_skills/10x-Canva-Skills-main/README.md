# 10x Canva Skills

A comprehensive Claude Code skills plugin for **Canva API integration** AND **local file editing** (PDF, PPTX, DOCX, XLSX).

## Quick Setup (One Command)

**Before using these skills, run this setup command:**

```bash
python setup.py
```

This will:
- Install all required Python packages
- Create necessary folders
- Set up the environment

**Prerequisites:**
- Python 3.9 or higher installed
- pip (Python package manager)

---

## Features

### Local File Editing (No API Required)
- **PDF** - Read, modify, merge, split, extract text
- **PowerPoint** - Edit slides, text, images, notes
- **Word** - Modify documents, tables, formatting
- **Excel** - Update cells, formulas, sheets

### Canva Cloud Features (Requires API)
- Browse and manage Canva designs
- Export designs to various formats
- Organize folders and assets
- Apply brand consistency

### Safety First
- **Original files are NEVER modified**
- All edits work on copies in `output/` folder
- Full audit trail of changes

---

## Installation

### Step 1: Clone/Download

```bash
cd /path/to/your/projects
# Place this folder there
```

### Step 2: Run Setup

```bash
cd 10x-Canva-Skills
python setup.py
```

### Step 3: (Optional) Configure Canva API

Only needed if you want cloud Canva features:

1. Create an app at [Canva Developer Portal](https://www.canva.com/developers/)
2. Edit `.env` file with your credentials:

```env
CANVA_CLIENT_ID=your_client_id
CANVA_CLIENT_SECRET=your_client_secret
CANVA_ACCESS_TOKEN=your_token
```

### Step 4: Start Claude Code

```bash
claude
```

Skills are automatically available!

---

## Usage Examples

### Local File Editing (Works Immediately)

```
"Edit my presentation.pptx and change Q3 to Q4"
"Update the sales figures in report.pdf"
"Modify my document.docx - replace old company name with new"
"Update cell B5 in spreadsheet.xlsx"
```

### Canva Cloud (Requires API Setup)

```
"Show my Canva designs"
"Export my presentation as PDF"
"Move designs to Marketing folder"
"invoke canva to create a new Instagram post"
```

---

## How It Works

### 3-Mode Workflow

1. **PLAN** - Analyze file, document what will change
2. **CLARIFY** - Ask questions, confirm changes
3. **IMPLEMENT** - Execute on copy, save to output

### File Safety

```
Your File (input/)  →  Working Copy (output/working/)  →  Result (output/)
   [PROTECTED]              [ALL EDITS HERE]              [FINAL FILE]
   Never touched            Safe to modify                Your output
```

---

## Project Structure

```
10x-Canva-Skills/
├── .claude/                  # Claude Code integration
│   ├── skills/               # 16 specialized skills
│   │   ├── canva-*           # 11 Canva API skills
│   │   └── local-*           # 5 Local editing skills
│   ├── agents/               # Planning and execution agents
│   └── commands/             # Slash commands
│
├── scripts/                  # Python scripts
│   ├── canva_client.py       # Canva API client
│   └── local/                # Local file utilities
│       ├── pdf_utils.py
│       ├── pptx_utils.py
│       ├── docx_utils.py
│       ├── xlsx_utils.py
│       └── safe_copy.py      # File protection utility
│
├── input/                    # Place your files here
├── output/                   # Modified files saved here
├── samples/                  # Your style preferences
│
├── setup.py                  # ONE-TIME SETUP SCRIPT
├── requirements.txt          # Python dependencies
├── .env                      # API credentials (edit with your keys)
└── README.md                 # This file
```

---

## Skills Available

### Local File Editing (16 skills)

| Skill | Description |
|-------|-------------|
| `local-file-manager` | Routes to correct editor, enforces file safety |
| `local-pdf-editor` | PDF manipulation |
| `local-pptx-editor` | PowerPoint editing |
| `local-docx-editor` | Word document editing |
| `local-xlsx-editor` | Excel spreadsheet editing |

### Canva Cloud

| Skill | Description |
|-------|-------------|
| `canva-manager` | Main Canva orchestrator |
| `canva-explorer` | Browse account (read-only) |
| `canva-image-editor` | Edit image designs |
| `canva-presentation` | Edit presentations |
| `canva-video` | Edit videos |
| `canva-export` | Export to various formats |
| `canva-content-generator` | Generate content ideas |
| `canva-design-terminology` | Design knowledge base |
| `canva-folder-organizer` | Organize folders |
| `canva-asset-manager` | Manage uploaded assets |
| `canva-brand-kit` | Brand consistency |

---

## Troubleshooting

### Setup Issues

```bash
# If setup.py fails, try manually:
pip install -r requirements.txt
```

### Missing Dependencies

```bash
# Reinstall all dependencies:
pip install --upgrade -r requirements.txt
```

### Skills Not Loading

1. Ensure you're in the correct directory
2. Restart Claude Code
3. Check `.claude/skills/` folder exists

---

## Important Rules

1. **Original files are NEVER modified** - All work happens on copies
2. **Canva API is optional** - Local editing works without it
3. **Always runs setup first** - `python setup.py` before using
4. **Use "invoke canva" explicitly** - For cloud operations

---

## License

MIT License - Free to use and modify.

---

## Quick Reference

```bash
# Setup (run once)
python setup.py

# Start Claude Code
claude

# Example commands
"Edit my file.pdf"
"Update my presentation.pptx"
"invoke canva to export my design"
```
