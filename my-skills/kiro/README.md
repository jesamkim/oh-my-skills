# Kiro CLI Delegation Skill

Claude Code가 **Kiro CLI(`kiro-cli`)** 에 작업을 위임하기 위한 스킬입니다. 컨텍스트
윈도우가 부족하거나, 독립된 AI 세션으로 격리 분석/제2의 의견이 필요하거나, 변경
사항에 대한 **전문 코드 리뷰**가 필요할 때 사용합니다. (`kiro-cli`는 Amazon Q
Developer CLI의 후속 제품이며 `q` 명령이 여기에 alias 되어 있습니다.)

## Overview

| Item | Value |
|------|-------|
| **Version** | 2.0.0 |
| **Author** | Jesam Kim |
| **License** | MIT |
| **Default Model** | `auto` (CLI 기본값, task-routed, 1.00x credits) |
| **검증 기준** | kiro-cli 2.7.1 (2026-06, 바이너리 직접 introspection + 실측) |

## 두 가지 모드

### 1. 범용 위임 — `scripts/run_kiro.sh`

Kiro의 새 컨텍스트에서 임의의 작업을 실행하고 깨끗한 텍스트 결과를 돌려받습니다.
기본 권한은 **읽기 전용**(`fs_read`)이라 파일을 수정하지 않습니다.

```bash
# 기본 (읽기 전용)
bash my-skills/kiro/scripts/run_kiro.sh "Summarize /abs/path/to/doc.md"

# 권한 수준 선택 (필요한 최소 권한만):
bash run_kiro.sh --trust none "CAP theorem의 트레이드오프 설명"     # 파일 접근 없음
bash run_kiro.sh --trust read "/abs/path/to/file.py 요약"          # 읽기 전용(기본)
bash run_kiro.sh --trust all  "/abs/path/to/project/ 리팩터링"      # 쓰기 허용(-a)

# 추론 깊이 / 모델 / 타임아웃 / 에이전트:
bash run_kiro.sh --effort high "이 race condition을 신중히 분석"
bash run_kiro.sh --model claude-sonnet-4.6 --timeout 600 "대형 코드베이스 분석"
bash run_kiro.sh --agent kiro_planner "이 아이디어를 구현 계획으로 분해"

# 컨텍스트 파이프 (프롬프트 앞에 prepend):
git diff | bash run_kiro.sh "이 변경의 정확성 검토"
```

### 2. 코드 리뷰 특화 — `scripts/run_kiro_review.sh`

codex 스킬의 리뷰 모드와 동일한 역할을, Kiro의 컨텍스트로 수행합니다. git 상태에서
리뷰 범위를 자동 감지하고, **적대적(adversarial) 읽기 전용** 리뷰를 돌려 `file:line` +
심각도 + 수정안 + `VERDICT: ship | no-ship` 를 반환합니다.

```bash
# git 상태에서 범위 자동 감지 (base보다 앞서면 branch diff, 아니면 working tree)
bash my-skills/kiro/scripts/run_kiro_review.sh

# 명시적 범위:
bash run_kiro_review.sh --scope working-tree                  # staged+unstaged+untracked
bash run_kiro_review.sh --scope branch --base origin/develop  # 이 브랜치 vs base
bash run_kiro_review.sh -- src/payments/ src/auth/handler.ts  # 명시적 경로

# 튜닝:
bash run_kiro_review.sh --focus "concurrency and the retry path"
bash run_kiro_review.sh --json                       # 기계 판독용 JSON 블록도 출력
bash run_kiro_review.sh --model claude-opus-4.8 --effort max   # 가장 깊은 리뷰
```

**핵심 속성 (codex 리뷰 계약과 동일):**

- **리뷰 전용.** findings만 보고하며 수정/패치/stage/commit 하지 않습니다. 결과는
  메인 에이전트나 사용자에게 넘겨 처리합니다.
- **구조상 읽기 전용.** 래퍼가 git diff/status를 미리 계산해 컨텍스트로 넘기고 Kiro는
  `fs_read`로만 실행 — 리뷰 중 어떤 것도 변경할 수 없습니다.
- **자가 검증(`/goal`의 가치를 headless로 재현).** 프롬프트가 Kiro에게 각 finding을
  실제 코드로 확인(파일 읽기 → 경로 확인 → `file:line` 인용)한 뒤 보고하도록 지시합니다.
- **구조화 + verbatim 둘 다.** 기본은 사람이 읽는 findings, `--json`이면 JSON 블록
  (`verdict`, `summary`, `findings[]`)도 추가. 결과는 **verbatim**으로 전달하고 임의로
  고치거나 요약하지 않습니다.

선택적으로 영속 리뷰 에이전트(`assets/agents/code-reviewer.json`)를 `~/.kiro/agents/`
에 복사하고 `KIRO_REVIEW_AGENT=code-reviewer` 를 설정하면, 검증 단계에서 git/grep도
함께 쓸 수 있습니다. 이 에이전트의 config 자체가 `execute_bash`를 읽기 전용
git/grep/조회 명령으로 제한합니다(`rm`/`mv`/`commit`/`push`/리다이렉션 등을 denylist로
차단). 에이전트 사용 시 래퍼는 CLI에서 `--trust none`을 넘기고 **에이전트의 config가
trust의 단일 출처**가 되도록 하므로, 리뷰가 에이전트가 선언한 것보다 넓은 권한을 조용히
얻는 일이 없습니다. 단, 이 경로는 번들된 `code-reviewer`(또는 사용자가 읽기 전용으로
검증한 에이전트)에만 사용하세요 — 쓰기 가능한 에이전트를 지정하면 읽기 전용 리뷰가
아닙니다. 기본 경로(에이전트 없음, `fs_read`만)는 설치가 필요 없고 가장 안전합니다.

