# AWS Diagram Troubleshooting & Fixes

Read this file when diagrams have visual issues after generation.

## Common Pitfalls & Fixes

### 1. VPC border overlaps with outside-VPC services
**Symptom:** S3, SQS icons visually touch or sit on the VPC rectangle border.
**Fix:** Skip 1 grid column between rightmost VPC node and first outside-VPC node. If VPC ends at x=5, start outside services at x=7.

### 2. Right-side labels clipped by viewBox
**Symptom:** Labels on rightmost nodes are cut off.
**Fix:** Widen viewBox (+150px right margin). In SVG, find `viewBox="0 0 W H"` and increase W.

### 3. Arrows crossing container title bars
**Symptom:** Arrow line passes through "VPC" or "AWS Cloud" header text.
**Fix:** The engine auto-reroutes below title bars. If still happening, move the source/target node to a different y to avoid the header zone.

### 4. Multiple arrows overlapping from same node
**Symptom:** Two arrows exit from the same edge of a node, merging visually.
**Fix:** Assign explicit `source_port` values to each connection. E.g., one uses `"source_port": "right"`, another `"source_port": "bottom"`.

### 5. Generic container too tight or too wide
**Symptom:** Logical group container clips its children or has excessive empty space.
**Fix:** Ensure all child nodes are listed in the container's `children[]` array. The engine auto-calculates bounds from children. Adjust grid positions if needed.

### 6. Arrow line crosses over a service icon
**Symptom:** An arrow path visually passes through another service icon that is not the source or target.
**Fix:** Three options (try in order):
1. Force explicit ports: add `"source_port": "bottom"` or `"target_port": "top"` to route around the icon
2. Move the blocking icon to a different grid position (change x or y by 1)
3. If the engine's 3-iteration obstacle avoidance isn't enough, split the long connection into two shorter ones via an intermediate service

### 7. Icons render as blank/missing in PNG
**Symptom:** White space where an icon should be.
**Fix:** Check that the `service` value matches an icon filename in `icons/`. Run with `--validate` flag to catch missing references.

### 8. Arrowhead pokes out the far side of the target icon
**Symptom:** A left-to-right arrow's head appears on the target icon's *right* edge (or a downward arrow's head on the *top* edge) — the line has run clean through the icon and out the other side. Often only a small stub is visible because the icon (drawn on top of arrows) hides most of the overrun.
**Cause:** The path's last `L` coordinate is on the icon's far edge instead of the near edge.
**Fix:** This was a router port-selection bug and is now fixed (`_auto_select_port` picks the edge facing the source for both endpoints). If you still see it — e.g. after forcing an awkward `target_port` — edit the SVG: find the arrow's `<path d="M ... L farX,Y">` and change the final coordinate to the near edge. The target's `<use href="#icon-..." x= y=>` gives the box; near-edge centers are `(x, y+24)` left, `(x+48, y+24)` right, `(x+24, y)` top, `(x+24, y+48)` bottom. Then `rsvg-convert -w 2048 file.svg -o file.png`.

### 9. Bottom-entering arrowhead spears the icon's label text
**Symptom:** An arrow that enters a node from below has its vertical segment and arrowhead running straight through the node's label / italic sublabel (e.g. through "Amazon Bedrock / Claude Opus · Sonnet · Haiku").
**Cause:** The engine stops the arrowhead at the icon's bottom edge (`y+48`), but the label sits ~14px below that and the sublabel ~14px below the label. Label height is not part of the icon box, so the router can't account for it.
**Fix:** Edit the SVG path's final `L x,Y` so `Y` is just under the lowest text line. With a sublabel, that's roughly the sublabel baseline + 10px; without one, the label line + ~16px. The arrowhead then lands cleanly beneath the text. Re-rasterize with `rsvg-convert`. Do NOT re-run the JSON generator afterward — it discards manual SVG edits.

---

## Post-Generation SVG Fixes

If the generated SVG has layout issues, apply these manual fixes before PNG conversion:

### Right-side label clipping
```bash
# Widen viewBox (add 150px right margin)
# Find: viewBox="0 0 1108 926" width="1108"
# Replace: viewBox="0 0 1258 926" width="1258"
```

### Container too wide (overlapping with outside nodes)
```bash
# Find the container <rect> and reduce width
# Example: VPC rect overlaps with right-side services
# Find: <rect x="474" ... width="604" ...>
# Replace: <rect x="474" ... width="500" ...>
# Also adjust child subnet rects to be narrower
```

### AWS Cloud container not covering all services
```bash
# Expand the AWS Cloud <rect> width to encompass right-side services
# Find: <rect x="270" ... width="848" ...> (first rect after </defs>)
# Replace: <rect x="270" ... width="968" ...>
```

### Regenerate PNG after SVG edits
```bash
rsvg-convert -o output.png output.svg
```
