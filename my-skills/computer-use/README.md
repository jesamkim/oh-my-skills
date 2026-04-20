# computer-use - Bedrock Computer Use GUI Automation

Amazon Bedrock Computer Use를 활용한 데스크톱 GUI 자동화 에이전트. 스크린샷 분석 → 액션 지시 → 실행의 에이전틱 루프로 실제 마우스/키보드를 제어한다.

## Features

- **스크린샷 기반 GUI 제어**: 모델이 화면을 보고 클릭/입력/스크롤 등을 자동 수행
- **에이전틱 루프**: 스크린샷 캡처 → Bedrock API 호출 → 액션 실행 → 검증 → 반복
- **모델 버전 자동 감지**: Claude 3.5~4.6 모델별 tool version/beta header 자동 매핑
- **시스템 프롬프트**: 모델에게 추론/검증 가이드라인 제공으로 정확도 향상
- **Intelligent Retry**: Transient error 자동 재시도 (exponential backoff + jitter)
- **다양한 액션 지원**: 클릭, 더블/트리플 클릭, 우클릭, 드래그, 텍스트 입력, 단축키, 스크롤, hold_key, mouse_down/up, 대기
- **토큰 사용량 추적**: 스텝별/누적 토큰 사용량 리포팅
- **venv 자동 설정**: 최초 실행 시 가상 환경 생성 및 의존성 자동 설치
- **안전 장치**: Fail-safe, 액션 간 딜레이, max-steps 제한

## Model Support

| Generation | Models | Computer Tool | 비고 |
|------------|--------|--------------|------|
| **4.6** | Opus 4.6, Sonnet 4.6 | `computer_20251124` | 기본 모델 (Opus 4.6), 최고 성능 |
| **4.5** | Opus 4.5, Sonnet 4.5, Haiku 4.5 | `computer_20250124` | 안정적, 비용 효율적 |
| **4.x** | Opus 4.1, Sonnet 4.0 | `computer_20250124` | 호환 지원 |
| **3.5** | Claude 3.5 Sonnet v2 | `computer_20241022` | Legacy 지원 |

> 모델 ID에 따라 tool version과 beta header가 자동으로 결정됨.

## Prerequisites

- AWS account with Amazon Bedrock access
- macOS: **접근성 권한** (System Settings > Privacy & Security > Accessibility)
- macOS: **Screen Recording 권한** (스크린샷 캡처용)
- Python 3.10+ (venv 자동 생성됨)

## Usage Examples

### 웹 브라우저 조작
```
AWS 콘솔에서 Bedrock 서비스 페이지로 이동해줘
```

### 애플리케이션 조작
```
Finder에서 Downloads 폴더 열어줘
```

### 폼 입력 자동화
```
로그인 페이지에서 이메일 입력해줘
```

### 모델 지정
```
--model us.anthropic.claude-sonnet-4-5-20250929-v1:0 으로 브라우저에서 검색해줘
```

## Troubleshooting

| 문제 | 해결 |
|------|------|
| `pyautogui.FailSafeException` | 마우스를 화면 모서리로 이동 시 안전 정지 발동 (정상) |
| 접근성 권한 오류 | System Settings > Privacy & Security에서 터미널 권한 부여 |
| 스크린샷이 검은 화면 | Screen Recording 권한 확인 |
| `ValidationException` | 모델 ID 확인 — tool version은 자동 감지됨 |
| `ThrottlingException` | 자동 재시도됨; 지속 시 Bedrock 할당량 확인 |
| 좌표가 어긋남 | Retina 디스플레이 자동 처리됨; 해상도 설정 확인 |

## Security Considerations

Computer Use는 실제 데스크톱을 제어하므로 주의:
- 민감한 계정이 로그인된 상태에서의 실행 자제
- 가능하면 전용 VM/컨테이너에서 실행
- `--max-steps`로 최대 반복 횟수 제한 (기본 50회)

## Version History

- **v2.0.0** - Model auto-detection (3.5~4.6), system prompt, retry logic, token tracking, enhanced actions
- **v1.1.0** - Fix tool name mapping, update defaults
- **v1.0.0** - Initial release with Bedrock Converse API Computer Use support

## License

MIT License - See [LICENSE](LICENSE)

## Author

Jesam Kim (jesamkim@gmail.com)
