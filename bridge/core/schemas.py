from typing import List, Optional, TypedDict

class AmountInfo(TypedDict):
    text: str
    amount: int

class BEParserOutput(TypedDict):
    filename: str
    type: str # 기안, 계약, 지출, 변경, 기타
    dates: List[str]
    amounts: List[AmountInfo]
    parties: List[str]
    keywords: List[str]
    raw_text: str

class DocumentResponse(TypedDict):
    id: str
    name: str
    date: str
    all_dates: List[str]
    docType: str
    summary: str
    amount: int
    all_amounts: List[AmountInfo]
    parties: List[str]
    keywords: List[str]
    status: str # normal, warning, error
    message: str
    raw_text: str
    children: Optional[List['DocumentResponse']]
