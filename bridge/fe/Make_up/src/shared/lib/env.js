/**
 * 환경 판별 유틸리티
 *
 * exe 패키징 시 핵심 차이점:
 *   - 개발: Vite dev server (http://localhost:5173)
 *   - exe:  file:// 프로토콜로 정적 HTML 로드
 */

/** Vite 개발 서버에서 실행 중인지 */
export const isDev = import.meta.env.DEV

/** 프로덕션 빌드인지 (npm run build 결과물) */
export const isProd = import.meta.env.PROD

/** exe (file://) 환경인지 */
export const isFileProtocol = window.location.protocol === 'file:'

/** pywebview 내부에서 실행 중인지 */
export const isEmbedded = isFileProtocol || !!window.pywebview

/**
 * 개발 서버 URL (Python 측에서 이 주소를 로드)
 * pywebview 개발 모드: webview.create_window('앱', DEV_URL)
 */
export const DEV_URL = 'http://localhost:5173'
