import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.rules import DocumentValidator


def test_basic_validation():
    """기본 검증 테스트 - 정상 케이스"""
    
    print("=" * 50)
    print("Rule Engine 기본 테스트 (정상)")
    print("=" * 50)
    
    # 정상 케이스
    docs = [
        {
            "filename": "01_기안.hwp",
            "type": "기안",
            "dates": ["2024.03.01"],
            "amounts": [{"text": "50,000,000원", "amount": 50000000}],
            "raw_text": "..."
        },
        {
            "filename": "02_계약서.hwp",
            "type": "계약서",
            "dates": ["2024.03.05"],
            "amounts": [{"text": "50,000,000원", "amount": 50000000}],
            "raw_text": "..."
        }
    ]
    
    validator = DocumentValidator(docs)
    result = validator.validate_all()
    
    print(f"\n{result['summary']}")
    print(f"상태: {result['status']}")
    print(f"경고: {len(result['warnings'])}개")
    print(f"오류: {len(result['errors'])}개")


def test_amount_mismatch():
    """금액 불일치 테스트"""
    
    print("\n" + "=" * 50)
    print("금액 불일치 테스트")
    print("=" * 50)
    
    docs = [
        {
            "filename": "01_기안.hwp",
            "type": "기안",
            "dates": ["2024.03.01"],
            "amounts": [{"text": "50,000,000원", "amount": 50000000}],
            "raw_text": "..."
        },
        {
            "filename": "02_계약서.hwp",
            "type": "계약서",
            "dates": ["2024.03.05"],
            "amounts": [{"text": "30,000,000원", "amount": 30000000}],  # 금액 다름!
            "raw_text": "..."
        }
    ]
    
    validator = DocumentValidator(docs)
    result = validator.validate_all()
    
    print(f"\n{result['summary']}")
    print(f"상태: {result['status']}")
    
    for error in result['errors']:
        print(f"❌ {error['message']}")


def test_missing_contract():
    """계약서 누락 테스트"""
    
    print("\n" + "=" * 50)
    print("계약서 누락 테스트")
    print("=" * 50)
    
    docs = [
        {
            "filename": "01_기안.hwp",
            "type": "기안",
            "dates": ["2024.03.01"],
            "amounts": [{"text": "50,000,000원", "amount": 50000000}],
            "raw_text": "..."
        }
        # 계약서 없음!
    ]
    
    validator = DocumentValidator(docs)
    result = validator.validate_all()
    
    print(f"\n{result['summary']}")
    print(f"상태: {result['status']}")
    
    for warning in result['warnings']:
        print(f"⚠️ {warning['message']}")


if __name__ == "__main__":
    print(f"현재 작업 디렉토리: {Path.cwd()}\n")
    
    test_basic_validation()
    test_amount_mismatch()
    test_missing_contract()