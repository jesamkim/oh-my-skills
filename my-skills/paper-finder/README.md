# paper-finder - Academic Paper Search & Discovery

Semantic Scholar, OpenAlex, ArXiv API를 활용한 학술 논문 검색 및 정리 도구.

## Features

- **키워드 검색**: 여러 학술 API를 통한 논문 검색
- **자동 Fallback**: Semantic Scholar → OpenAlex 자동 전환 (rate limit 대응)
- **논문 조회**: ArXiv ID 또는 DOI로 특정 논문 직접 조회
- **BibTeX 내보내기**: 검색 결과를 BibTeX 형식으로 저장
- **인용수 정렬**: 인용 횟수 기준 정렬로 영향력 있는 논문 우선 확인
- **마크다운 테이블**: 검색 결과를 깔끔한 테이블 형태로 출력

## Supported APIs

| API | Rate Limit | Notes |
|-----|------------|-------|
| Semantic Scholar | 100 req/5min (무료) | 기본 소스, 인용수 정확 |
| OpenAlex | ~100K req/day | Fallback 소스, 관대한 제한 |
| ArXiv | 3 req/sec | 프리프린트 검색 |

## Usage Examples

### 키워드 검색
```
"multi-agent LLM" 관련 논문 찾아줘
```

### ArXiv ID 조회
```
ArXiv 논문 2301.00234 찾아줘
```

### DOI 조회
```
이 DOI 논문 정보 알려줘: 10.1145/1234567.1234568
```

### BibTeX 내보내기
```
RAG 관련 논문 검색해서 BibTeX으로 저장해줘
```

## Requirements

- Python 3.8+
- 인터넷 연결 (API 호출용)
- API 키 불필요 (무료 사용 가능)

## Version History

- **v1.0.0** - Initial release with multi-API search, BibTeX export, and markdown output

## License

MIT License - See [LICENSE.txt](LICENSE.txt)

## Author

Jesam Kim (jesamkim@gmail.com)
