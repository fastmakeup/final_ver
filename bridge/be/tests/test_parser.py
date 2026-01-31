import sys
from pathlib import Path
import re

# 프로젝트 루트(be 폴더)를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 모든 import를 여기서 한번에!
from core.parser import extract_text_from_hwp, parse_hwp_file, extract_text_from_txt
from core.processor import extract_dates, extract_amounts, process_document


def test_extract_text():
    """텍스트 추출 테스트"""
    
    test_file = "resources/dummy_hwp/01_기안.txt"
    
    print("=" * 50)
    print("텍스트 파서 테스트 시작")
    print("=" * 50)
    
    try:
        # 상단에서 이미 import 했으니 바로 사용!
        text = extract_text_from_txt(test_file)
        
        print(f"\n✅ 텍스트 추출 성공!")
        print(f"\n추출된 텍스트 ({len(text)}자):")
        print("-" * 50)
        print(text)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()


def test_parse_hwp_file():
    """parse_hwp_file 함수 테스트"""
    
    test_file = "resources/dummy_hwp/01_기안.hwp"
    
    print("\n" + "=" * 50)
    print("parse_hwp_file 테스트")
    print("=" * 50)
    
    result = parse_hwp_file(test_file)
    
    print(f"\n결과:")
    print(f"  파일명: {result['filename']}")
    print(f"  성공: {result['success']}")
    print(f"  에러: {result['error']}")
    print(f"  텍스트 길이: {len(result['text'])}자")


def test_processor():
    """processor 함수들 테스트"""
    
    print("\n" + "=" * 50)
    print("Processor 테스트")
    print("=" * 50)
    
    test_text = """
    벚꽃축제 기본계획 수립
    
    일시: 2024.03.01
    예산: 금오천만원
    담당자: 홍길동
    
    본 기안은 2024년 벚꽃축제 개최를 위한 기본계획입니다.
    총 예산은 금 50,000,000원이며, 2024년 4월 10일까지 완료 예정입니다.
    """
    
    # 날짜 추출 테스트
    dates = extract_dates(test_text)
    print(f"\n📅 추출된 날짜: {dates}")
    
    # 금액 추출 테스트
    amounts = extract_amounts(test_text)
    print(f"\n💰 추출된 금액:")
    for amt in amounts:
        print(f"  - {amt['text']} → {amt['amount']:,}원")
    
    # 전체 처리 테스트
    result = process_document("resources/dummy_hwp/01_기안.txt", test_text)
    print(f"\n📄 문서 처리 결과:")
    print(f"  파일명: {result['filename']}")
    print(f"  타입: {result['type']}")
    print(f"  날짜: {result['dates']}")
    print(f"  금액 개수: {len(result['amounts'])}")

def test_data_types():
    """데이터 타입 확인 테스트"""
    
    print("\n" + "=" * 50)
    print("데이터 타입 확인")
    print("=" * 50)
    
    test_text = """
    일시: 2024.03.01
    예산: 금오천만원
    총 예산은 금 50,000,000원이며, 2024년 4월 10일까지 완료 예정입니다.
    """
    
    # 1. 날짜 추출
    dates = extract_dates(test_text)
    print(f"\n📅 dates 변수:")
    print(f"  타입: {type(dates)}")
    print(f"  값: {dates}")
    print(f"  첫 번째 요소 타입: {type(dates[0]) if dates else 'N/A'}")
    
    # 2. 금액 추출
    amounts = extract_amounts(test_text)
    print(f"\n💰 amounts 변수:")
    print(f"  타입: {type(amounts)}")
    print(f"  값: {amounts}")
    if amounts:
        print(f"  첫 번째 요소 타입: {type(amounts[0])}")
        print(f"  첫 번째 요소 구조:")
        print(f"    - text: {amounts[0]['text']} (타입: {type(amounts[0]['text'])})")
        print(f"    - amount: {amounts[0]['amount']} (타입: {type(amounts[0]['amount'])})")
    
    # 3. 전체 문서 처리
    result = process_document("test.hwp", test_text)
    print(f"\n📄 result 변수:")
    print(f"  타입: {type(result)}")
    print(f"  키 목록: {list(result.keys())}")
    print(f"  각 키별 타입:")
    for key, value in result.items():
        if key == "raw_text":
            print(f"    - {key}: {type(value)} (길이: {len(value)})")
        else:
            print(f"    - {key}: {type(value)} = {value}")


