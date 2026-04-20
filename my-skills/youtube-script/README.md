# youtube-script - YouTube Transcript Extractor

YouTube 영상에서 자막/캡션을 추출하여 텍스트 파일로 저장하는 도구.

## Features

- **자동/수동 자막 추출**: 자동 생성 자막과 수동 자막 모두 지원
- **다국어 지원**: 한국어, 영어, 일본어 등 여러 언어의 자막 추출
- **타임스탬프 포함**: 선택적으로 시간 정보와 함께 추출
- **JSON 출력**: 메타데이터 포함 JSON 형식 지원
- **URL 자동 파싱**: youtube.com, youtu.be, embed 등 다양한 URL 형식 지원

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- 플레이리스트, 타임스탬프 등 추가 파라미터 포함 URL

## Usage Examples

### 기본 추출
```
이 유튜브 영상 스크립트 뽑아줘 https://youtu.be/Z6-QSTia1tY
```

### 언어 지정
```
이 영상의 영어 자막 추출해줘 https://www.youtube.com/watch?v=abc123
```

### 타임스탬프 포함
```
타임스탬프 포함해서 자막 뽑아줘
```

### 강의 노트 연동
```
이 유튜브 강의 내용을 Week 3 노트에 추가해줘
```

## Requirements

- Python 3.8+
- `youtube-transcript-api` 패키지

## Error Handling

| 문제 | 해결 |
|------|------|
| 자막 없음 | 일부 영상은 자막 비활성화됨. Whisper 등 대안 제안 |
| 비공개 영상 | 비공개/삭제/연령 제한 영상은 접근 불가 |
| Rate Limit | 잠시 후 자동 재시도 |

## Version History

- **v1.0.0** - Initial release with multi-language transcript extraction

## License

MIT License - See [LICENSE.txt](LICENSE.txt)

## Author

Jesam Kim (jesamkim@gmail.com)
