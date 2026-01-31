
import os
import glob
from typing import List
import sys

# 경로 보정
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.schemas import BEParserOutput

def analyze_folder_interface(folder_path: str) -> List[BEParserOutput]:
    """
    폴더 내의 모든 문서를 분석하여 결과를 반환합니다.
    """
    # Lazy Import (초기 로딩 속도 향상)
    try:
        from be.core.parser import parse_hwp_file
        from be.core.processor import process_document
    except ImportError:
        # 경로가 안 잡혀있을 수 있으므로 다시 체크
        be_path = os.path.join(current_dir, 'be')
        if be_path not in sys.path:
            sys.path.insert(0, be_path)
        from be.core.parser import parse_hwp_file
        from be.core.processor import process_document
    print(f"[Core] 폴더 분석 시작: {folder_path}")
    
    results = []
    
    # 지원하는 파일 확장자
    extensions = ['*.hwp', '*.hwpx', '*.pdf', '*.txt']
    
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(folder_path, ext)))
        
    print(f"[Core] 발견된 파일: {len(files)}개")
    
    for file_path in files:
        try:
            print(f"[Core] 파일 파싱 중: {os.path.basename(file_path)}")
            
            # 1. 텍스트 추출 (Parser)
            parse_result = parse_hwp_file(file_path)
            
            if not parse_result['success']:
                print(f"[Core] 파싱 실패 ({os.path.basename(file_path)}): {parse_result['error']}")
                continue
                
            text = parse_result['text']
            
            # 2. 정보 추출 (Processor)
            processed_data = process_document(file_path, text)
            
            # 결과 저장
            result: BEParserOutput = {
                'filename': processed_data['filename'],
                'type': processed_data['type'],
                'dates': processed_data['dates'],
                'amounts': processed_data['amounts'],
                'parties': processed_data.get('parties', []),
                'keywords': processed_data.get('keywords', []),
                'raw_text': processed_data['raw_text']
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"[Core] 처리 중 에러 발생 ({os.path.basename(file_path)}): {str(e)}")
            continue
            
    print(f"[Core] 분석 완료: {len(results)}개 성공")
    return results

if __name__ == "__main__":
    # 테스트 코드
    print("=== Integration Test ===")
    test_dir = "./dummy_data"
    if os.path.exists(test_dir):
        results = analyze_folder_interface(test_dir)
        for res in results:
            print(f"- {res['filename']}: {res['type']} / {len(res['amounts'])} payments")
    else:
        print(f"테스트 폴더가 없습니다: {test_dir}")
