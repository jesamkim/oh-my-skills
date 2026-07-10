# pptx-trans — Format-Preserving PPTX Translation

> Created by **Jesam Kim** (AWS Solutions Architect)

Translate English PPTX presentations to Korean (or other languages) while preserving **100% of the original formatting**.

## The Problem

When translating PPTX files using python-pptx, setting `paragraph.text = "..."` destroys all run-level formatting — font size, color, typeface, bold, italic are all lost. This is because python-pptx deletes all existing runs and creates a single new run without any formatting properties.

## The Solution

This skill uses **run-level text replacement** (`run.text = "..."`) which only modifies the `<a:t>` text element in the XML while keeping the `<a:rPr>` run properties (formatting) completely intact.

## Installation

### Prerequisites

```bash
pip install python-pptx lxml
```

> `lxml` is also a dependency of python-pptx, but `apply_translation.py` imports it directly for East Asian font XML manipulation.

### Korean Font (Recommended)

The `apply_translation.py` script sets an East Asian font (`--ea-font "Nanum Gothic"` by default) on runs containing CJK characters. This ensures proper rendering when the original font (e.g., Amazon Ember) lacks Korean glyphs. Install a Korean font for best results:

**Ubuntu/Debian:**
```bash
sudo apt-get install -y fonts-nanum
fc-cache -fv
```

**macOS:**
```bash
brew install --cask font-nanum-gothic
```

**Windows:**
- Download Nanum Gothic from [Google Fonts](https://fonts.google.com/specimen/Nanum+Gothic) and install manually, or use the built-in Malgun Gothic (automatically detected as fallback).

The script tries these fonts in order: Nanum Gothic, NanumGothic, Apple SD Gothic Neo (macOS), Malgun Gothic (Windows). If no Korean font is found, EA font setting is skipped and the translated PPTX still works — but CJK characters may not render correctly in some viewers.

To disable EA font setting entirely, use `--no-ea-font`.

### Install as Claude Code Skill

Add the skill directory to your Claude Code configuration:

```bash
# Clone or copy to your skills directory
cp -r pptx-trans/ /path/to/your/skills/
```

## Usage

### Quick Start

1. Trigger with: "translate pptx", "PPTX 번역", "translate slides"
2. Provide the path to your PPTX file
3. The skill handles extraction, translation, and application automatically

### Manual Workflow

```bash
# 1. Extract text to JSON
python scripts/extract_text.py presentation.pptx

# 2. Translate the JSON (done by Claude)

# 3. Apply translation back to PPTX
python scripts/apply_translation.py presentation.pptx presentation_text.json --prefix KO_

# 4. Verify formatting
python scripts/verify_formatting.py presentation.pptx KO_presentation.pptx
```

### Large Presentations (>10 slides)

```bash
# 1. Extract per-slide
python scripts/extract_text.py presentation.pptx --per-slide

# 2. Translate each slide JSON (parallelizable)

# 3. Apply all translations
python scripts/apply_translation.py presentation.pptx --per-slide --prefix KO_

# 4. Verify
python scripts/verify_formatting.py presentation.pptx KO_presentation.pptx
```

## Scripts

| Script | Purpose |
|--------|---------|
| `extract_text.py` | Extract text at run-level from PPTX to JSON |
| `apply_translation.py` | Apply translated JSON back to PPTX |
| `verify_formatting.py` | Verify formatting preservation between files |

## Options

### extract_text.py

| Option | Default | Description |
|--------|---------|-------------|
| `--per-slide` | off | Output one JSON per slide |
| `--output-dir` | input dir | Output directory |
| `--target-lang` | `ko` | Target language code |

### apply_translation.py

| Option | Default | Description |
|--------|---------|-------------|
| `--per-slide` | off | Read per-slide JSON files |
| `--prefix` | `KO_` | Output filename prefix |
| `--output-dir` | input dir | Output directory |
| `--ea-font` | `Nanum Gothic` | East Asian font for CJK characters |
| `--no-ea-font` | off | Disable East Asian font setting |

### verify_formatting.py

| Option | Default | Description |
|--------|---------|-------------|
| `--verbose` | off | Show per-slide details |

## How It Works

1. **Extract**: Parses PPTX using python-pptx, recording every run's text and position (slide/shape/paragraph/run indices)
2. **Translate**: Claude translates text using full paragraph context, then distributes translations across runs
3. **Apply**: Writes translated text back to the exact same runs using `run.text = ...`
4. **Verify**: Compares slide XML to confirm only `<a:t>` changed while `<a:rPr>` stayed identical

## Supported Elements

- Text frames (titles, body text, text boxes)
- Tables (cell-level text)
- Grouped shapes (recursive traversal)
- Speaker notes
- Multi-level bullet points

## License

MIT License
