"""
어댑터 레이어: BE 파서 출력을 FE JSON 프로토콜로 변환
"""
from typing import List, Optional
from schemas import BEParserOutput, DocumentResponse, AmountInfo


def select_primary_date(dates: List[str]) -> str:
    """
    여러 날짜 중 대표 날짜 선택
    
    전략:
    1. 가장 이른 날짜 선택 (기안일 가능성 높음)
    2. 날짜가 없으면 "날짜 없음" 반환
    
    Args:
        dates: 날짜 문자열 리스트 (예: ['2024.04.10', '2024.03.01'])
        
    Returns:
        대표 날짜 문자열
    """
    if not dates:
        return "날짜 없음"
    
    # 날짜 정렬 (문자열 정렬로도 YYYY.MM.DD 형식은 정확함)
    sorted_dates = sorted(dates)
    return sorted_dates[0]


def select_primary_amount(amounts: List[AmountInfo]) -> int:
    """
    여러 금액 중 대표 금액 선택
    
    전략:
    1. 가장 큰 금액 선택 (주요 예산일 가능성 높음)
    2. 금액이 없으면 0 반환
    
    Args:
        amounts: 금액 정보 리스트
        
    Returns:
        대표 금액 (정수)
    """
    if not amounts:
        return 0
    
    # 가장 큰 금액 선택
    max_amount = max(amounts, key=lambda x: x['amount'])
    return max_amount['amount']


def extract_title(raw_text: str, max_length: int = 50) -> str:
    """
    원본 텍스트에서 제목 추출
    
    전략:
    1. 첫 번째 줄을 제목으로 사용
    2. 빈 줄이면 두 번째 줄 시도
    3. max_length로 자르기
    
    Args:
        raw_text: 원본 텍스트
        max_length: 최대 길이
        
    Returns:
        제목 문자열
    """
    if not raw_text:
        return "제목 없음"
    
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    if not lines:
        return "제목 없음"
    
    title = lines[0][:max_length]
    return title


def detect_amount_conflict(amounts: List[AmountInfo]) -> bool:
    """
    금액 충돌 감지
    
    같은 문서에 서로 다른 금액이 있으면 True
    
    Args:
        amounts: 금액 정보 리스트
        
    Returns:
        충돌 여부
    """
    if len(amounts) <= 1:
        return False
    
    # 고유한 금액 개수 확인
    unique_amounts = set(a['amount'] for a in amounts)
    return len(unique_amounts) > 1


def generate_warning_message(amounts: List[AmountInfo]) -> str:
    """
    금액 충돌 시 경고 메시지 생성
    
    Args:
        amounts: 금액 정보 리스트
        
    Returns:
        경고 메시지
    """
    if not detect_amount_conflict(amounts):
        return ""
    
    unique_amounts = list(set(a['amount'] for a in amounts))
    amount_strs = [f"{amt:,}원" for amt in sorted(unique_amounts, reverse=True)]
    
    return f"[WARNING] 문서 내 금액 불일치 ({' vs '.join(amount_strs)})"


def infer_document_type(filename: str, raw_text: str, be_type: str) -> str:
    """
    문서 타입 추론 (BE가 '기타'로 분류한 경우 재추론)
    
    전략:
    1. BE 결과 우선 사용
    2. BE가 '기타'인 경우에만 재추론
    3. 파일명 패턴 확인
    4. 텍스트 키워드 확인
    
    Args:
        filename: 파일명
        raw_text: 원본 텍스트
        be_type: BE가 분류한 타입
        
    Returns:
        추론된 문서 타입
    """
    # BE 결과가 '기타'가 아니면 그대로 사용
    if be_type != '기타':
        return be_type
    
    # 파일명 패턴 확인
    filename_lower = filename.lower()
    if '기안' in filename_lower:
        return '기안'
    if '계약' in filename_lower:
        return '계약'
    if '지출' in filename_lower:
        return '지출'
    if '변경' in filename_lower:
        return '변경'
    
    # 텍스트 키워드 확인
    text_lower = raw_text.lower()
    if '계약서' in text_lower or '용역계약' in text_lower:
        return '계약'
    if '지출' in text_lower or '예산집행' in text_lower:
        return '지출'
    if '설계변경' in text_lower or '계약변경' in text_lower:
        return '변경'
    if '기안' in text_lower:
        return '기안'
    
    # 추론 실패 시 '기타' 유지
    return '기타'


