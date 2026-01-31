# Frontend

## 기술 스택

| 분류 | 기술 |
|------|------|
| Framework | React 19 |
| Build Tool | Vite 6 |
| Styling | Tailwind CSS 3 |
| Language | JavaScript (ES6+) |
| Desktop 연동 | pywebview bridge |

## 설치 및 실행

```bash
cd Make_up

# 의존성 설치
npm install

# 개발 서버 실행 (localhost:5173)
npm run dev

# 프로덕션 빌드
npm run build
```

## 프로젝트 구조

```
fe/
├── Make_up/                        # Vite 프로젝트 루트
│   ├── index.html                  # 한글 lang, Pretendard 폰트
│   ├── vite.config.js              # base: './' (exe 필수), @/ 별칭
│   ├── tailwind.config.js          # 디자인 토큰
│   ├── postcss.config.js           # Tailwind + Autoprefixer
│   ├── package.json
│   ├── src/
│   │   ├── main.jsx                # 엔트리포인트
│   │   ├── index.css               # Tailwind 진입점
│   │   ├── App.jsx                 # 루트 컴포넌트
│   │   ├── App.css
│   │   ├── domains/                # 도메인(기능) 단위 코드
│   │   │   ├── analysis/           # 문서 분석
│   │   │   ├── timeline/           # 타임라인
│   │   │   ├── fileExplorer/       # 파일 탐색기
│   │   │   └── chat/               # AI 채팅
│   │   ├── shared/                 # 공유 코드
│   │   │   ├── components/         # 공통 UI (Button, Card 등)
│   │   │   ├── hooks/              # 공통 훅 (useApi, useDebounce 등)
│   │   │   ├── lib/
│   │   │   │   ├── bridge.js       # pywebview <-> React 통신
│   │   │   │   └── env.js          # 개발/exe 환경 판별
│   │   │   ├── utils/
│   │   │   │   └── cn.js           # Tailwind 클래스 병합
│   │   │   └── constants/
│   │   ├── layouts/                # 페이지 레이아웃
│   │   ├── pages/                  # 페이지 컴포넌트
│   │   └── api/                    # API 인프라, mock 데이터
│   └── dist/                       # 빌드 결과물 (gitignore)
└── README.md
```

## 주요 설정

| 파일 | 역할 |
|------|------|
| `vite.config.js` | `base: './'` (exe에서 file:// 로드 시 상대경로 필수), `@/` 별칭 |
| `postcss.config.js` | Tailwind + Autoprefixer 연결 |
| `bridge.js` | pywebview API 호출 래퍼 (`callPython()`) |
| `env.js` | 개발/exe 환경 판별 유틸 |

## pywebview 통신

```javascript
import { callPython } from '@/shared/lib/bridge';

// Python 측: class Api: def get_data(self, id): ...
const data = await callPython('get_data', 123);
```

## 개발 컨벤션

### 파일 네이밍

| 유형 | 규칙 | 예시 |
|------|------|------|
| 컴포넌트 | PascalCase | `TimelineItem.jsx` |
| 훅 | camelCase + use 접두사 | `useTimelineData.js` |
| 유틸 | camelCase | `dateUtils.js` |

### Import 경로

```javascript
'@/' → src/
```

### 컴포넌트 구조

```jsx
import { useState } from 'react';
import { cn } from '@/shared/utils/cn';

export default function ComponentName({ prop1, prop2 }) {
  const [state, setState] = useState();

  const handleClick = () => {};

  return (
    <div>{/* JSX */}</div>
  );
}
```
