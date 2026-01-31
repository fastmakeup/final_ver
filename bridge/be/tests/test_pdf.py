import sys
from pathlib import Path
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.parser import parse_hwp_file
from core.processor import extract_dates, extract_amounts


def test_pdf():
    """PDF 파일 테스트"""
    
    print("=" * 50)
    print("PDF 파일 테스트")
    print("=" * 50)
    
    # 폴더에서 PDF 파일 자동 찾기
    dummy_folder = "resources/dummy_hwp"
    
    pdf_files = []
    for filename in os.listdir(dummy_folder):
        if filename.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(dummy_folder, filename))
    
    if not pdf_files:
        print("⏭️  PDF 파일 없음 - 테스트 스킵")
        return
    
    # 첫 번째 PDF 파일 테스트
    pdf_file = pdf_files[0]
    print(f"\n📄 테스트 파일: {Path(pdf_file).name}")
    
    # 파싱
    result = parse_hwp_file(pdf_file)
    
    if result['success']:
        print(f"✅ PDF 파싱 성공!")
        print(f"  텍스트 길이: {len(result['text'])}자")
        
        # 날짜/금액 추출
        dates = extract_dates(result['text'])
        amounts = extract_amounts(result['text'])
        
        print(f"\n📅 추출된 날짜: {len(dates)}개")
        for date in dates[:5]:
            print(f"  - {date}")
        if len(dates) > 5:
            print(f"  ... 외 {len(dates)-5}개")
        
        print(f"\n💰 추출된 금액: {len(amounts)}개")
        for amt in amounts[:5]:
            print(f"  - {amt['text']} → {amt['amount']:,}원")
        if len(amounts) > 5:
            print(f"  ... 외 {len(amounts)-5}개")
        
        # 미리보기
        print(f"\n📝 텍스트 미리보기 (처음 500자):")
        print("-" * 50)
        preview = result['text'][:500].replace('\n', ' ')
        print(preview + "...")
        print("-" * 50)
    else:
        print(f"❌ 실패: {result['error']}")


if __name__ == "__main__":
    test_pdf()