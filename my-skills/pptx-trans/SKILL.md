---
name: pptx-trans
description: |
  Format-preserving PPTX translation skill using run-level text replacement.
  Translates English PowerPoint presentations to Korean (or other languages)
  while preserving 100% of original formatting (font size, color, typeface, bold, italic).
  Uses python-pptx run.text replacement to keep Font objects intact.
  Supports both sequential and parallel (sub-agent) workflows for large decks.
  Trigger: "translate pptx", "PPTX 번역", "translate slides", "번역해줘 pptx"
license: MIT License
metadata:
    skill-author: Jesam Kim
    version: 1.0.0
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
---

# PPTX Format-Preserving Translation

## Overview

Translate English PPTX presentations to Korean (or other target languages) while preserving **100% of the original formatting** — font size, color, typeface, bold, italic, underline, and all other run-level properties.

**Key Technical Principle**: Only `run.text` is modified. Font objects are never touched. This ensures every `<a:rPr>` (run properties) element in the slide XML remains identical.

**Target Audience**: AWS Solutions Architects and teams who need high-quality localized presentations.

## Critical Rules

### NEVER DO
- **NEVER** use `paragraph.text = "..."` — this destroys ALL run formatting
- **NEVER** delete or recreate runs — this loses Font objects
- **NEVER** modify `run.font` properties during translation

### ALWAYS DO
- **ALWAYS** use `run.text = "..."` to replace text within existing runs
- **ALWAYS** preserve the number of runs in each paragraph
- **ALWAYS** translate using full paragraph context, then distribute to runs

## Prerequisites

Install python-pptx:
```bash
pip install python-pptx
```

## Workflow A — Sequential (≤ 10 slides)

Use this workflow for presentations with 10 or fewer slides.

### Step 1: Extract text

Run the extraction script to generate a single JSON file:

```bash
python ${SKILL_DIR}/scripts/extract_text.py "${INPUT_PPTX}"
```

This creates `{filename}_text.json` in the same directory as the input file.

### Step 2: Translate the JSON

Read the generated JSON file. For each paragraph:

1. Read `full_text` to understand the complete sentence/phrase context
2. Translate the full paragraph into the target language
3. Distribute the translated text across the existing runs
4. Write the translated text into the `translated_text` field of each run

**Run distribution strategy**:

- **Single run paragraph**: Put the entire translation in that run's `translated_text`
- **Multi-run paragraph**: Translate the full paragraph first, then split the translation across runs proportionally, keeping meaning units together
- **Formatting runs** (`has_formatting: true`): These runs have special formatting (bold, colored, etc.). Keep key terms in these runs — especially AWS service names, product names, or emphasized words
- **Empty/whitespace runs**: Preserve spaces and line breaks as-is
- **Technical terms**: Keep AWS service names (Amazon S3, AWS Lambda, Amazon Bedrock, etc.) in English. Do NOT translate product names, service names, or technical acronyms

After translating, write the updated JSON back using the Write tool. The JSON structure should have `translated_text` added to each run:

```json
{
  "runs": [
    {"index": 0, "text": "Cloud", "translated_text": "클라우드", "has_formatting": true},
    {"index": 1, "text": " services are ", "translated_text": " 서비스는 ", "has_formatting": false},
    {"index": 2, "text": "transforming", "translated_text": "혁신하고 있습니다", "has_formatting": true},
    {"index": 3, "text": " the industry.", "translated_text": " — 산업 전반에 걸쳐.", "has_formatting": false}
  ]
}
```

### Step 3: Apply translation

```bash
python ${SKILL_DIR}/scripts/apply_translation.py "${INPUT_PPTX}" "${JSON_FILE}" --prefix KO_
```

This creates `KO_{original_filename}.pptx` with all formatting preserved. By default, `--ea-font "Nanum Gothic"` is applied to ensure Korean text renders correctly even when the original font (e.g., Amazon Ember) lacks Korean glyphs. The script automatically detects if the font is available on the system and falls back to other Korean fonts (Apple SD Gothic Neo on macOS, Malgun Gothic on Windows) if needed.

### Step 4: Verify formatting

```bash
python ${SKILL_DIR}/scripts/verify_formatting.py "${INPUT_PPTX}" "KO_${INPUT_FILENAME}"
```

