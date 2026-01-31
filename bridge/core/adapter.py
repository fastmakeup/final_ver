from typing import List, Optional
from core.schemas import BEParserOutput, DocumentResponse, AmountInfo

def select_primary_date(dates: List[str]) -> str:
    if not dates: return "날짜 없음"
    return sorted(dates)[0]

def select_primary_amount(amounts: List[AmountInfo]) -> int:
    if not amounts: return 0
    return max(amounts, key=lambda x: x['amount'])['amount']

def extract_title(raw_text: str, max_length: int = 50) -> str:
    if not raw_text: return "제목 없음"
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    return lines[0][:max_length] if lines else "제목 없음"

def detect_amount_conflict(amounts: List[AmountInfo]) -> bool:
    if len(amounts) <= 1: return False
    return len(set(a['amount'] for a in amounts)) > 1

def generate_warning_message(amounts: List[AmountInfo]) -> str:
    if not detect_amount_conflict(amounts): return ""
    unique_amounts = sorted(list(set(a['amount'] for a in amounts)), reverse=True)
    return f"[경고] 금액 불일치 ({' vs '.join([f'{a:,}원' for a in unique_amounts])})"

def infer_document_type(filename: str, raw_text: str, be_type: str) -> str:
    if be_type != '기타': return be_type
    f_lower, t_lower = filename.lower(), raw_text.lower()
    mapping = {'기안': ['기안'], '계약': ['계약', '용역'], '지출': ['지출', '집행'], '변경': ['변경', '설계']}
    for doc_type, keywords in mapping.items():
        if any(kw in f_lower or kw in t_lower for kw in keywords):
            return doc_type
    return '기타'

def adapt_be_to_fe(be_data: BEParserOutput, file_index: int) -> DocumentResponse:
    has_conflict = detect_amount_conflict(be_data['amounts'])
    return {
        'id': f"doc_{file_index:02d}",
        'name': be_data['filename'],
        'date': select_primary_date(be_data['dates']),
        'all_dates': be_data['dates'],
        'docType': infer_document_type(be_data['filename'], be_data['raw_text'], be_data['type']),
        'summary': extract_title(be_data['raw_text']),
        'amount': select_primary_amount(be_data['amounts']),
        'all_amounts': be_data['amounts'],
        'parties': be_data.get('parties', []),
        'keywords': be_data.get('keywords', []),
        'status': 'warning' if has_conflict else 'normal',
        'message': generate_warning_message(be_data['amounts']) if has_conflict else "",
        'raw_text': be_data['raw_text'],
        'children': None
    }

def adapt_be_list_to_fe(be_data_list: List[BEParserOutput]) -> List[DocumentResponse]:
    return [adapt_be_to_fe(be_data, idx) for idx, be_data in enumerate(be_data_list)]
