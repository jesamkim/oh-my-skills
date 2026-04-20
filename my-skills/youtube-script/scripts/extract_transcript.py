#!/usr/bin/env python3
"""
YouTube Transcript Extractor
Extracts captions/subtitles from YouTube videos.
"""

import argparse
import json
import re
import sys


def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")


def fetch_transcript(video_id: str, language: str | None = None):
    """Fetch transcript using youtube_transcript_api."""
    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()

    if language:
        try:
            return api.fetch(video_id, languages=[language]), language
        except Exception:
            pass

    # Fallback: try common languages, then any available
    for lang in ['en', 'ko', 'ja', 'zh']:
        try:
            return api.fetch(video_id, languages=[lang]), lang
        except Exception:
            continue

    # Last resort: fetch whatever is available
    try:
        transcript = api.fetch(video_id)
        return transcript, 'auto'
    except Exception as e:
        raise RuntimeError(f"No captions available for video {video_id}: {e}")


def format_transcript(transcript_data, with_timestamps: bool = False) -> str:
    """Format transcript data into plain text."""
    lines = []
    for item in transcript_data:
        if with_timestamps:
            start = item.start
            minutes = int(start // 60)
            seconds = int(start % 60)
            lines.append(f"[{minutes:02d}:{seconds:02d}] {item.text}")
        else:
            lines.append(item.text)

    if with_timestamps:
        return '\n'.join(lines)
    else:
        return ' '.join(lines)


def main():
    parser = argparse.ArgumentParser(description='YouTube Transcript Extractor')
    parser.add_argument('url', help='YouTube URL')
    parser.add_argument('--language', '-l', default=None,
                        help='Preferred language code (e.g., ko, en, ja)')
    parser.add_argument('--output', '-o', default=None,
                        help='Output file path')
    parser.add_argument('--with-timestamps', action='store_true',
                        help='Include timestamps in output')
    parser.add_argument('--json', action='store_true', dest='as_json',
                        help='Output as JSON with metadata')

    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        transcript_data, detected_lang = fetch_transcript(video_id, args.language)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    text = format_transcript(transcript_data, args.with_timestamps)

    output_path = args.output or f"{video_id}_transcript.txt"

    if args.as_json:
        result = {
            'video_id': video_id,
            'language': detected_lang,
            'char_count': len(text),
            'word_count': len(text.split()),
            'output_file': output_path,
            'transcript': text,
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(json.dumps({k: v for k, v in result.items() if k != 'transcript'},
                         ensure_ascii=False, indent=2))
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

        # Print summary to stdout
        print(f"video_id: {video_id}")
        print(f"language: {detected_lang}")
        print(f"chars: {len(text)}")
        print(f"words: {len(text.split())}")
        print(f"output: {output_path}")
        print(f"preview: {text[:200]}...")


if __name__ == '__main__':
    main()
