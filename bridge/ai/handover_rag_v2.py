"""
공공기관/공기업 인수인계 RAG 시스템 v2
- 하이브리드 검색 (BM25 + 벡터)
- 질문 유형 분류
- 구조화된 응답
"""

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
import os
import glob
import re
from typing import List, Dict, Tuple
from collections import Counter

# BM25 검색용
from rank_bm25 import BM25Okapi
import numpy as np

# 파일 읽기
from pypdf import PdfReader
from docx import Document
import pandas as pd
import olefile
import zlib
import zipfile
import xml.etree.ElementTree as ET

# ============== 설정 ==============
BASE_URL = "http://localhost:8000/v1"
API_KEY = "EMPTY"
MODEL_NAME = "mistralai/Mistral-Nemo-Instruct-2407"

CHROMA_DB_PATH = "./chroma_db_handover"
DATA_DIR = "./my_data"
# =================================


class QueryClassifier:
    """질문 유형 분류기"""
    
    QUERY_TYPES = {
        "budget": ["예산", "금액", "비용", "원", "천원", "만원", "억", "결산", "세출", "세입", "산출"],
        "regulation": ["규정", "지침", "매뉴얼", "절차", "방법", "기준", "조항", "법령", "규칙"],
        "organization": ["담당자", "부서", "조직", "팀", "과", "실", "본부", "센터", "담당"],
        "history": ["연혁", "변경", "이력", "개정", "수정", "언제", "년도", "월", "일자"],
        "process": ["업무", "프로세스", "진행", "순서", "단계", "흐름", "처리", "방식"]
    }
    
    @classmethod
    def classify(cls, query: str) -> Tuple[str, float]:
        """질문 유형 분류 및 신뢰도 반환"""
        scores = {}
        
        for qtype, keywords in cls.QUERY_TYPES.items():
            score = sum(1 for kw in keywords if kw in query)
            scores[qtype] = score
        
        if max(scores.values()) == 0:
            return "general", 0.0
        
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type] / len(cls.QUERY_TYPES[best_type])
        
        return best_type, min(confidence, 1.0)


class HybridSearcher:
    """하이브리드 검색 엔진 (BM25 + 벡터)"""
    
    def __init__(self, collection):
        self.collection = collection
        self.documents = []
        self.doc_ids = []
        self.bm25 = None
        self._build_bm25_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """한국어 토크나이징 (간단 버전)"""
        # 특수문자 제거 및 공백 분리
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 1]
    
    def _build_bm25_index(self):
        """BM25 인덱스 구축"""
        # ChromaDB에서 모든 문서 가져오기
        all_docs = self.collection.get(include=["documents", "metadatas"])
        
        if not all_docs['documents']:
            return
        
        self.documents = all_docs['documents']
        self.doc_ids = all_docs['ids']
        self.metadatas = all_docs['metadatas']
        
        # 토크나이징
        tokenized_docs = [self._tokenize(doc) for doc in self.documents]
        
        # BM25 인덱스 생성
        self.bm25 = BM25Okapi(tokenized_docs)
        print(f"   📊 BM25 인덱스 구축 완료: {len(self.documents)}개 문서")
    
    def search(self, query: str, n_results: int = 5, 
               bm25_weight: float = 0.3, vector_weight: float = 0.7) -> Dict:
        """하이브리드 검색 수행"""
        
        # 1. 벡터 검색
        vector_results = self.collection.query(
            query_texts=[query],
            n_results=n_results * 2  # 더 많이 가져와서 병합
        )
        
        # 2. BM25 검색
        bm25_scores = {}
        if self.bm25:
            query_tokens = self._tokenize(query)
            scores = self.bm25.get_scores(query_tokens)
            
            # 상위 n_results * 2개 선택
            top_indices = np.argsort(scores)[::-1][:n_results * 2]
            
            for idx in top_indices:
                if scores[idx] > 0:
                    bm25_scores[self.doc_ids[idx]] = scores[idx]
        
        # 3. 점수 병합
        combined_scores = {}
        
        # 벡터 검색 결과 점수화 (거리 기반)
        for i, doc_id in enumerate(vector_results['ids'][0]):
            # ChromaDB는 거리를 반환하므로 역수로 변환
            distance = vector_results['distances'][0][i] if 'distances' in vector_results else 0
            vector_score = 1 / (1 + distance)  # 거리가 작을수록 높은 점수
            combined_scores[doc_id] = vector_score * vector_weight
        
        # BM25 점수 추가
        if bm25_scores:
            max_bm25 = max(bm25_scores.values())
            for doc_id, score in bm25_scores.items():
                normalized_score = score / max_bm25 if max_bm25 > 0 else 0
                if doc_id in combined_scores:
                    combined_scores[doc_id] += normalized_score * bm25_weight
                else:
                    combined_scores[doc_id] = normalized_score * bm25_weight
        
        # 4. 상위 n_results 선택
        sorted_ids = sorted(combined_scores.keys(), 
                           key=lambda x: combined_scores[x], 
                           reverse=True)[:n_results]
        
        # 5. 결과 구성
        result_docs = []
        result_metas = []
        
        for doc_id in sorted_ids:
            idx = self.doc_ids.index(doc_id)
            result_docs.append(self.documents[idx])
            result_metas.append(self.metadatas[idx])
        
        return {
            'documents': [result_docs],
            'metadatas': [result_metas],
            'ids': [sorted_ids]
        }


