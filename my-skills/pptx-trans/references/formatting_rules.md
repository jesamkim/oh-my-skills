# Formatting Preservation Rules

## Why Run-Level Replacement Matters

In OOXML (the format behind .pptx files), text formatting is stored at the **run** level. A paragraph can contain multiple runs, each with its own formatting properties.

### XML Structure

```xml
<a:p>                          <!-- paragraph -->
  <a:r>                        <!-- run 1 -->
    <a:rPr lang="en-US" b="1" sz="2400">  <!-- run properties (formatting) -->
      <a:solidFill><a:srgbClr val="FF0000"/></a:solidFill>
    </a:rPr>
    <a:t>Bold Red Text</a:t>   <!-- text content -->
  </a:r>
  <a:r>                        <!-- run 2 -->
    <a:rPr lang="en-US" sz="2400"/>  <!-- different formatting -->
    <a:t> Normal Text</a:t>
  </a:r>
</a:p>
```

### Key Elements

| Element | Purpose | Modified During Translation? |
|---------|---------|------------------------------|
| `<a:rPr>` | Run properties (font, size, color, bold, italic) | **NO — NEVER** |
| `<a:t>` | Text content | **YES — this is the only thing we change** |
| `<a:pPr>` | Paragraph properties (alignment, spacing, bullets) | **NO** |

## Safe vs Unsafe Operations

### SAFE: `run.text = "translated text"`

```python
for run in paragraph.runs:
    run.text = "번역된 텍스트"  # Font object is untouched
```

This only modifies the `<a:t>` element. The `<a:rPr>` element and its entire subtree (colors, fonts, effects) remain identical.

### UNSAFE: `paragraph.text = "translated text"`

```python
paragraph.text = "번역된 텍스트"  # DESTROYS ALL FORMATTING
```

**What actually happens internally:**
1. All existing `<a:r>` (run) elements are deleted
2. A single new `<a:r>` is created
3. The new run has no `<a:rPr>` — all formatting is lost
4. Font size, color, bold, italic, typeface — everything gone

### UNSAFE: Deleting and recreating runs

```python
# DON'T DO THIS
for run in paragraph.runs:
    paragraph._p.remove(run._r)
new_run = paragraph.add_run()
new_run.text = "translated"  # New run has no formatting
```

## Formatting Properties Reference

The `<a:rPr>` element can contain:

| Attribute/Child | What It Controls |
|----------------|------------------|
| `b="1"` | Bold |
| `i="1"` | Italic |
| `u="sng"` | Underline |
| `sz="2400"` | Font size (hundredths of a point; 2400 = 24pt) |
| `lang="en-US"` | Language |
| `<a:solidFill>` | Font color |
| `<a:latin typeface="...">` | Latin font (e.g., Calibri) |
| `<a:ea typeface="...">` | East Asian font (e.g., 맑은 고딕) |
| `<a:hlinkClick>` | Hyperlink |
| `<a:effectLst>` | Text effects (shadow, glow) |

All of these are preserved when using `run.text = ...`.

## Table Text Handling

Tables in PPTX store text in cells, each containing a text frame:

```
Table → Row → Cell → TextFrame → Paragraph → Run
```

The same rules apply: only modify `run.text`, never `paragraph.text` or `cell.text`.

## Speaker Notes Handling

Speaker notes use the same text frame structure:

```
Slide → NotesSlide → NotesTextFrame → Paragraph → Run
```

Apply the same run-level replacement.

## Grouped Shapes

Grouped shapes contain nested shape collections:

```
GroupShape → Shapes → [Shape1, Shape2, GroupShape2 → Shapes → ...]
```

The extraction script recursively traverses group shapes to find all text frames. The same run-level replacement applies at every nesting level.
