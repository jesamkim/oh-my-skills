# Troubleshooting Guide

## Common Issues

### 1. Formatting Lost After Translation

**Symptom**: Font sizes, colors, or styles are different in the translated PPTX.

**Cause**: `paragraph.text` was used instead of `run.text`.

**Fix**: Always use the provided scripts. The `apply_translation.py` script only modifies `run.text` and never touches the Font object. Re-run the workflow using the scripts.

**Verify**: Run `verify_formatting.py` to confirm:
```bash
python scripts/verify_formatting.py original.pptx KO_original.pptx
```

If it reports "run count mismatch", that confirms paragraph-level text replacement was used.

### 2. Run Count Mismatch Error

**Symptom**: `verify_formatting.py` reports different run counts between original and translated.

**Cause**: Runs were added or removed during translation. This happens if:
- `paragraph.text` was used (destroys all runs, creates one)
- Runs were manually deleted and recreated
- The JSON was incorrectly edited to add/remove run entries

**Fix**: Re-extract the text and re-translate. Ensure the number of runs in the translated JSON matches the original exactly.

### 3. Text Overflow in Translated Slides

**Symptom**: Korean text is cut off or extends beyond text box boundaries.

**Cause**: Korean text can be wider than English text for the same content, especially with CJK fonts at smaller sizes.

**Workaround**:
- Most PPTX text boxes have auto-fit or shrink-text-on-overflow enabled — this handles minor differences
- For significant overflow, manually adjust font size or text box size in PowerPoint
- Consider using more concise Korean phrasing where possible

### 4. Missing Text from Grouped Shapes

**Symptom**: Some text elements are not translated in the output.

**Cause**: The text might be inside deeply nested group shapes.

**Fix**: The extraction script recursively traverses group shapes. If text is still missing:
1. Check the extracted JSON to confirm the text was captured
2. Look for the text in the JSON — it may be under a `"group"` type element
3. If the text is not in the JSON, the shape may use a format not covered by the script (e.g., embedded OLE objects)

### 5. Table Text Not Translated

**Symptom**: Text inside tables remains in English.

**Cause**: Table cells need special handling — they have their own text frames.

**Fix**: The extraction script handles tables via `cell.text_frame`. Check the JSON output for `"type": "table"` elements. If missing:
1. Verify the table is a native PPTX table (not an image of a table)
2. Check if the table is inside a group shape

### 6. Speaker Notes Not Translated

**Symptom**: Presenter notes remain in English.

**Check**: Look for `"notes"` sections in the extracted JSON. If present, ensure `translated_text` is added to each run in the notes.

### 7. JSON Parse Errors

**Symptom**: `apply_translation.py` fails with JSON decode error.

**Cause**: The translated JSON file has syntax errors (common with manual editing or truncated output).

**Fix**:
1. Validate the JSON: `python -m json.tool translated.json`
2. Check for missing commas, unescaped quotes in translated text, or truncated content
3. Korean text with special characters should be properly escaped in JSON

### 8. python-pptx Not Installed

**Symptom**: `ModuleNotFoundError: No module named 'pptx'`

**Fix**:
```bash
pip install python-pptx
```

Or if using a specific Python environment:
```bash
python3 -m pip install python-pptx
```

## Debugging Tips

### Inspect Extracted JSON

The JSON output shows the exact structure of runs:
```bash
python -m json.tool extracted_text.json | head -50
```

Look for:
- `has_formatting: true` — runs with explicit formatting that should keep key terms
- Long `full_text` values — complex paragraphs that need careful run distribution
- Empty or whitespace-only runs — preserve these as-is

### Compare Slide XML Directly

For deep debugging, unzip both PPTX files and compare the slide XML:

```bash
mkdir -p /tmp/orig /tmp/trans
unzip -o original.pptx -d /tmp/orig
unzip -o KO_original.pptx -d /tmp/trans
diff /tmp/orig/ppt/slides/slide1.xml /tmp/trans/ppt/slides/slide1.xml
```

Only `<a:t>` elements should differ. If `<a:rPr>` elements differ, formatting was corrupted.

### Check Run Count Per Slide

Quick check to see total runs per slide:
```python
from pptx import Presentation
prs = Presentation("original.pptx")
for i, slide in enumerate(prs.slides):
    runs = 0
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                runs += len(para.runs)
    print(f"Slide {i+1}: {runs} runs")
```

## Large File Tips

### Memory Usage

`python-pptx` loads the entire presentation into memory. For very large files (>100MB):
- Ensure at least 2x the file size available in RAM
- Close other applications if needed
- The `--per-slide` mode doesn't reduce memory for extraction (the full PPTX is still loaded), but it helps with translation parallelism

### Translation Speed

For large decks (30+ slides):
- Use Workflow B (parallel) with sub-agents
- Group 5-6 slides per sub-agent for optimal throughput
- Each sub-agent translates its assigned slides independently
- No merge conflicts since each slide JSON is a separate file

### Verify Before Sharing

Always run `verify_formatting.py` before sharing translated files. A quick check catches issues early and saves time.
