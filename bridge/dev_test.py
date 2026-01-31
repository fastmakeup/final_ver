"""
개발 테스트 스크립트
Bridge API 독립 실행 테스트
"""
import sys
import os

# 현재 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.dirname(__file__))

from schemas import (
    Document, 
    create_dummy_documents, 
    validate_document_list,
    serialize_documents,
    deserialize_documents
)
from bridge_api import BridgeAPI


def test_schemas():
    """JSON 프로토콜 테스트"""
    print("=" * 60)
    print("1. JSON 프로토콜 테스트")
    print("=" * 60)
    
    # 더미 데이터 생성
    docs = create_dummy_documents()
    print(f"[OK] 더미 문서 생성: {len(docs)}개")
    
    # 직렬화
    json_str = serialize_documents(docs)
    print(f"[OK] 직렬화 성공: {len(json_str)} bytes")
    
    # 검증
    doc_dicts = [doc.to_dict() for doc in docs]
    is_valid = validate_document_list(doc_dicts)
    print(f"[OK] 검증 결과: {'통과' if is_valid else '실패'}")
    
    # 역직렬화
    restored_docs = deserialize_documents(json_str)
    print(f"[OK] 역직렬화 성공: {len(restored_docs)}개 문서 복원")
    
    # 데이터 무결성 확인
    assert len(docs) == len(restored_docs), "문서 개수 불일치"
    assert docs[0].title == restored_docs[0].title, "데이터 불일치"
    print("[OK] 데이터 무결성 확인 완료\n")


def test_bridge_api():
    """Bridge API 테스트"""
    print("=" * 60)
    print("2. Bridge API 테스트")
    print("=" * 60)
    
    api = BridgeAPI()
    
    # Ping 테스트
    print("\n[테스트] Ping")
    result = api.ping()
    assert result['status'] == 'ok', "Ping 실패"
    print(f"[OK] Ping 성공: {result['message']}")
    
    # 폴더 분석 테스트
    print("\n[테스트] 폴더 분석")
    result = api.analyze_folder("./dummy_data")
    assert isinstance(result, list), "결과가 리스트가 아님"
    assert len(result) > 0, "결과가 비어있음"
    print(f"[OK] 폴더 분석 성공: {len(result)}개 문서")
    print(f"   첫 번째 문서: {result[0]['title']}")
    
    # 캐시 테스트
    print("\n[테스트] 캐시")
    cache_status = api.get_cache_status()
    assert cache_status['cache_count'] > 0, "캐시가 비어있음"
    print(f"[OK] 캐시 확인: {cache_status['cache_count']}개 항목")
    
    # 캐시 재사용 테스트
    print("\n[테스트] 캐시 재사용")
    result2 = api.analyze_folder("./dummy_data")
    assert result == result2, "캐시 데이터 불일치"
    print("[OK] 캐시 재사용 성공")
    
    # AI 검색 테스트
    print("\n[테스트] AI 검색")
    search_result = api.search_documents("변경계약서")
    assert 'query' in search_result, "검색 결과 형식 오류"
    assert 'answer' in search_result, "검색 결과 형식 오류"
    print(f"[OK] AI 검색 성공")
    print(f"   쿼리: {search_result['query']}")
    print(f"   응답: {search_result['answer'][:50]}...")
    
    # 캐시 초기화 테스트
    print("\n[테스트] 캐시 초기화")
    clear_result = api.clear_cache()
    assert clear_result['cleared'] > 0, "캐시 초기화 실패"
    print(f"[OK] 캐시 초기화 성공: {clear_result['cleared']}개 항목 삭제")
    
    cache_status = api.get_cache_status()
    assert cache_status['cache_count'] == 0, "캐시가 완전히 삭제되지 않음"
    print("[OK] 캐시 완전 삭제 확인\n")


def test_be_integration():
    """BE 모듈 통합 테스트 (나중에 구현)"""
    print("=" * 60)
    print("3. BE 모듈 통합 테스트")
    print("=" * 60)
    print("[SKIP] BE 모듈 구현 대기 중...\n")


def test_ai_integration():
    """AI 모듈 통합 테스트 (나중에 구현)"""
    print("=" * 60)
    print("4. AI 모듈 통합 테스트")
    print("=" * 60)
    print("[SKIP] AI 모듈 구현 대기 중...\n")


def main():
    """모든 테스트 실행"""
    print("\n")
    print("=" * 60)
    print(" " * 15 + "Bridge 통합 테스트")
    print("=" * 60)
    print()
    
    try:
        test_schemas()
        test_bridge_api()
        test_be_integration()
        test_ai_integration()
        
        print("=" * 60)
        print("[SUCCESS] 모든 테스트 통과!")
        print("=" * 60)
        print()
        print("다음 단계:")
        print("  1. BE 팀: be/main.py에 analyze_folder_interface() 함수 구현")
        print("  2. AI 팀: ai/local_client.py에 search_interface() 함수 구현")
        print("  3. FE 팀: React에서 usePyWebView 훅 사용하여 UI 연결")
        print("  4. 통합: uv run python main.py 실행하여 PyWebView 테스트")
        print()
        
    except AssertionError as e:
        print(f"\n[FAIL] 테스트 실패: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 예상치 못한 오류: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