## `/goal` 등 인터랙티브 기능에 대하여 (중요)

kiro-cli 2.7.x는 `/goal`(성공 기준을 인용 증거로 검증한 뒤 완료하는 goal-driven 자율
루프)을 추가했습니다. 강력하지만 **`/goal`·`/plan`·`/model` 피커 등 인터랙티브 슬래시
커맨드는 `--no-interactive`(headless)에서 작동하지 않습니다** — 터미널이 필요하며
무시되거나 에러가 납니다. (실측으로 확인: `/goal ...`을 headless 입력으로 넘겨도 아무
동작 안 함.)

이 스킬은 **비인터랙티브 위임** 용도이므로 `/goal`을 직접 호출하지 않고, 리뷰 모드가
그 가치(반복·증거 기반 검증)를 프롬프트로 재현합니다. 진짜 인터랙티브 `/goal` 루프가
필요하면 사용자가 직접 `kiro-cli chat` 후 `/goal <설명> [--max N]`을 실행하면 됩니다.

## 모델 선택 (검증됨)

CLI 실제 기본값은 `auto`(1.00x credits, task별 라우팅)이며 스크립트도 이를 따릅니다.
`--model`은 결정성이나 특정 티어가 필요할 때만 지정하세요. `claude-opus-4.8`은 2.2x
credits이므로 일상 작업에 하드코딩하지 마세요.

| Model | Credits | 용도 |
|-------|---------|------|
| `auto` (기본) | 1.00x | 대부분의 위임 |
| `claude-haiku-4.5` | 0.40x | 저렴/빠른 요약·간단 점검 |
| `claude-sonnet-4.6` | 1.30x | 균형 분석, 1M context |
| `claude-opus-4.8` | 2.20x | 가장 어려운 추론/깊은 리뷰 |

## Prerequisites

- [Kiro CLI](https://kiro.dev) 설치 — macOS는 `/Applications/Kiro CLI.app/`, Linux는
  PATH의 `kiro-cli`. 래퍼가 바이너리를 자동 감지하며 `KIRO_BIN` 환경변수로 override
  가능합니다.
- 인증: `kiro-cli login` (CI는 Pro 플랜에서 `KIRO_API_KEY`).
- (선택) 하드 타임아웃을 쓰려면 coreutils `timeout`/`gtimeout`. 없으면 타임아웃 없이
  실행됩니다.

## 동작 원리

1. Claude Code가 필요한 모든 컨텍스트(절대 경로, 지시, 기대 출력 형식)를 담은
   프롬프트를 구성합니다. Kiro는 대화 맥락을 공유하지 않으므로 self-contained 해야 합니다.
2. 래퍼가 `kiro-cli chat --no-interactive`를 호출합니다(모델/effort/trust/agent 지정).
3. **터미널 chrome 제거**: ANSI 코드, OSC "Response complete" 마커, 선행 `> ` 접두사를
   제거합니다. macOS BSD `sed`는 `\x1b` hex escape를 인식하지 못하므로 `perl`로 처리합니다.
4. 깨끗한 텍스트를 stdout으로 반환합니다(진행/에러는 stderr).

## 종료 코드

| Code | 의미 |
|------|------|
| 0 | 성공 |
| 1 | 일반 실패 (인증, 잘못된 모델 등) |
| 2 | 인자 파싱 에러 |
| 3 | MCP 시작 실패 (`--require-mcp-startup` 사용 시) |
| 124 | 타임아웃 |

비-0 종료는 결과가 신뢰할 수 없음을 의미하므로 항상 종료 코드를 확인하세요.

## File Structure

```
kiro/
├── SKILL.md                          # Claude Code 스킬 정의
├── README.md                         # 이 파일
├── LICENSE                           # MIT License
├── scripts/
│   ├── run_kiro.sh                   # 범용 위임 래퍼 (ANSI strip, 타임아웃, trust)
│   └── run_kiro_review.sh            # 코드 리뷰 특화 (git scope 감지, 적대적 리뷰)
└── assets/
    ├── prompts/
    │   └── adversarial-review.md     # 리뷰어 프롬프트 템플릿
    └── agents/
        └── code-reviewer.json        # (선택) 영속 리뷰어 에이전트 — kiro-cli 검증 통과
```

## Changelog

### v2.0.0
- **코드 리뷰 특화 모드 추가** (`run_kiro_review.sh`): git scope 자동 감지
  (working-tree/branch/paths), 적대적 읽기 전용 리뷰, `/goal`식 자가 검증, 구조화+verbatim
  출력, ship/no-ship 판정. codex 스킬의 리뷰 계약을 Kiro 컨텍스트로 재현.
- **범용 래퍼 현대화**: 기본 모델 `auto`(기존 `claude-opus-4.8` 하드코딩 제거),
  `--effort`/`--agent`/`--trust`(read/all/none)/`--trust-tools` 옵션 추가, 기본 권한을
  읽기 전용으로.
- **버그 수정**: macOS BSD `sed`에서 ANSI stripping이 실패하던 문제를 `perl` 기반으로
  교체(실측 확인), pipe+prompt 동시 사용 시 stdin 유실, 대형 출력의 `echo` ARG_MAX
  위험(`printf`로 교체), 누락 인자 처리.
- `/goal` 등 인터랙티브 슬래시 커맨드가 headless에서 동작하지 않음을 문서화하고 그
  가치를 프롬프트로 재현하는 설계 근거 추가.

### v1.0.0
- 초기 릴리스: `kiro-cli chat --no-interactive` 기반 단순 위임 래퍼.
```
```
