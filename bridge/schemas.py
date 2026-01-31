"""
JSON 프로토콜 타입 정의
BE/FE/AI 팀 간 통신 계약

단일 소스: core/schemas.py
이 파일은 하위 호환을 위한 re-export + 유틸리티 함수 제공
"""
from typing import List, Literal
from dataclasses import dataclass, asdict
import json

# ===== 단일 소스에서 re-export =====
from core.schemas import AmountInfo, BEParserOutput, DocumentResponse


# ===== 추가 응답 타입 =====

from typing import TypedDict

class SearchResponse(TypedDict):
    """AI 검색 결과 응답"""
    query: str
    answer: str
    sources: List[str]


class ErrorResponse(TypedDict):
    """에러 응답"""
    error: str
    detail: str
    timestamp: str


# ===== 데이터 클래스 (내부 사용) =====

@dataclass
class Document:
    """문서 객체 (내부 처리용)"""
    id: str
    name: str
    date: str
    docType: str
    summary: str
    amount: int
    status: Literal['normal', 'warning'] = 'normal'
    message: str = ''

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        """딕셔너리에서 생성"""
        return cls(**data)


# ===== 검증 함수 =====

def validate_document_response(data: dict) -> bool:
    """DocumentResponse 타입 검증 (core/schemas.py 필드명 기준)"""
    required_fields = ['id', 'name', 'date', 'docType', 'summary', 'amount', 'status', 'message']

    if not all(field in data for field in required_fields):
        return False

    if not isinstance(data['id'], str):
        return False
    if not isinstance(data['name'], str):
        return False
    if not isinstance(data['date'], str):
        return False
    if not isinstance(data['docType'], str):
        return False
    if not isinstance(data['summary'], str):
        return False
    if not isinstance(data['amount'], int):
        return False
    if data['status'] not in ['normal', 'warning']:
        return False
    if not isinstance(data['message'], str):
        return False

    return True


def validate_document_list(data: List[dict]) -> bool:
    """문서 리스트 검증"""
    if not isinstance(data, list):
        return False
    return all(validate_document_response(doc) for doc in data)


# ===== 유틸리티 함수 =====

def serialize_documents(documents: List[Document]) -> str:
    """문서 리스트를 JSON 문자열로 직렬화"""
    return json.dumps([doc.to_dict() for doc in documents], ensure_ascii=False, indent=2)


def deserialize_documents(json_str: str) -> List[Document]:
    """JSON 문자열을 문서 리스트로 역직렬화"""
    data = json.loads(json_str)
    return [Document.from_dict(doc) for doc in data]


# ===== 더미 데이터 생성 (테스트용) =====

def create_dummy_documents() -> List[Document]:
    """테스트용 더미 문서 생성"""
    return [
        Document(
            id="doc_01",
            name="01_기안.hwp",
            date="2024-03-01",
            docType="기안",
            summary="2024 벚꽃축제 기본계획수립",
            amount=50000000,
            status="normal",
            message=""
        ),
        Document(
            id="doc_02",
            name="02_계약.hwp",
            date="2024-03-10",
            docType="계약",
            summary="벚꽃축제 용역 계약",
            amount=50000000,
            status="normal",
            message=""
        ),
        Document(
            id="doc_03",
            name="03_지출.hwp",
            date="2024-03-15",
            docType="지출",
            summary="벚꽃축제 예산 지출",
            amount=50000000,
            status="normal",
            message=""
        ),
        Document(
            id="doc_04",
            name="05_설계변경.hwp",
            date="2024-03-20",
            docType="기안",
            summary="설계변경 요청",
            amount=5000000,
            status="warning",
            message="🚨 변경계약서 누락 (설계변경 건)"
        ),
        Document(
            id="doc_05",
            name="06_추가지출.hwp",
            date="2024-03-25",
            docType="지출",
            summary="설계변경 추가 지출",
            amount=5000000,
            status="warning",
            message="⚠️ 변경계약서 없이 지출 진행됨"
        ),
    ]


if __name__ == "__main__":
    print("=== JSON 프로토콜 테스트 ===\n")

    docs = create_dummy_documents()
    print(f"생성된 문서 수: {len(docs)}\n")

    json_str = serialize_documents(docs)
    print("직렬화 결과:")
    print(json_str[:200] + "...\n")

    doc_dicts = [doc.to_dict() for doc in docs]
    is_valid = validate_document_list(doc_dicts)
    print(f"검증 결과: {'✅ 통과' if is_valid else '❌ 실패'}\n")

    restored_docs = deserialize_documents(json_str)
    print(f"역직렬화 결과: {len(restored_docs)}개 문서 복원")
    print(f"첫 번째 문서: {restored_docs[0].summary}")
