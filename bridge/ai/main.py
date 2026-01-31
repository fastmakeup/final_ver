"""
공공기관 인수인계 시스템 - 클라이언트 (파일 업로드 + 분석 + 챗봇)
로컬 PC에서 실행 → RunPod 서버에 연결
"""

import requests
import os
import glob

# 상위 디렉토리(bridge)를 sys.path에 추가하여 config 접근
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# RunPod API 서버 URL
API_BASE_URL = config.BRIDGE_API_URL

# 로컬 문서 폴더 (기본값)
DEFAULT_DATA_DIR = config.DEFAULT_DATA_DIR


def check_server():
    """서버 연결 확인 (상세 진단 버전)"""
    try:
        # User-Agent 추가 및 SSL 검증 일시 해제(테스트용)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(f"{API_BASE_URL}/", timeout=10, headers=headers, verify=False)
        
        print(f"   [진단] 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ 서버 연결 성공!")
                print(f"   서버 상태: {data}")
                return True
            except ValueError:
                print("❌ 서버 응답이 JSON 형식이 아닙니다. (HTML 페이지일 수 있습니다)")
                return False
        else:
            print(f"❌ 서버 에러: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 연결 중 실제 오류 발생: {e}")
        return False


def upload_documents_from_path(data_dir):
    """지정된 폴더의 문서를 서버에 업로드"""
    print(f"� 업로드 대상 폴더: {data_dir}")
    
    # 지원 파일 형식
    extensions = ['*.pdf', '*.docx', '*.xlsx', '*.xls', '*.hwp', '*.hwpx', '*.txt', '*.md']
    files_to_upload = []
    
    for ext in extensions:
        files_to_upload.extend(glob.glob(os.path.join(data_dir, ext)))
    
    if not files_to_upload:
        print("⚠️ 업로드할 지원 문서가 폴더에 없습니다.")
        return False
    
    print(f"📂 발견된 파일: {len(files_to_upload)}개")
    
    files = []
    try:
        for file_path in files_to_upload:
            filename = os.path.basename(file_path)
            files.append(('files', (filename, open(file_path, 'rb'))))
            print(f"   + {filename}")
    
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=60)
        
        if response.status_code == 200:
            print("\n✅ 서버 업로드 및 저장 완료")
            return True
        else:
            print(f"❌ 업로드 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 업로드 오류 발생: {e}")
        return False
    finally:
        # 파일 핸들 안전하게 닫기
        for _, (_, f) in files:
            f.close()


def analyze_documents():
    """서버에서 문서 분석 요청"""
    print("\n📊 문서 분석 중... (시간이 걸릴 수 있습니다)")
    
    try:
        response = requests.post(f"{API_BASE_URL}/analyze", timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                data = result.get("result", {})
                print("\n📋 분석 결과 요약")
                print("-" * 40)
                print(f"   프로젝트: {data.get('name', 'N/A')}")
                print(f"   파일 수: {data.get('fileCount', 0)}개")
                print(f"   이슈: {len(data.get('summary', {}).get('issues', []))}개")
                
                if data.get('summary', {}).get('totalAmount'):
                    print(f"   총 금액: {data['summary']['totalAmount']:,}원")
                return True
        else:
            print(f"❌ 분석 실패: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 분석 오류: {e}")
    
    return False


def chat(question: str) -> str:
    """챗봇 질문"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"question": question},
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("answer", "응답 없음")
        else:
            return f"오류: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"연결 오류: {e}"


def main():
    print("\n" + "=" * 70)
    print("🏛️ HandOver AI - 통합 관리 클라이언트")
    print("=" * 70)
    print(f"🔗 서버 주소: {API_BASE_URL}")
    print("=" * 70)
    
    # 서버 연결 확인
    if not check_server():
        print("\n[오류] 서버에 연결할 수 없습니다. 서버 상태를 확인하세요.")
        return
    
    # 업로드 경로 선택
    current_dir = input(f"\n📁 업로드할 폴더 경로를 입력하세요 (기본: {DEFAULT_DATA_DIR}): ").strip()
    upload_dir = current_dir if current_dir else DEFAULT_DATA_DIR
    
    if not os.path.exists(upload_dir):
        print(f"[경고] {upload_dir} 경로가 존재하지 않습니다. 새로 생성합니다.")
        os.makedirs(upload_dir, exist_ok=True)

    # ===== Step 1: 파일 업로드 =====
    print("\n[Step 1] 문서 업로드 시작")
    print("-" * 40)
    
    # upload_documents 함수가 upload_dir를 인자로 받도록 수정해야 함 (아래에서 수정)
    success = upload_documents_from_path(upload_dir)
    if not success:
        print("[오류] 파일 업로드실패. 중단합니다.")
        return
    
    # ===== Step 2: 자동 분석 =====
    print("\n[Step 2] 문서 자동 분석 요청")
    print("-" * 40)
    analyze_documents()
    
    # ===== Step 3: 챗봇 모드 =====
    print("\n\n" + "=" * 70)
    print("💬 [Step 3] 챗봇 모드 (종료: quit)")
    print("=" * 70)
    
    while True:
        try:
            question = input("\n🙋 질문: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q', '종료']:
                print("\n👋 프로그램을 종료합니다.")
                break
            
            print("\n🤖 답변 생성 중...")
            answer = chat(question)
            print(f"\n💡 답변:\n{answer}")
            
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break


if __name__ == "__main__":
    main()
