# agentcore-browser

AWS Bedrock AgentCore Browser를 활용한 클라우드 기반 브라우저 자동화 skill.

## 개요

AgentCore Browser는 AWS가 관리하는 Chrome 144 브라우저 인스턴스를 CDP(Chrome DevTools Protocol)로 제어합니다. 로컬 Chrome 설치 없이, Python `boto3` + `websockets`만으로 웹 페이지 탐색, 데이터 추출, 폼 자동화, 스크린샷 캡처가 가능합니다.

## agent-browser와의 관계

이 skill은 `agent-browser`를 **대체하지 않고 보완**합니다.

| 항목 | agent-browser | agentcore-browser |
|------|---------------|-------------------|
| 실행 위치 | 로컬 Chrome | AWS 클라우드 (관리형) |
| 의존성 | agent-browser CLI + Chrome | boto3 + websockets |
| 속도 | 빠름 (로컬) | 네트워크 RTT 추가 |
| 비용 | 무료 | 세션 시간 기반 과금 |
| headless 서버 | CDP 우회 필요 | 기본 동작 |
| VPC 내부 접근 | 불가 | VPC 모드 지원 |
| 세션 지속성 | 프로세스 종료 시 소멸 | Browser Profile로 영구 저장 |

**사용 기준**: agent-browser를 먼저 시도하고, 다음 상황에서 이 skill로 전환:
- agent-browser CLI 미설치 / 실행 불가
- 로컬 Chrome 없는 headless 환경
- Python async 네이티브 통합 필요 (Strands, LangGraph 등)
- AWS VPC 내부 사이트 접근
- 세션 상태 영구 저장 필요

## 실험 결과 (2026-04-16)

실제 AgentCore Browser API를 탐색하여 확인한 사항:

### 프로토콜

- automation stream은 **CDP v1.3** (JSON-RPC over WebSocket)을 직접 노출
- SigV4 서명으로 WebSocket 인증
- Chrome 144.0 (`Amazon-Bedrock-AgentCore-Browser/1.0`)

### 테스트 결과

| 테스트 | 대상 | 결과 |
|--------|------|------|
| 웹 UI 폼 테스트 | httpbin.org/forms/post | PASS - 폼 입력/제출/검증 성공 |
| 환율 스크래핑 | finance.naver.com | PASS - 12개 환율/시세 실시간 추출 |
| 날씨 스크래핑 | wttr.in/Seoul | PASS - 3일 예보 추출 |
| 기상청 | weather.go.kr | FAIL - 서비스 오류 (사이트 자체 문제) |
| AccuWeather | accuweather.com | FAIL - AWS IP 차단 |

### 주의사항

- 일부 사이트는 AWS IP를 차단 (AccuWeather, 기상청 등)
- 세션은 시간 기반 과금 — 반드시 `stop()` 호출
- `element.value` 직접 설정은 일부 프레임워크에서 실패 — `type_text()`(CDP key events) 사용 권장

## 설치

```bash
/plugin install agentcore-browser@my-skills
```

## 파일 구조

```
agentcore-browser/
├── SKILL.md              # Skill 정의 (트리거 조건, 워크플로우, API)
├── README.md             # 이 파일
├── LICENSE.txt           # MIT License
└── scripts/
    ├── browser_client.py # CDP over WebSocket 클라이언트
    └── config.py         # 기본 설정 (region, viewport, timeout)
```

## 라이선스

MIT License - Jesam Kim
