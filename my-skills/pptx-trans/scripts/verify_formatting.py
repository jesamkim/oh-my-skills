#!/usr/bin/env python3
"""Verify formatting preservation between original and translated PPTX.

Usage:
    python verify_formatting.py original.pptx translated.pptx

Compares slide XML to ensure only <a:t> (text) elements changed,
while <a:rPr> (run properties / formatting) remain identical.
"""

import argparse
import os
import sys
import zipfile
from xml.etree import ElementTree as ET

# Namespace map for OOXML
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}


def get_slide_xmls(pptx_path):
    """Extract slide XML content from PPTX (which is a ZIP)."""
    slides = {}
    with zipfile.ZipFile(pptx_path, 'r') as zf:
        for name in sorted(zf.namelist()):
            if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
                slides[name] = zf.read(name)
    return slides


def extract_run_properties(xml_bytes):
    """Extract all run properties (<a:rPr>) from slide XML."""
    root = ET.fromstring(xml_bytes)
    runs_info = []

    # Find all <a:r> (run) elements
    for run_elem in root.iter(f'{{{NS["a"]}}}r'):
        rPr = run_elem.find(f'{{{NS["a"]}}}rPr')
        text_elem = run_elem.find(f'{{{NS["a"]}}}t')

        text = text_elem.text if text_elem is not None else ""

        # Serialize rPr to string for comparison (excluding text)
        if rPr is not None:
            rPr_str = ET.tostring(rPr, encoding='unicode', short_empty_elements=True)
        else:
            rPr_str = None

        runs_info.append({
            'text': text,
            'rPr': rPr_str,
        })

    return runs_info


def compare_slides(orig_xml, trans_xml, slide_name):
    """Compare formatting between original and translated slide."""
    orig_runs = extract_run_properties(orig_xml)
    trans_runs = extract_run_properties(trans_xml)

    issues = []

    if len(orig_runs) != len(trans_runs):
        issues.append({
            'type': 'run_count_mismatch',
            'slide': slide_name,
            'original_count': len(orig_runs),
            'translated_count': len(trans_runs),
        })
        return issues

    for i, (orig, trans) in enumerate(zip(orig_runs, trans_runs)):
        # Run properties should be identical
        if orig['rPr'] != trans['rPr']:
            issues.append({
                'type': 'formatting_changed',
                'slide': slide_name,
                'run_index': i,
                'original_text': orig['text'],
                'translated_text': trans['text'],
                'original_rPr': orig['rPr'],
                'translated_rPr': trans['rPr'],
            })

    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Verify formatting preservation between original and translated PPTX"
    )
    parser.add_argument("original", help="Path to original PPTX file")
    parser.add_argument("translated", help="Path to translated PPTX file")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed per-slide comparison",
    )
    args = parser.parse_args()

    for path in [args.original, args.translated]:
        if not os.path.exists(path):
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)

    orig_slides = get_slide_xmls(args.original)
    trans_slides = get_slide_xmls(args.translated)

    # Check slide count
    if len(orig_slides) != len(trans_slides):
        print(f"WARNING: Slide count mismatch: original={len(orig_slides)}, translated={len(trans_slides)}")

    all_issues = []
    slides_checked = 0
    slides_ok = 0
    text_changes = 0

    for slide_name in sorted(orig_slides.keys()):
        if slide_name not in trans_slides:
            all_issues.append({
                'type': 'missing_slide',
                'slide': slide_name,
            })
            continue

        slides_checked += 1
        issues = compare_slides(orig_slides[slide_name], trans_slides[slide_name], slide_name)

        if issues:
            all_issues.extend(issues)
        else:
            slides_ok += 1

        # Count text changes
        orig_runs = extract_run_properties(orig_slides[slide_name])
        trans_runs = extract_run_properties(trans_slides[slide_name])
        for orig, trans in zip(orig_runs, trans_runs):
            if orig['text'] != trans['text']:
                text_changes += 1

        if args.verbose:
            status = "OK" if not issues else f"{len(issues)} issue(s)"
            print(f"  {slide_name}: {status}")

    # Report
    print("\n" + "=" * 60)
    print("FORMATTING VERIFICATION REPORT")
    print("=" * 60)
    print(f"Original:    {args.original}")
    print(f"Translated:  {args.translated}")
    print(f"Slides checked: {slides_checked}")
    print(f"Slides OK:      {slides_ok}")
    print(f"Text changes:   {text_changes}")
    print(f"Issues found:   {len(all_issues)}")
    print()

    if not all_issues:
        print("RESULT: PASS - All formatting preserved correctly")
        print("  Only <a:t> (text) elements were modified.")
        print("  All <a:rPr> (run properties) remain identical.")
    else:
        print("RESULT: ISSUES DETECTED")
        print()
        for issue in all_issues:
            itype = issue['type']
            slide = issue.get('slide', 'unknown')

            if itype == 'run_count_mismatch':
                print(f"  [{slide}] Run count mismatch: {issue['original_count']} -> {issue['translated_count']}")
                print(f"    This means paragraph.text was used instead of run.text!")
            elif itype == 'formatting_changed':
                print(f"  [{slide}] Run {issue['run_index']}: formatting changed")
                print(f"    Text: '{issue['original_text']}' -> '{issue['translated_text']}'")
            elif itype == 'missing_slide':
                print(f"  [{slide}] Missing in translated file")
            print()

    return 0 if not all_issues else 1


if __name__ == "__main__":
    sys.exit(main())
