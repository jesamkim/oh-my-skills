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

## 시작하기

이 저장소는 Claude Code 플러그인 마켓플레이스 구조를 따릅니다. 아래 절차대로 등록하면 `/plugin` 명령으로 스킬을 설치할 수 있습니다.

> Claude Code가 처음이라면 [Claude Code Quickstart Guide](https://docs.claude.com/en/docs/claude-code/quickstart)를 먼저 확인하세요.

### 1단계: Claude Code 설치

**macOS:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://claude.ai/install.ps1 | iex
```

### 2단계: 저장소 클론

```bash
git clone https://github.com/jesamkim/oh-my-skills.git
cd oh-my-skills
```

### 3단계: 마켓플레이스 등록

**방법 A: Claude Code 안에서 `/plugin`으로 등록 (권장)**

Claude Code 세션에서 아래 명령을 실행하세요. 클론한 저장소의 절대 경로를 인자로 넘깁니다.

```
/plugin marketplace add /absolute/path/to/oh-my-skills
```

- 예: `/plugin marketplace add /Users/jesamkim/workspace/oh-my-skills`
- GitHub에서 바로 등록도 가능합니다:
  ```
  /plugin marketplace add jesamkim/oh-my-skills
  ```

등록이 되면 `/plugin marketplace list`에 `oh-my-skills`가 보입니다.

**방법 B: `~/.claude/settings.json` 직접 편집**

```json
{
  "extraKnownMarketplaces": {
    "oh-my-skills": {
      "source": {
        "source": "directory",
        "path": "/absolute/path/to/oh-my-skills"
      }
    }
  }
}
```

> 예시: `"path": "/Users/jesamkim/workspace/oh-my-skills"` 또는 `"/Workshop/oh-my-skills"`

### 4단계: 스킬 설치

**방법 A: CLI로 바로 설치 (빠름)**

원하는 스킬만 설치:
```bash
/plugin install aws-diagram@oh-my-skills
/plugin install myslide@oh-my-skills
/plugin install svg-diagram@oh-my-skills
/plugin install readme@oh-my-skills
/plugin install paper-finder@oh-my-skills
/plugin install youtube-script@oh-my-skills
/plugin install agentcore-browser@oh-my-skills
/plugin install computer-use@oh-my-skills
/plugin install kiro@oh-my-skills
```

한 번에 모두 설치:
```bash
/plugin install aws-diagram@oh-my-skills myslide@oh-my-skills svg-diagram@oh-my-skills readme@oh-my-skills paper-finder@oh-my-skills youtube-script@oh-my-skills agentcore-browser@oh-my-skills computer-use@oh-my-skills kiro@oh-my-skills
```

**방법 B: 대화형 설치**

1. Claude Code에서 `/plugin` 실행
2. **Browse and install plugins** 선택
3. **oh-my-skills** 마켓플레이스 선택
4. 설치할 스킬 체크
5. **Install now** 클릭

설치가 끝나면 Claude가 작업 내용에 맞춰 자동으로 해당 스킬을 호출합니다.

### 스킬 관리

```bash
# 설치된 플러그인 확인 (UI)
/plugin → Manage Plugins

# 최신 버전으로 업데이트
/plugin update aws-diagram@oh-my-skills
/plugin update myslide@oh-my-skills

# 활성화 / 비활성화
/plugin enable aws-diagram@oh-my-skills
/plugin disable aws-diagram@oh-my-skills

# 제거
/plugin uninstall aws-diagram@oh-my-skills
```

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
