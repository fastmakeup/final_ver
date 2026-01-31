# SDK-less Verification Scenario: HandOverAI

이 문서는 개발 도구(Python, Node.js, C++ Redistributable 등)가 설치되지 않은 제한된 환경(공공기관 내부망 등)에서 HandOverAI가 정상 작동하는지 검증하기 위한 시나리오를 정의합니다.

## 1. 검증 대상
- **대상**: `HandOverAI-Setup.exe` (인스톨러)
- **목표 환경**: Windows 10/11 Home/Pro (클린 설치 상태)

## 2. 검증 환경 준비 (SDK-less Simulation)
가장 확실한 방법은 가상머신(VM) 또는 리셋된 PC를 사용하는 것입니다.

### 시뮬레이션 환경 조건
- [ ] Python이 설치되어 있지 않음 (`where python` 시 결과 없음)
- [ ] Node.js/npm이 설치되어 있지 않음
- [ ] Visual C++ Redistributable이 설치되어 있지 않음 (또는 최소 버전)
- [ ] 네트워크 연결 제한 (옵션: 내부망 환경 시뮬레이션)

## 3. 테스트 시나리오

### 시나리오 1: 설치 및 시작 (Deployment)
1. **절차**:
   - `HandOverAI-Setup.exe` 실행
   - 설치 경로 확인 (`C:\Program Files\HandOverAI` 등)
   - 바탕화면 및 시작 메뉴 바로가기 생성 확인
2. **성공 기준**:
   - 관리자 권한 요청이 정상적으로 뜨고 설치가 완료됨
   - WebView2 런타임 체크 경고창이 상황에 맞게 노출됨

### 시나리오 2: 실행 및 UI 로딩 (UI Integrity)
1. **절차**:
   - 생성된 바로가기를 통해 앱 실행
2. **성공 기준**:
   - Splash Screen(FE) 이후 메인 화면이 정상적으로 렌더링됨
   - "React 빌드를 찾을 수 없습니다" 경고가 뜨지 않아야 함

### 시나리오 3: 로컬 AI 분석 (Engine Functional Test)
1. **절차**:
   - 임의의 문서 폴더(또는 `dummy_data`)를 선택하여 분석 실행
   - 챗봇에 질문 입력 (예: "예산 항목 알려줘")
2. **성공 기준**:
   - `.venv` 없이 패키징된 바이너리가 정상적으로 LLM/ChromaDB를 로드함
   - 분석 결과 JSON이 `%LOCALAPPDATA%\HandOverAI` 경로에 정상 생성됨

### 시나리오 4: 데이터 영속성 (Persistence)
1. **절차**:
   - 앱 종료 후 재실행
   - 이전 분석 내역이 유지되는지 확인
2. **성공 기준**:
   - `Program Files`가 아닌 `%LOCALAPPDATA%`를 사용하므로 권한 문제 없이 데이터가 유지됨

## 4. 체크리스트
| 항목 | 결과 | 비고 |
| :--- | :---: | :--- |
| 인스톨러 정상 실행 | [ ] | |
| WebView2 런타임 감지 | [ ] | |
| 바로가기 아이콘 생성 | [ ] | |
| 앱 실행 (백그라운드 로딩) | [ ] | |
| 폴더 분석 기능 (AI 엔진) | [ ] | |
| 챗봇 응답 (vLLM 로컬 연동) | [ ] | |
| 데이터 저장 권한 확인 | [ ] | |

## 5. 문제 해결 (Troubleshooting)
- **앱이 공백으로 뜰 때**: Edge WebView2 런타임 설치 여부 확인
- **분석 중 오류 발생**: `vcruntime140.dll` 등 필수 DLL 누락 여부 확인 (PyInstaller 빌드 시 포함 여부 재검토)
- **데이터 저장 실패**: 로그 파일(`%LOCALAPPDATA%\HandOverAI\app.log`) 확인
