---
name: youtube-script
description: |
  YouTube transcript extractor. Extracts captions/subtitles from YouTube videos
  and saves them as text files. Supports auto-generated and manual captions
  in multiple languages (Korean, English, etc.).
  Use this skill whenever the user provides a YouTube URL and wants to extract
  the transcript, subtitles, captions, or script. Also trigger when the user
  says "youtube script", "youtube transcript", "유튜브 스크립트", "자막 추출",
  "유튜브 자막", "extract captions", "get subtitles", or pastes a youtu.be
  or youtube.com link and asks about its content or transcript.
license: MIT License
metadata:
  skill-author: jesamkim
  version: 1.0.0
allowed-tools: [Read, Write, Bash, AskUserQuestion]
---

# YouTube Transcript Extractor

Extract subtitles/captions from YouTube videos using the `youtube_transcript_api` library.

## Prerequisites

The skill uses a bundled Python script that requires `youtube_transcript_api`.
Check if the package is available:

```bash
pip show youtube-transcript-api 2>/dev/null || pip install youtube-transcript-api
```

If a known working venv exists at `~/QCLI/youtube-script/venv/`, use that Python directly:
```bash
~/QCLI/youtube-script/venv/bin/python ${SKILL_DIR}/scripts/extract_transcript.py <URL>
```

## Workflow

### Step 1: Parse the YouTube URL

Extract the video ID from the URL. Supported formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- URLs with additional parameters (playlist, timestamp, etc.)

### Step 2: Run the extraction script

```bash
python ${SKILL_DIR}/scripts/extract_transcript.py <URL> [OPTIONS]
```

Options:
- `--language` / `-l`: Preferred language code (default: auto-detect). Examples: `ko`, `en`, `ja`
- `--output` / `-o`: Output file path (default: `{video_id}_transcript.txt` in CWD)
- `--with-timestamps`: Include timestamps in output
- `--json`: Output as JSON with timestamps and metadata

The script tries to fetch captions in this order:
1. Manual captions in the preferred language
2. Auto-generated captions in the preferred language
3. Any available captions (fallback)

### Step 3: Report results

After extraction, report:
- Video ID
- Language detected
- Character count / word count
- Output file path
- First ~200 characters as preview

If the transcript is needed for further processing (e.g., enriching lecture notes, summarizing),
read the saved file and proceed with the downstream task.

## Error Handling

- **No captions available**: Some videos have captions disabled. Inform the user and suggest
  alternatives (e.g., downloading audio and using Whisper via `/yonsei transcribe`).
- **Video unavailable**: Private, deleted, or age-restricted videos may fail. Report the error clearly.
- **Rate limiting**: If YouTube blocks requests, wait and retry once after a short delay.

## Examples

**Example 1: Basic extraction**
```
User: "이 유튜브 영상 스크립트 뽑아줘 https://youtu.be/Z6-QSTia1tY"
→ Run extract_transcript.py with the URL
→ Save to Z6-QSTia1tY_transcript.txt
→ Report: language, length, preview
```

**Example 2: With specific language**
```
User: "Extract the English transcript from https://www.youtube.com/watch?v=abc123"
→ Run with --language en
→ Save and report
```

**Example 3: For lecture note enrichment**
```
User: "이 유튜브 영상 내용을 Week 3 노트에 추가해줘 https://youtu.be/xyz"
→ Extract transcript
→ Read transcript content
→ Summarize key points
→ Add to the relevant notes file
```