Confirm the report shows "PASS — All formatting preserved correctly".

## Workflow B — Parallel (> 10 slides)

Use this workflow for large presentations to leverage sub-agent parallelism.

### Step 1: Extract text per slide

```bash
python ${SKILL_DIR}/scripts/extract_text.py "${INPUT_PPTX}" --per-slide
```

This creates individual `{filename}_slide_{N}.json` files.

### Step 2: Parallel translation with sub-agents

Launch Task tool sub-agents (haiku model) to translate slides in parallel. Group 5-6 slides per sub-agent:

```
Task(subagent_type="general-purpose", model="sonnet", prompt="
  You are a professional English-to-Korean translator for AWS presentations.
  Read the following slide JSON files and translate each run's text to Korean.
  Add 'translated_text' field to each run. Keep AWS service names in English.
  Translate using full paragraph context (full_text), then distribute to runs.

  CRITICAL JSON RULE: When writing JSON, you MUST escape double quotes inside
  string values with backslash. For example:
    WRONG: "full_text": "Gartner, "More than 80%""
    RIGHT: "full_text": "Gartner, \"More than 80%\""

  Files: {slide_file_1}, {slide_file_2}, ...
  Write the translated JSON back to the same files using the Write tool.
")
```

Launch multiple sub-agents simultaneously (e.g., 5-10 agents for 60 slides, 6 slides per agent).

> **Note**: The `apply_translation.py` script includes automatic JSON repair for common issues like unescaped quotes. Minor formatting errors in sub-agent output will be auto-corrected during the apply step.

### Step 3: Apply per-slide translations

```bash
python ${SKILL_DIR}/scripts/apply_translation.py "${INPUT_PPTX}" --per-slide --prefix KO_
```

### Step 4: Verify formatting

```bash
python ${SKILL_DIR}/scripts/verify_formatting.py "${INPUT_PPTX}" "KO_${INPUT_FILENAME}"
```

## Translation Quality Guidelines

### Korean Translation Standards

- Use natural Korean sentence structure (SOV order)
- Use appropriate honorific level (합쇼체 for formal presentations)
- Maintain consistency in terminology throughout the deck
- Preserve the tone and emphasis of the original

### Terms to Keep in English

- AWS service names: Amazon S3, AWS Lambda, Amazon Bedrock, Amazon EC2, etc.
- Product names: PowerPoint, Kubernetes, Docker, etc.
- Technical acronyms: API, SDK, CI/CD, ML, AI, GenAI, LLM, RAG, etc.
- Company/brand names
- URLs, email addresses

### Run Distribution Examples

**Example 1: Simple single-run paragraph**
```
Original:  [Run0: "Welcome to our presentation"]
Translate: [Run0: "프레젠테이션에 오신 것을 환영합니다"]
```

**Example 2: Multi-run with formatting**
```
Original:  [Run0(bold): "Amazon Bedrock"] [Run1: " enables generative AI applications"]
Translate: [Run0(bold): "Amazon Bedrock"] [Run1: "은 생성형 AI 애플리케이션을 가능하게 합니다"]
```

**Example 3: Complex multi-run**
```
Original:  [Run0: "Use "] [Run1(bold): "S3"] [Run2: " for storage and "] [Run3(bold): "Lambda"] [Run4: " for compute"]
Translate: [Run0: "스토리지에는 "] [Run1(bold): "S3"] [Run2: "를, 컴퓨팅에는 "] [Run3(bold): "Lambda"] [Run4: "를 사용합니다"]
```

## Edge Cases

- **Bullet points**: Translate each bullet independently; maintain bullet structure
- **Charts/SmartArt**: Text inside charts is extracted if it uses text frames; SmartArt may require manual review
- **Hyperlinks**: Preserved automatically (stored in run properties, not text)
- **Animations**: Preserved (stored at shape level, not affected by text changes)
- **Speaker notes**: Translated along with slide content
- **Tables**: Each cell is treated as an independent text frame with its own paragraphs and runs
- **Grouped shapes**: Recursively traversed to find all text frames

## Output File Naming

- Default prefix: `KO_` (Korean)
- Use `--prefix` for other languages: `JA_` (Japanese), `ZH_` (Chinese), etc.
- Example: `input.pptx` → `KO_input.pptx`
