import sys
from pathlib import Path
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.parser import parse_hwp_file


def debug_pdf_text():
    """PDF 텍스트 전체 확인 (디버깅용)"""
    
    print("=" * 50)
    print("PDF 텍스트 전체 확인")
    print("=" * 50)
    
    # PDF 찾기
    dummy_folder = "resources/dummy_hwp"
    
    for filename in os.listdir(dummy_folder):
        if filename.lower().endswith('.pdf'):
            pdf_file = os.path.join(dummy_folder, filename)
            break
    else:
        print("PDF 파일 없음")
        return
    
    print(f"\n📄 파일: {Path(pdf_file).name}")
    
    # 파싱
    result = parse_hwp_file(pdf_file)
    
    if result['success']:
        # 텍스트를 파일로 저장
        output_file = "pdf_extracted_text.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        print(f"✅ 텍스트를 {output_file}에 저장했습니다")
        print(f"텍스트 길이: {len(result['text'])}자")
        
        # 숫자 패턴 찾기 (금액일 가능성)
        import re
        
        # 콤마 포함 숫자 찾기
        numbers = re.findall(r'\d{1,3}(?:,\d{3})+', result['text'])
        print(f"\n발견된 콤마 포함 숫자: {len(numbers)}개")
        
        # 샘플 출력
        if numbers:
            print("샘플:")
            for num in numbers[:10]:
                print(f"  - {num}")
        
        # "원" 이 포함된 줄 찾기
        lines_with_won = [line for line in result['text'].split('\n') if '원' in line]
        print(f"\n'원'이 포함된 줄: {len(lines_with_won)}개")
        
        if lines_with_won:
            print("샘플:")
            for line in lines_with_won[:5]:
                print(f"  {line.strip()}")


if __name__ == "__main__":
    debug_pdf_text()