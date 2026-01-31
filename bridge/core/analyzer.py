import os
import glob
import sys
from typing import List
import config

# 상대 경로를 위한 절대 경로 보정
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.schemas import BEParserOutput

def analyze_folder_interface(folder_path: str) -> List[BEParserOutput]:
    """폴더 내의 문서를 분석하여 구조화된 데이터 반환"""
    try:
        from be.core.parser import parse_hwp_file
        from be.core.processor import process_document
    except ImportError:
        # be 패키지 직접 접근 실패 시 경로 보정
        be_path = os.path.join(root_dir, 'be')
        if be_path not in sys.path:
            sys.path.insert(0, be_path)
        from be.core.parser import parse_hwp_file
        from be.core.processor import process_document

    print(f"[Analyzer] 분석 시작: {folder_path}")
    results = []
    
    files = []
    for ext in config.SUPPORTED_EXTENSIONS:
        files.extend(glob.glob(os.path.join(folder_path, ext)))
        
    print(f"[Analyzer] 발견된 파일: {len(files)}개")
    
    for file_path in files:
        try:
            print(f"   + 파싱 중: {os.path.basename(file_path)}")
            # 1. 텍스트 추출
            parse_result = parse_hwp_file(file_path)
            if not parse_result['success']:
                print(f"   ! 실패: {parse_result.get('error', 'Unknown Error')}")
                continue
            
            # 2. 정보 추출
            processed_data = process_document(file_path, parse_result['text'])
            
            results.append({
                'filename': processed_data['filename'],
                'type': processed_data['type'],
                'dates': processed_data['dates'],
                'amounts': processed_data['amounts'],
                'parties': processed_data.get('parties', []),
                'keywords': processed_data.get('keywords', []),
                'raw_text': processed_data['raw_text']
            })
        except Exception as e:
            print(f"   ! 오류 ({os.path.basename(file_path)}): {e}")

    print(f"[Analyzer] 분석 완료: {len(results)}개 성공")
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_folder_interface(sys.argv[1])
