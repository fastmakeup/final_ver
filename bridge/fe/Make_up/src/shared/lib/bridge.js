/**
 * pywebview ↔ React 통신 브릿지
 *
 * 사용법:
 *   import { callPython } from '@/shared/lib/bridge';
 *   const result = await callPython('get_user_data', { id: 1 });
 *
 * 작동 원리:
 *   - exe 모드: window.pywebview.api.메서드명() 으로 Python 함수 직접 호출
 *   - 개발 모드: window.pywebview가 없으므로 콘솔 로그 + mock 반환
 */

/**
 * pywebview API가 준비될 때까지 대기
 * pywebview는 window 로드 후 약간의 딜레이 후에 api 객체를 주입함
 */
function waitForPywebview(timeout = 5000) {
  return new Promise((resolve, reject) => {
    // 이미 있으면 바로 반환
    if (window.pywebview?.api) {
      resolve(window.pywebview.api);
      return;
    }

    // pywebview가 준비되면 발생하는 이벤트
    const onReady = () => {
      clearTimeout(timer);
      resolve(window.pywebview.api);
    };

    const timer = setTimeout(() => {
      window.removeEventListener('pywebviewready', onReady);
      reject(new Error('pywebview API 로드 타임아웃'));
    }, timeout);

    window.addEventListener('pywebviewready', onReady);
  });
}

/**
 * Python 백엔드 함수 호출
 * @param {string} method - Python 측 함수 이름
 * @param  {...any} args - 함수에 전달할 인자
 * @returns {Promise<any>} Python 함수의 반환값
 */
export async function callPython(method, ...args) {
  // exe 모드 (pywebview 존재)
  if (window.pywebview?.api) {
    const fn = window.pywebview.api[method];
    if (!fn) {
      throw new Error(`Python API에 '${method}' 메서드가 없습니다`);
    }
    try {
      return await fn(...args);
    } catch (err) {
      console.error(`[bridge] Python 호출 실패 — ${method}:`, err);
      throw err;
    }
  }

  // 개발 모드 (Vite dev server)
  console.warn(`[bridge] 개발 모드 - callPython('${method}', ${JSON.stringify(args)})`);
  return null;
}

/**
 * pywebview 환경 여부 확인
 */
export function isPywebview() {
  return !!window.pywebview?.api;
}

/**
 * 앱 초기화 시 pywebview 연결 대기
 * main.jsx에서 호출 권장
 */
export async function initBridge() {
  try {
    const api = await waitForPywebview();
    console.log('[bridge] pywebview 연결 완료, 사용 가능한 API:', Object.keys(api));
    return api;
  } catch {
    console.info('[bridge] pywebview 없음 → 개발 모드로 실행');
    return null;
  }
}
