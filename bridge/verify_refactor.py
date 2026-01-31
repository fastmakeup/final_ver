import os
import time
import sys
from bridge_api import BridgeAPI

def verify():
    # 1. Setup Test Data
    test_dir = os.path.abspath("test_data_api_check")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    with open(os.path.join(test_dir, "test_doc.txt"), "w", encoding="utf-8") as f:
        f.write("이 문서는 브릿지 API 테스트를 위한 문서입니다. 인수인계 시스템이 잘 작동하는지 확인합니다.")

    print(f"Creating BridgeAPI instance...")
    api = BridgeAPI()

    # 2. Test Ping
    print("\n[Test] Ping")
    print(api.ping())

    # 3. Test Analyze Folder
    print(f"\n[Test] Analyze Folder: {test_dir}")
    result = api.analyze_folder(test_dir)
    print(f"Analyze Result (Immediate): {result}")
    
    # Wait for background thread (Upload + Analyze)
    print("Waiting for background upload/analyze to complete (10s)...")
    time.sleep(10)

    # 4. Test Search/Chat
    print("\n[Test] Search Documents")
    query = "이 문서의 내용은 무엇인가요?"
    chat_result = api.search_documents(query)
    print(f"Chat Result: {chat_result}")

    # Cleanup
    try:
        os.remove(os.path.join(test_dir, "test_doc.txt"))
        os.rmdir(test_dir)
    except:
        pass

if __name__ == "__main__":
    verify()
