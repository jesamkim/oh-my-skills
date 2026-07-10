# Translation Output Report

## Summary

| Item | Value |
|------|-------|
| Source File | `{source_file}` |
| Output File | `{output_file}` |
| Target Language | {target_language} |
| Total Slides | {total_slides} |
| Total Runs Translated | {total_runs} |
| Formatting Verified | {verified} |

## Slide-by-Slide Summary

| Slide | Elements | Runs Translated | Notes |
|-------|----------|-----------------|-------|
| 1 | Title, Body | 12 | — |
| 2 | Title, Table | 24 | Table with 3x4 cells |
| ... | ... | ... | ... |

## Terms Kept in English

- AWS service names: Amazon Bedrock, Amazon S3, AWS Lambda, ...
- Technical acronyms: API, SDK, GenAI, LLM, RAG, ...
- Product names: ...

## Issues / Notes

- Slide X: Text box may overflow due to longer Korean text
- Slide Y: Chart text not translatable (embedded image)

## Verification Result

```
FORMATTING VERIFICATION REPORT
================================
Slides checked: {total_slides}
Slides OK:      {slides_ok}
Issues found:   0
RESULT: PASS — All formatting preserved correctly
```
