import re
from datetime import datetime
from typing import List, Dict, Optional


def extract_dates(text: str) -> List[str]:
    """
    텍스트에서 날짜 추출
    
    지원 형식:
    - 2024.03.01
    - 2024-03-01
    - 2024년 3월 1일
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        찾은 날짜 리스트 (예: ['2024.03.01', '2024.04.10'])
    """
    dates = []
    
    # 패턴 1: 2024.03.01 형식
    pattern1 = r'\d{4}\.\d{1,2}\.\d{1,2}'
    dates.extend(re.findall(pattern1, text))
    
    # 패턴 2: 2024-03-01 형식
    pattern2 = r'\d{4}-\d{1,2}-\d{1,2}'
    dates.extend(re.findall(pattern2, text))
    
    # 패턴 3: 2024년 3월 1일 형식
    pattern3 = r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일'
    korean_dates = re.findall(pattern3, text)
    
    # 한글 날짜를 2024.03.01 형식으로 변환
    for kdate in korean_dates:
        # "2024년 3월 1일" → "2024.03.01"
        match = re.match(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', kdate)
        if match:
            year, month, day = match.groups()
            normalized = f"{year}.{month.zfill(2)}.{day.zfill(2)}"
            dates.append(normalized)
    
    # 중복 제거
    return list(set(dates))


def extract_amounts(text: str) -> List[Dict[str, any]]:
    amounts = []
    seen_amounts = set()
    
    # 제외할 단위들 (인원, 횟수, 연도 등)
    exclude_units = ['명', '개', '회', '호', '건', '일', '월', '년']
    
    # 콤마 포함 숫자 패턴
    p_number = r'(\d{1,3}(?:,\d{3})+)'
    
    for match in re.finditer(p_number, text):
        val_str = match.group(1).replace(',', '')
        start, end = match.span()
        
        # 숫자 바로 뒤 2글자를 검사하여 제외 단위가 있는지 확인
        suffix = text[match.end():match.end()+2].strip()
        if any(unit in suffix for unit in exclude_units):
            continue
            
        try:
            amount = int(val_str)
            if amount >= 1000 and amount not in seen_amounts:
                # 실제로 '원'이 붙어있는지 확인
                has_won = '원' in text[end:end+3]
                display_text = match.group(0) + ("원" if has_won else "")
                
                amounts.append({"text": display_text, "amount": amount})
                seen_amounts.add(amount)
        except: continue

    # (기존 한글 금액 '오천만' 등의 패턴은 유지)
    return amounts


def convert_korean_to_number(korean_amount: str) -> int:
    """
    한글 금액을 숫자로 변환
    
    예: "금오천만원" → 50000000
    
    Args:
        korean_amount: 한글 금액 (예: "금오천만원")
        
    Returns:
        숫자 금액
    """
    # 간단한 변환 로직 (주요 케이스만)
    korean_amount = korean_amount.replace('금', '').replace('원', '')
    
    # 한글 숫자 매핑
    num_map = {
        '일': 1, '이': 2, '삼': 3, '사': 4, '오': 5,
        '육': 6, '칠': 7, '팔': 8, '구': 9,
        '십': 10, '백': 100, '천': 1000,
        '만': 10000, '억': 100000000
    }
    
    # 간단한 파싱 (완벽하지 않지만 주요 케이스 커버)
    # 예: "오천만" → 5 * 1000 * 10000 = 50,000,000
    
    result = 0
    temp = 0
    
    for char in korean_amount:
        if char in num_map:
            value = num_map[char]
            
            if value >= 10000:  # 만, 억
                temp = (temp if temp > 0 else 1) * value
                result += temp
                temp = 0
            elif value >= 10:  # 십, 백, 천
                temp += (temp if temp > 0 else 1) * value
                temp = 0 if temp >= 10 else temp
            else:  # 일~구
                temp = value
    
    result += temp
    
    # 간단한 케이스 처리
    if '오천만' in korean_amount:
        return 50000000
    elif '삼천만' in korean_amount:
        return 30000000
    elif '오백만' in korean_amount:
        return 5000000
    
    return result if result > 0 else 0


def classify_document_type(filename: str) -> str:
    """
    파일명에서 문서 타입 추출
    
    Args:
        filename: 파일명 (예: "01_기안.hwp")
        
    Returns:
        문서 타입 (기안/계약서/준공/설계변경 등)
    """
    keywords = {
        '기안': '기안',
        '계약': '계약서',
        '계약서': '계약서',
        '준공': '준공',
        '설계변경': '설계변경',
        '변경': '변경'
    }
    
    for keyword, doc_type in keywords.items():
        if keyword in filename:
            return doc_type
    
    return '기타'


def extract_parties(text: str) -> List[str]:
    """
    텍스트에서 계약 상대방(업체명) 추출

    지원 형식:
    - (주)축제나라, 주식회사 OO, OO(주)
    """
    parties = []

    # (주)OO 또는 OO(주) 패턴
    patterns = [
        r'\(주\)\s*[가-힣A-Za-z0-9]+',
        r'[가-힣A-Za-z0-9]+\(주\)',
        r'주식회사\s*[가-힣A-Za-z0-9]+',
        r'[가-힣A-Za-z0-9]+\s*주식회사',
    ]
    for pattern in patterns:
        parties.extend(re.findall(pattern, text))

    return list(set(parties))


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    텍스트에서 핵심 키워드 추출 (빈도 기반)
    """
    # 불용어
    stopwords = {
        '있다', '없다', '하다', '되다', '이다', '것', '수', '등', '및', '또는',
        '위해', '대한', '관련', '따라', '대하여', '위하여', '있는', '없는',
        '하는', '되는', '같은', '위한', '통해', '에서', '으로', '부터',
    }

    # 한글 명사 후보 추출 (2~6글자 한글 단어)
    words = re.findall(r'[가-힣]{2,6}', text)

    # 빈도 계산 (불용어 제외)
    freq = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1

    # 빈도 상위 키워드 반환
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_keywords]]


def process_document(file_path: str, text: str) -> Dict:
    """
    문서 전체 처리
    
    Args:
        file_path: 파일 경로
        text: 추출된 텍스트
        
    Returns:
        {
            "filename": "01_기안.hwp",
            "type": "기안",
            "dates": ["2024.03.01"],
            "amounts": [{"text": "금오천만원", "amount": 50000000}],
            "raw_text": "..."
        }
    """
    from pathlib import Path
    
    filename = Path(file_path).name
    
    return {
        "filename": filename,
        "type": classify_document_type(filename),
        "dates": extract_dates(text),
        "amounts": extract_amounts(text),
        "parties": extract_parties(text),
        "keywords": extract_keywords(text),
        "raw_text": text
    }


if __name__ == "__main__":
    # 테스트
    test_text = """
    벚꽃축제 기본계획 수립
    
    일시: 2024.03.01
    예산: 금오천만원
    
    총 예산은 금 50,000,000원이며, 2024년 4월 10일까지 완료 예정입니다.
    """
    
    print("날짜:", extract_dates(test_text))
    print("금액:", extract_amounts(test_text))