def test_real_hwp_files():
    """실제 HWP 파일들 테스트"""
    
    print("\n" + "=" * 50)
    print("실제 HWP 파일 테스트")
    print("=" * 50)
    
    # 폴더 안의 모든 HWP/HWPX 파일 자동으로 찾기!
    import os
    
    dummy_folder = "resources/dummy_hwp"
    test_files = []
    
    # 폴더 안의 모든 파일 찾기
    for filename in os.listdir(dummy_folder):
        # .hwp 또는 .hwpx 파일만
        if filename.endswith('.hwp') or filename.endswith('.hwpx'):
            # .txt는 제외
            if not filename.endswith('.txt'):
                test_files.append(os.path.join(dummy_folder, filename))
    
    print(f"\n🔍 찾은 파일 개수: {len(test_files)}개")
    
    for file_path in test_files:
        print(f"\n{'='*50}")
        print(f"📄 파일: {Path(file_path).name}")
        print('='*50)
        
        # 1. 파일 존재 확인
        if not Path(file_path).exists():
            print(f"❌ 파일 없음: {file_path}")
            continue
        
        # 2. 텍스트 추출
        try:
            result = parse_hwp_file(file_path)
            
            if result['success']:
                print(f"✅ 파싱 성공!")
                print(f"  텍스트 길이: {len(result['text'])}자")
                
                # 3. 날짜/금액 추출
                dates = extract_dates(result['text'])
                amounts = extract_amounts(result['text'])
                
                print(f"\n📅 추출된 날짜 ({len(dates)}개):")
                for date in dates[:5]:  # 최대 5개만 출력
                    print(f"  - {date}")
                if len(dates) > 5:
                    print(f"  ... 외 {len(dates)-5}개")
                
                print(f"\n💰 추출된 금액 ({len(amounts)}개):")
                for amt in amounts[:5]:  # 최대 5개만 출력
                    print(f"  - {amt['text']} → {amt['amount']:,}원")
                if len(amounts) > 5:
                    print(f"  ... 외 {len(amounts)-5}개")
                
                # 4. 텍스트 미리보기 (처음 300자)
                print(f"\n📝 텍스트 미리보기:")
                print("-" * 50)
                preview = result['text'][:300].replace('\n', ' ').replace('\r', '')
                print(preview + "...")
                print("-" * 50)
                
            else:
                print(f"❌ 파싱 실패: {result['error']}")
                
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            import traceback
            traceback.print_exc()

def test_hwpx_structure():
    """HWPX 파일 내부 구조 확인 (디버깅용)"""
    
    print("\n" + "=" * 50)
    print("HWPX 파일 구조 분석")
    print("=" * 50)
    
    import zipfile
    
    hwpx_files = [
        "resources/dummy_hwp/★유엔참전용사 등 재방한 초청사업 운영지침(260130개정).hwpx",
    ]
    
    for hwpx_file in hwpx_files:
        if not Path(hwpx_file).exists():
            # 폴더 내 첫 번째 hwpx 찾기
            for f in Path("resources/dummy_hwp").glob("*.hwpx"):
                hwpx_file = str(f)
                break
        
        if not Path(hwpx_file).exists():
            print("❌ HWPX 파일을 찾을 수 없습니다")
            return
        
        print(f"\n📄 분석 중: {Path(hwpx_file).name}")
        
        try:
            with zipfile.ZipFile(hwpx_file, 'r') as zf:
                all_files = zf.namelist()
                
                print(f"\n📦 ZIP 내부 파일 목록 ({len(all_files)}개):")
                for i, name in enumerate(all_files[:20], 1):  # 최대 20개만
                    print(f"  {i}. {name}")
                if len(all_files) > 20:
                    print(f"  ... 외 {len(all_files)-20}개")
                
                # section 파일 찾기
                section_files = [f for f in all_files if 'section' in f.lower() and f.endswith('.xml')]
                
                if section_files:
                    print(f"\n📝 Section XML 파일:")
                    for sf in section_files[:3]:  # 처음 3개만
                        print(f"  - {sf}")
                        
                        # 첫 번째 파일 내용 미리보기
                        with zf.open(sf) as f:
                            content = f.read()
                            text = content.decode('utf-8', errors='ignore')
                            
                            # 사용된 태그들 찾기
                            tags = re.findall(r'<([a-zA-Z:]+)[^>]*>', text)
                            unique_tags = list(set(tags))[:20]
                            
                            print(f"\n  사용된 XML 태그들:")
                            print(f"    {', '.join(unique_tags)}")
                            
                            # 텍스트 샘플
                            preview = text[:500]
                            print(f"\n  XML 내용 미리보기:")
                            print(f"    {preview}...")
                            
                        break  # 첫 번째 파일만 분석
                else:
                    print("❌ section XML 파일을 찾을 수 없습니다")
                    
        except Exception as e:
            print(f"❌ 에러: {e}")
            import traceback
            traceback.print_exc()

def test_amount_extraction():
    """표 안의 금액 추출 테스트"""
    
    print("\n" + "=" * 50)
    print("표 형식 금액 추출 테스트")
    print("=" * 50)
    
    # 실제 표에 있는 형식들
    test_text = """
    2,421,586원
    2,321,050원
    80,000원×2명×9일
    1,440,000원
    금 50,000,000원
    금오천만원
    5천만원
    20,377,728원
    17,129,179원
    6,294,179원
    """
    
    amounts = extract_amounts(test_text)
    
    print(f"\n💰 추출된 금액 ({len(amounts)}개):")
    for amt in sorted(amounts, key=lambda x: x['amount'], reverse=True):  # 큰 금액부터
        print(f"  - {amt['text']:20s} → {amt['amount']:>12,}원")


if __name__ == "__main__":
    # 현재 작업 디렉토리 출력 (디버깅용)
    print(f"현재 작업 디렉토리: {Path.cwd()}")
    print(f"프로젝트 루트: {project_root}\n")
    
    # 모든 테스트 실행
    test_extract_text()
    test_parse_hwp_file()
    test_processor()
    test_data_types()
    test_real_hwp_files()
    test_hwpx_structure()
    test_amount_extraction()
    