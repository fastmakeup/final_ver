"""
PyWebView 메인 애플리케이션
React + Python 통합
"""
import webview
import os
import sys
from bridge_api import BridgeAPI


def get_resource_path(relative_path):
    """
    리소스 파일 경로 가져오기
    개발 모드와 PyInstaller 빌드 모드 모두 지원
    """
    try:
        # PyInstaller로 빌드된 경우
        base_path = sys._MEIPASS
    except AttributeError:
        # 개발 모드
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, relative_path)


def main():
    """메인 애플리케이션"""
    
    # Splash Screen 관련 로직 제거 (사용자 요청: FE 로딩 화면으로 대체)
    # 즉시 윈도우를 띄우고 React에서 로딩을 처리하도록 변경
    api = BridgeAPI()
    
    # React 빌드 파일 경로 결정
    # 개발 모드: fe/Make_up/dist/index.html
    # 프로덕션: bridge_build/index.html (빌드 시 복사됨)
    
    dev_build_path = os.path.join(
        os.path.dirname(__file__), 
        'fe', 'Make_up', 'dist', 'index.html'
    )
    prod_build_path = get_resource_path('bridge_build/index.html')
    
    # 개발/프로덕션 모드 자동 감지
    frozen = getattr(sys, 'frozen', False)
    html_path = None
    mode = "폴백"
    
    if frozen:
        # EXE 모드: 무조건 내부 리소스 사용
        html_path = prod_build_path
        mode = "프로덕션(EXE)"
    else:
        # 개발 모드: 로컬 파일 우선
        if os.path.exists(dev_build_path):
            html_path = dev_build_path
            mode = "개발(Local dist)"
        elif os.path.exists(prod_build_path):
            html_path = prod_build_path
            mode = "개발(Bridge build)"
    
    print(f"[Bridge] 모드: {mode}")
    if html_path:
        print(f"[Bridge] HTML 경로: {html_path}")
    
    # 폴백 HTML (React 빌드가 없을 때)
    fallback_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>HandOver AI - 테스트 모드</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                width: 100%;
                max-width: 800px;
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                padding: 3rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                margin: 0 0 0.5rem 0;
                font-size: 2.5rem;
            }
            .subtitle {
                margin-bottom: 2rem;
                opacity: 0.9;
                font-size: 1.1rem;
            }
            .warning {
                background: rgba(255, 193, 7, 0.2);
                border: 2px solid rgba(255, 193, 7, 0.5);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
            .button-group {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }
            button {
                background: white;
                color: #667eea;
                border: none;
                padding: 1rem 1.5rem;
                font-size: 1rem;
                border-radius: 10px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
            button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            #result {
                margin-top: 2rem;
                padding: 1.5rem;
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                max-height: 400px;
                overflow-y: auto;
                text-align: left;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
                line-height: 1.5;
            }
            #result:empty {
                display: none;
            }
            .success { color: #4caf50; }
            .error { color: #f44336; }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤝 HandOver AI</h1>
            <p class="subtitle">Bridge API 테스트 모드</p>
            
            <div class="warning">
                ⚠️ React 빌드를 찾을 수 없습니다. 테스트 모드로 실행 중입니다.
            </div>
            
            <div class="button-group">
                <button onclick="testPing()">연결 테스트</button>
                <button onclick="testAnalyze()">폴더 분석</button>
                <button onclick="testSearch()">AI 검색</button>
                <button onclick="testCache()">캐시 상태</button>
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            const resultDiv = document.getElementById('result');
            let isProcessing = false;
            
            function showResult(title, data, isError = false) {
                resultDiv.style.display = 'block';
                const className = isError ? 'error' : 'success';
                resultDiv.innerHTML = `<div class="${className}"><strong>${title}</strong></div><pre>${JSON.stringify(data, null, 2)}</pre>`;
            }
            
            function setLoading(loading) {
                isProcessing = loading;
                document.querySelectorAll('button').forEach(btn => {
                    btn.disabled = loading;
                });
            }
            
            async function testPing() {
                try {
                    setLoading(true);
                    const result = await pywebview.api.ping();
                    showResult('✅ Ping 성공', result);
                } catch (error) {
                    showResult('❌ Ping 실패', { error: error.toString() }, true);
                } finally {
                    setLoading(false);
                }
            }
            
            async function testAnalyze() {
                try {
                    setLoading(true);
                    resultDiv.innerHTML = '<strong>분석 중...</strong>';
                    resultDiv.style.display = 'block';
                    
                    const result = await pywebview.api.analyze_folder('./dummy_data');
                    
                    if (result && result[0] && result[0].error) {
                        showResult('❌ 분석 실패', result[0], true);
                    } else {
                        showResult(`✅ 폴더 분석 성공 (${result.length}개 문서)`, result);
                    }
                } catch (error) {
                    showResult('❌ 분석 실패', { error: error.toString() }, true);
                } finally {
                    setLoading(false);
                }
            }
            
            async function testSearch() {
                try {
                    setLoading(true);
                    const result = await pywebview.api.search_documents('변경계약서');
                    
                    if (result.error) {
                        showResult('❌ 검색 실패', result, true);
                    } else {
                        showResult('✅ AI 검색 성공', result);
                    }
                } catch (error) {
                    showResult('❌ 검색 실패', { error: error.toString() }, true);
                } finally {
                    setLoading(false);
                }
            }
            
            async function testCache() {
                try {
                    setLoading(true);
                    const result = await pywebview.api.get_cache_status();
                    showResult('✅ 캐시 상태', result);
                } catch (error) {
                    showResult('❌ 캐시 조회 실패', { error: error.toString() }, true);
                } finally {
                    setLoading(false);
                }
            }
            
            // 초기 연결 테스트
            window.addEventListener('pywebviewready', function() {
                console.log('PyWebView API ready');
                testPing();
            });
        </script>
    </body>
    </html>
    """
    
    # PyWebView 윈도우 생성
    if html_path:
        # 파일 경로가 있으면 url로 로드
        window = webview.create_window(
            title='HandOver AI - 인수인계 도우미',
            url=html_path,
            js_api=api,
            width=1200,
            height=800,
            resizable=True,
            background_color='#FFFFFF'
        )
    else:
        # 폴백 HTML을 html 파라미터로 전달
        window = webview.create_window(
            title='HandOver AI - 인수인계 도우미',
            html=fallback_html,
            js_api=api,
            width=1200,
            height=800,
            resizable=True,
            background_color='#FFFFFF'
        )
    
    # API에 window 객체 전달 (비동기 콜백용)
    # 반드시 private 변수(_window)에 저장해야 함. public 변수면 pywebview가 직렬화 시도함.
    api._window = window

    print("[Bridge] PyWebView 윈도우 생성 완료")
    print("[Bridge] 애플리케이션 시작...")
    
    # 애플리케이션 실행
    webview.start(debug=True)  # 진단을 위해 debug=True 활성화


if __name__ == '__main__':
    main()
