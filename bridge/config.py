import os
import sys

# --- API & 서버 설정 ---
# --- API & 서버 설정 ---
BRIDGE_API_URL = "https://yvfe7u20ltb89m-8888.proxy.runpod.net"
LLM_API_URL = "http://localhost:8000/v1"
API_KEY = "EMPTY"
MODEL_NAME = "mistralai/Mistral-Nemo-Instruct-2407"

# --- 경로 설정 ---
def get_app_data_path():
    if getattr(sys, 'frozen', False):
        # EXE 실행 시
        app_data = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'HandOverAI')
        if not os.path.exists(app_data):
            os.makedirs(app_data)
        return app_data
    # 개발 환경
    return os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = get_app_data_path()
CHROMA_DB_PATH = os.path.join(ROOT_DIR, "chroma_db_v3")
DEFAULT_DATA_DIR = os.path.join(ROOT_DIR, "my_data")

# 데이터 디렉토리 생성 보장
if not os.path.exists(DEFAULT_DATA_DIR):
    os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)

# --- 파싱 설정 ---
SUPPORTED_EXTENSIONS = ['*.hwp', '*.hwpx', '*.pdf', '*.txt', '*.docx', '*.xlsx', '*.md']

print(f"[Config] 설정 로드 완료 (ROOT: {ROOT_DIR})")
