# handover.bat 사용 가이드

## 문제 해결

### 문제 1: bash에서 실행 시 "command not found"

**증상**:
```bash
$ handover.bat build
bash: handover.bat: command not found
```

**원인**: bash 셸에서 `.bat` 파일을 직접 실행할 수 없음

**해결책**:
```bash
# PowerShell에서 실행
.\handover.bat build

# 또는 cmd에서 실행
handover.bat build
```

---

### 문제 2: bat 파일 더블클릭 시 창이 즉시 닫힘

**원인**: 명령어 인자 없이 실행되어 도움말만 표시하고 종료

**해결책**:

#### 방법 1: PowerShell/CMD에서 실행 (권장)
```powershell
# PowerShell 열기 (Win + X → Windows PowerShell)
cd c:\Users\SSAFY\Desktop\hackathon\bridge
.\handover.bat build
```

#### 방법 2: 바로가기 만들기
1. `handover.bat` 우클릭 → "바로가기 만들기"
2. 바로가기 우클릭 → "속성"
3. "대상" 필드 수정:
   ```
   C:\Windows\System32\cmd.exe /k "cd /d C:\Users\SSAFY\Desktop\hackathon\bridge && handover.bat build"
   ```
4. 바로가기 더블클릭하면 빌드 실행

#### 방법 3: 개별 명령어 bat 파일 생성
간단한 래퍼 스크립트 생성:

**build_quick.bat**:
```batch
@echo off
cd /d %~dp0
call handover.bat build
pause
```

---

## 올바른 사용법

### PowerShell에서 (권장)
```powershell
# 디렉토리 이동
cd c:\Users\SSAFY\Desktop\hackathon\bridge

# 빌드
.\handover.bat build

# 저사양 테스트
.\handover.bat low-spec

# 도움말
.\handover.bat help
```

### CMD에서
```cmd
cd c:\Users\SSAFY\Desktop\hackathon\bridge
handover.bat build
```

### Git Bash에서 (비권장)
```bash
# PowerShell로 전환
powershell

# 또는 cmd로 실행
cmd //c handover.bat build
```

---

## 모든 명령어

```bash
# 빌드
.\handover.bat build
.\handover.bat build --with-react
.\handover.bat build --clean

# VM 전송 준비
.\handover.bat prepare

# 개발 환경 테스트
.\handover.bat test

# 저사양 시뮬레이션
.\handover.bat low-spec

# 빌드 검증
.\handover.bat verify

# 도움말
.\handover.bat help
```
