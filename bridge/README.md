# HandOverAI - Bridge

**PyWebView + React + Python** 데스크톱 애플리케이션

---

## 🚀 빠른 시작

### 개발 환경 테스트
```bash
# 1. 의존성 설치
uv sync

# 2. 테스트 실행
uv run python dev_test.py

# 3. 애플리케이션 실행
uv run python main.py
```

### 프로덕션 빌드
```bash
# 기본 빌드
handover.bat build

# React 포함 빌드
handover.bat build --with-react

# Clean 빌드
handover.bat build --clean

# 실행
cd dist\HandOverAI
HandOverAI.exe
```

---

## 📁 핵심 파일

- `main.py` - PyWebView 메인 애플리케이션
- `bridge_api.py` - Bridge API (BE/FE 연결)
- `schemas.py` - JSON 프로토콜 정의
- `adapter.py` - BE → FE 데이터 변환
- `build.bat` - 빌드 스크립트

---

## 📊 성능 목표

- ✅ 빌드 크기: 100MB 이하 (현재: ~25MB)
- ✅ 메모리 사용: 300MB 이하
- ✅ 초기 로딩: 5초 이내

---

## 🧪 테스트

### 개발 환경
```bash
handover.bat test
```

### 저사양 시뮬레이션 (VM 없이)
```bash
# 1. 빌드 생성
handover.bat build

# 2. 저사양 환경 시뮬레이션 실행
handover.bat low-spec
```

### 실제 저사양 PC 테스트
```bash
# 1. 빌드 + 압축
handover.bat prepare

# 2. USB로 다른 PC에 전송
# 3. 압축 해제 후 HandOverAI.exe 실행
```

자세한 내용: [LOW_SPEC_TEST.md](LOW_SPEC_TEST.md)

---

## 📚 문서

- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - 전체 구현 요약
- [LOW_SPEC_TEST.md](LOW_SPEC_TEST.md) - 저사양 테스트 가이드

---

## 🔧 문제 해결

### 404 에러
- **원인**: React 빌드 없음
- **해결**: 폴백 HTML 자동 사용 (기본 기능 테스트 가능)

### DLL 오류
- **해결**: `build.bat`이 자동으로 처리

---

**라이선스**: MIT  
**프로젝트**: 해커톤 - 공공기관 인수인계 자동화