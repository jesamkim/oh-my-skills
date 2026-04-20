# oh-my-skills

AWS 중심 워크플로, 시각 자료 생성, 에이전트 자동화를 위한 Claude Code 스킬 모음입니다.

## 제공 스킬

| 스킬 | 설명 |
|------|------|
| [`aws-diagram`](my-skills/aws-diagram/) | 공식 AWS Architecture Icons을 이용해 AWS 아키텍처 다이어그램을 SVG / PPTX로 생성합니다. |
| [`myslide`](my-skills/myslide/) | AWS 테마 PowerPoint 덱을 생성합니다 (다크 reInvent 테마 / 라이트 L100 테마). SVG 다이어그램 및 브랜드 컬러 내장. |
| [`svg-diagram`](my-skills/svg-diagram/) | 겹침 방지 규칙이 적용된 픽셀 단위 정밀 SVG 다이어그램, 배너, 히어로 그래픽을 생성합니다. |
| [`readme`](my-skills/readme/) | 커뮤니티 모범 사례를 따르는 세련된 README.md 파일을 자동 생성합니다. |
| [`paper-finder`](my-skills/paper-finder/) | Semantic Scholar, OpenAlex, ArXiv API 기반 논문 검색. BibTeX 내보내기 지원. |
| [`youtube-script`](my-skills/youtube-script/) | YouTube 영상의 자막/스크립트를 추출합니다 (한국어, 영어 등). |
| [`agentcore-browser`](my-skills/agentcore-browser/) | AWS Bedrock AgentCore Browser를 SigV4 서명된 WebSocket 위의 CDP로 자동화합니다. |
| [`computer-use`](my-skills/computer-use/) | Anthropic Computer Use 패턴 기반 GUI 자동화. |
| [`kiro`](my-skills/kiro/) | Claude Code 컨텍스트가 부족하거나 독립 세션이 필요할 때 Kiro CLI에 작업을 위임합니다. |

> `my-skills/scripts/`에는 위 스킬들이 공유하는 헬퍼 스크립트가 있습니다 (예: AWS 아이콘 추출).

## 설치

이 저장소는 Claude Code 플러그인 마켓플레이스 구조를 따릅니다.

```bash
# Claude Code가 읽을 수 있는 위치에 클론합니다
git clone https://github.com/jesamkim/oh-my-skills.git
```

이후 Claude Code에 로컬 플러그인 소스로 등록하세요. `my-skills/` 아래 각 스킬에는 트리거 문구와 사용법이 담긴 `SKILL.md`가 들어 있습니다.

## 구조

```
oh-my-skills/
├── .claude-plugin/
│   └── marketplace.json     # 플러그인 마켓플레이스 descriptor
├── my-skills/
│   ├── aws-diagram/
│   ├── myslide/
│   ├── svg-diagram/
│   ├── readme/
│   ├── paper-finder/
│   ├── youtube-script/
│   ├── agentcore-browser/
│   ├── computer-use/
│   ├── kiro/
│   └── scripts/             # 공용 헬퍼
├── LICENSE
└── README.md
```

## 라이선스

MIT License. [LICENSE](LICENSE)를 참고하세요.

Copyright (c) 2026 Jesam Kim