class HandoverRAG:
    """공공기관 인수인계 RAG 시스템"""
    
    def __init__(self):
        self.client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        self.collection = None
        self.searcher = None
        
        # 질문 유형별 시스템 프롬프트
        self.system_prompts = {
            "budget": """당신은 공공기관 예산/회계 전문 인수인계 담당자입니다.

[핵심 지침]
1. 예산 금액은 천 단위 쉼표 포함, 1원 단위까지 정확히 (예: 20,377,728원)
2. 표 형식으로 항목-산출식-금액을 명확히 정리
3. 세부 항목 합계와 총계가 일치하는지 검산하여 표시
4. 예산 편성 근거와 관련 규정을 함께 안내
5. 전년 대비 증감이 있다면 변동 사유 설명""",

            "regulation": """당신은 공공기관 규정/지침 전문 인수인계 담당자입니다.

[핵심 지침]
1. 규정의 조항 번호와 정확한 문구를 인용
2. 적용 대상과 예외 사항을 명확히 구분
3. 관련된 상위 법령이나 다른 규정 언급
4. 실무 적용 시 주의사항 안내
5. 개정 이력이 있다면 최신 버전 기준으로 답변""",

            "organization": """당신은 공공기관 조직/인사 전문 인수인계 담당자입니다.

[핵심 지침]
1. 담당 부서와 담당자 정보를 정확히 전달
2. 업무 분장 및 결재 라인 설명
3. 유관 부서와의 협업 관계 안내
4. 비상 연락처나 대체 담당자 정보 포함
5. 조직 변경 이력이 있다면 함께 설명""",

            "history": """당신은 공공기관 업무 이력 관리 전문 인수인계 담당자입니다.

[핵심 지침]
1. 시간순으로 변경 이력 정리 (최신순 또는 과거순)
2. 변경 사유와 결정 배경 설명
3. 변경 전후 비교가 가능하도록 정리
4. 관련 결재 문서나 회의록 참조 안내
5. 향후 예정된 변경 사항도 포함""",

            "process": """당신은 공공기관 업무 프로세스 전문 인수인계 담당자입니다.

[핵심 지침]
1. 업무 진행 순서를 단계별로 명확히 설명
2. 각 단계별 담당자, 소요 시간, 필요 서류 안내
3. 주의사항과 자주 발생하는 오류 사례 공유
4. 관련 시스템이나 프로그램 사용법 포함
5. 업무 인계 시 반드시 알아야 할 노하우 전달""",

            "general": """당신은 공공기관 업무 인수인계 전문가입니다.

[핵심 지침]
1. 한국어로 정중하고 상세하게 답변
2. 문서에서 확인된 정보만 정확히 전달
3. 가독성을 위해 표, 목록, 단계별 형식 활용
4. 관련 문서 출처를 명시
5. 불확실한 내용은 "문서에서 확인되지 않음" 표시"""
        }
    
    def setup(self):
        """시스템 초기화"""
        print("=" * 70)
        print("🏛️ 공공기관 인수인계 RAG 시스템 v2")
        print("=" * 70)
        print(f"📍 서버: {BASE_URL}")
        print(f"💾 DB 경로: {CHROMA_DB_PATH}")
        print(f"📁 문서 경로: {DATA_DIR}")
        print()
        
        # 서버 연결 테스트
        print("[연결 테스트] vLLM 서버 확인 중...", end="", flush=True)
        try:
            self.client.models.list()
            print(" ✅ 연결 성공!")
        except Exception as e:
            print(f" ❌ 실패!")
            print(f"🔴 오류: {e}")
            print("\n💡 SSH 터널링을 확인하세요.")
            return False
        
        # 임베딩 및 DB 설정
        print("\n[1/4] 한국어 임베딩 엔진 로드 중...")
        ko_embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask"
        )
        
        print("[2/4] ChromaDB 초기화 중...")
        db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = db_client.get_or_create_collection(
            "handover_docs",
            embedding_function=ko_embedding
        )
        
        # 문서 로드
        print("[3/4] 문서 로드 중...")
        self._load_documents()
        
        # 하이브리드 검색 엔진 초기화
        print("[4/4] 하이브리드 검색 엔진 초기화 중...")
        self.searcher = HybridSearcher(self.collection)
        
        print("\n✅ 시스템 준비 완료!")
        return True
    
    def _load_documents(self):
        """문서 로드 및 색인"""
        from local_rag import (
            read_pdf, read_docx, read_excel, read_hwp, read_hwpx, 
            read_text_file, split_text
        )
        
        loaders = {
            ".txt": read_text_file,
            ".md": read_text_file,
            ".pdf": read_pdf,
            ".docx": read_docx,
            ".xlsx": read_excel,
            ".xls": read_excel,
            ".hwp": read_hwp,
            ".hwpx": read_hwpx
        }
        
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            print(f"   📁 '{DATA_DIR}' 폴더 생성됨")
            return
        
        all_files = glob.glob(os.path.join(DATA_DIR, "*.*"))
        docs, metas, ids = [], [], []
        
        for file_path in all_files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in loaders:
                continue
            
            try:
                content = loaders[ext](file_path)
                if content and len(content.strip()) > 10:
                    # 청크 크기를 줄여서 더 많은 결과 검색 가능
                    chunks = split_text(content, chunk_size=1500, overlap=300)
                    
                    for j, chunk in enumerate(chunks):
                        docs.append(chunk)
                        metas.append({
                            "source": os.path.basename(file_path),
                            "type": ext,
                            "chunk": j,
                            "doc_type": self._infer_doc_type(file_path, chunk)
                        })
                        ids.append(f"{os.path.basename(file_path)}_chunk_{j}")
                    
                    print(f"   ✅ {os.path.basename(file_path)} → {len(chunks)}개 청크")
            except Exception as e:
                print(f"   ❌ {os.path.basename(file_path)}: {e}")
        
        if docs:
            self.collection.upsert(documents=docs, metadatas=metas, ids=ids)
            print(f"   📚 총 {len(docs)}개 청크 색인 완료")
    
    def _infer_doc_type(self, file_path: str, content: str) -> str:
        """문서 유형 추론"""
        filename = os.path.basename(file_path).lower()
        content_lower = content.lower()
        
        if any(kw in filename for kw in ["예산", "결산", "세출", "세입"]):
            return "budget"
        elif any(kw in filename for kw in ["규정", "지침", "매뉴얼"]):
            return "regulation"
        elif any(kw in filename for kw in ["조직", "분장", "담당"]):
            return "organization"
        elif "원" in content and any(c.isdigit() for c in content):
            return "budget"
        else:
            return "general"
    
    def ask(self, query: str) -> str:
        """질문에 답변"""
        
        # 1. 질문 유형 분류
        query_type, confidence = QueryClassifier.classify(query)
        print(f"   📋 질문 유형: {query_type} (신뢰도: {confidence:.1%})")
        
        # 2. 하이브리드 검색
        print("   🔍 하이브리드 검색 중...", end="", flush=True)
        
        # 질문 유형에 따라 검색 가중치 조정
        if query_type == "budget":
            # 예산 질문은 키워드 매칭 중요 (청크가 작아서 5개 가능)
            results = self.searcher.search(query, n_results=5, 
                                          bm25_weight=0.5, vector_weight=0.5)
        else:
            # 일반적인 경우 의미론적 검색 우선
            results = self.searcher.search(query, n_results=5,
                                          bm25_weight=0.3, vector_weight=0.7)
        
        print(" 완료!")
        
        # 3. 컨텍스트 구성
        context = ""
        sources = set()
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            source = meta.get('source', 'unknown')
            doc_type = meta.get('doc_type', 'general')
            sources.add(source)
            context += f"[📄 {source} | 유형: {doc_type}]\n{doc}\n\n"
        
        print(f"   📚 참고 문서: {len(results['documents'][0])}개")
        
        # 4. 시스템 프롬프트 선택
        system_prompt = self.system_prompts.get(query_type, self.system_prompts["general"])
        
        # 5. LLM 호출
        print("   🤖 AI 분석 중:\n")
        
        user_prompt = f"""아래 인수인계 문서를 참고하여 질문에 상세히 답변해 주세요.

[참고 문서]
{context}

[질문]
{query}

[답변 형식]
- 핵심 내용을 먼저 요약
- 상세 내용은 표나 목록으로 정리
- 관련 규정이나 근거가 있으면 언급
- 마지막에 참고한 문서명 표시"""

        try:
            stream = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                stream=True
            )
            
            response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    response += content
            
            print(f"\n\n   📄 참고 파일: {', '.join(sources)}")
            return response
            
        except Exception as e:
            print(f"\n❌ 오류: {e}")
            return ""
    
    def run(self):
        """대화형 실행"""
        print("\n" + "=" * 70)
        print("💡 인수인계 질문 예시:")
        print("   - 2026년 예산 세부 항목을 표로 정리해줘")
        print("   - 출장비 정산 절차를 단계별로 알려줘")
        print("   - 담당 업무 분장은 어떻게 되어 있어?")
        print("   - 최근 규정 개정 이력을 알려줘")
        print("=" * 70)
        print("(종료: quit)")
        print()
        
        while True:
            query = input("\n질문: ")
            if query.lower() in ["quit", "exit", "종료"]:
                print("👋 시스템을 종료합니다.")
                break
            
            if not query.strip():
                continue
            
            self.ask(query)


def main():
    # BM25 의존성 확인
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        print("⚠️ rank_bm25 설치 필요: pip install rank-bm25")
        return
    
    rag = HandoverRAG()
    if rag.setup():
        rag.run()


if __name__ == "__main__":
    main()