def adapt_be_to_fe(be_data: BEParserOutput, file_index: int) -> DocumentResponse:
    """
    BE 파서 출력을 FE JSON 프로토콜로 변환
    
    핵심 변환 로직:
    - dates 리스트 → date (가장 이른 날짜)
    - amounts 리스트 → amount (가장 큰 금액)
    - raw_text → title (첫 줄)
    - filename → id (자동 생성)
    - 금액 충돌 감지 → status, message
    
    Args:
        be_data: BE 파서 출력
        file_index: 파일 인덱스 (ID 생성용)
        
    Returns:
        FE용 DocumentResponse
    """
    # 기본 정보
    filename = be_data['filename']
    doc_id = f"doc_{file_index:02d}"
    
    # 날짜 선택
    primary_date = select_primary_date(be_data['dates'])
    
    # 금액 선택
    primary_amount = select_primary_amount(be_data['amounts'])
    
    # 제목 추출
    title = extract_title(be_data['raw_text'])
    
    # 문서 타입 추론
    doc_type = infer_document_type(filename, be_data['raw_text'], be_data['type'])
    
    # 금액 충돌 감지
    has_conflict = detect_amount_conflict(be_data['amounts'])
    warning_msg = generate_warning_message(be_data['amounts']) if has_conflict else ""
    
    return {
        'id': doc_id,
        'name': filename,
        'date': primary_date,
        'all_dates': be_data['dates'],
        'docType': doc_type,
        'summary': title,
        'amount': primary_amount,
        'all_amounts': be_data['amounts'],
        'status': 'warning' if has_conflict else 'normal',
        'message': warning_msg,
        'raw_text': be_data['raw_text'],
        'children': None
    }


def adapt_be_list_to_fe(be_data_list: List[BEParserOutput]) -> List[DocumentResponse]:
    """
    BE 파서 출력 리스트를 FE JSON 프로토콜 리스트로 변환
    
    Args:
        be_data_list: BE 파서 출력 리스트
        
    Returns:
        FE용 DocumentResponse 리스트
    """
    return [adapt_be_to_fe(be_data, idx) for idx, be_data in enumerate(be_data_list)]


if __name__ == "__main__":
    # 테스트 코드
    print("=" * 60)
    print("어댑터 레이어 테스트")
    print("=" * 60)
    
    # BE 파서 출력 시뮬레이션
    be_output: BEParserOutput = {
        'filename': '01_기안.hwp',
        'type': '기안',
        'dates': ['2024.04.10', '2024.03.01'],
        'amounts': [
            {'text': '금 50,000,000원', 'amount': 50000000},
            {'text': '금오천만원', 'amount': 50000000}
        ],
        'raw_text': '벚꽃축제 기본계획 수립\n\n일시: 2024.03.01\n예산: 금오천만원'
    }
    
    # 어댑터 실행
    fe_output = adapt_be_to_fe(be_output, 0)
    
    print("\n[BE 입력]")
    print(f"  파일명: {be_output['filename']}")
    print(f"  타입: {be_output['type']}")
    print(f"  날짜: {be_output['dates']}")
    print(f"  금액: {be_output['amounts']}")
    
    print("\n[FE 출력]")
    print(f"  ID: {fe_output['id']}")
    print(f"  제목: {fe_output['summary']}")
    print(f"  대표 날짜: {fe_output['date']}")
    print(f"  대표 금액: {fe_output['amount']:,}원")
    print(f"  상태: {fe_output['status']}")
    print(f"  메시지: {fe_output['message']}")
    
    # 금액 충돌 테스트
    print("\n" + "=" * 60)
    print("금액 충돌 테스트")
    print("=" * 60)
    
    be_conflict: BEParserOutput = {
        'filename': '05_설계변경.hwp',
        'type': '기안',
        'dates': ['2024.03.20'],
        'amounts': [
            {'text': '금 50,000,000원', 'amount': 50000000},
            {'text': '금 5,000,000원', 'amount': 5000000}
        ],
        'raw_text': '설계변경 요청'
    }
    
    fe_conflict = adapt_be_to_fe(be_conflict, 1)
    
    print(f"\n  상태: {fe_conflict['status']}")
    print(f"  메시지: {fe_conflict['message']}")
    print("\n[OK] 어댑터 테스트 완료")
