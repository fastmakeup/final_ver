"""
공공기관 인수인계 RAG 시스템 v3 (LangGraph 기반)
- 구조화된 JSON 응답
- 프론트엔드 대시보드 연동
- 공공기관 지침 내장
"""

import json
import os
import glob
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, TypedDict
from dataclasses import dataclass, asdict

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from rank_bm25 import BM25Okapi
import numpy as np

# LangGraph
from langgraph.graph import StateGraph, END

# ============== 설정 (중앙 config 연동) ==============
import config
# =================================


# ============== 공공기관 기본 지침 ==============
PUBLIC_INSTITUTION_GUIDELINES = """
## 📋 공공기관 업무처리 기본 지침

### 1. 문서 분류 체계
- **기안문**: 업무 시작, 예산 요청, 계획 수립
- **계약서**: 용역계약, 물품구매, 시설공사
- **품의서**: 지출 승인 요청
- **결재문서**: 최종 승인 문서
- **검수조서**: 납품/용역 완료 확인
- **정산서**: 사업 종료 후 정산

### 2. 예산 집행 프로세스
1) 기본계획 수립 → 예산 확보
2) 사업자 선정 → 계약 체결
3) 사업 수행 → 중간점검
4) 검수 → 대금 지급
5) 정산 → 사업 종료

### 3. 주요 법령 및 규정
- 「국가재정법」: 예산 편성 및 집행
- 「국가를 당사자로 하는 계약에 관한 법률」: 계약 절차
- 「공공기관의 운영에 관한 법률」: 기관 운영
- 「정부업무평가 기본법」: 성과 측정

### 4. 금액 표기 원칙
- 천 단위 쉼표 필수 (예: 20,377,728원)
- 부가세 포함/별도 명시
- 예산과 실집행액 구분

### 5. 주의사항 (Issues 분류)
- 🔴 critical: 법령 위반, 금액 오류
- 🟡 warn: 절차 누락, 서류 미비
- 🔵 info: 참고사항, 권고사항
"""


# ============== 데이터 모델 ==============
class ProjectState(TypedDict):
    """LangGraph 상태 정의"""
    query: str
    query_type: str
    files: List[Dict]
    retrieved_docs: List[Dict]
    timeline: Dict
    issues: List[Dict]
    summary: Dict
    response_json: Dict
    final_answer: str


@dataclass
class TimelineEvent:
    date: str
    label: str
    description: str
    phaseId: str
    fileId: str
    amount: Optional[int] = None
    highlight: bool = False


@dataclass
class TimelinePhase:
    id: str
    name: str
    color: str


@dataclass 
class Issue:
    level: str  # critical, warn, info
    title: str
    description: str
    suggestion: str
    relatedFileIds: List[str]


# ============== 질문 유형 분류 ==============
class QueryClassifier:
    QUERY_TYPES = {
        "budget": ["예산", "금액", "비용", "원", "결산", "세출", "세입", "산출", "정산"],
        "contract": ["계약", "용역", "입찰", "낙찰", "수의계약", "업체", "사업자"],
        "process": ["절차", "프로세스", "순서", "단계", "방법", "진행"],
        "regulation": ["규정", "지침", "법령", "조항", "기준"],
        "timeline": ["일정", "기간", "언제", "날짜", "연혁", "이력"],
        "organization": ["담당자", "부서", "조직", "담당", "연락처"]
    }
    
    @classmethod
    def classify(cls, query: str) -> tuple:
        scores = {qtype: sum(1 for kw in keywords if kw in query) 
                  for qtype, keywords in cls.QUERY_TYPES.items()}
        if max(scores.values()) == 0:
            return "general", 0.0
        best_type = max(scores, key=scores.get)
        return best_type, scores[best_type] / len(cls.QUERY_TYPES[best_type])


# ============== 하이브리드 검색 ==============
class HybridSearcher:
    def __init__(self, collection):
        self.collection = collection
        self.documents = []
        self.doc_ids = []
        self.metadatas = []
        self.bm25 = None
        self._build_index()
    
    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'[^\w\s]', ' ', text)
        return [t for t in text.split() if len(t) > 1]
    
    def _build_index(self):
        all_docs = self.collection.get(include=["documents", "metadatas"])
        if not all_docs['documents']:
            return
        self.documents = all_docs['documents']
        self.doc_ids = all_docs['ids']
        self.metadatas = all_docs['metadatas']
        tokenized = [self._tokenize(doc) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        # 벡터 검색
        vector_results = self.collection.query(query_texts=[query], n_results=n_results * 2)
        
        # BM25 검색
        bm25_scores = {}
        if self.bm25:
            scores = self.bm25.get_scores(self._tokenize(query))
            for idx in np.argsort(scores)[::-1][:n_results * 2]:
                if scores[idx] > 0:
                    bm25_scores[self.doc_ids[idx]] = scores[idx]
        
        # 점수 병합
        combined = {}
        for i, doc_id in enumerate(vector_results['ids'][0]):
            combined[doc_id] = 0.7 * (1 / (1 + i))
        
        if bm25_scores:
            max_bm25 = max(bm25_scores.values())
            for doc_id, score in bm25_scores.items():
                combined[doc_id] = combined.get(doc_id, 0) + 0.3 * (score / max_bm25)
        
        # 상위 결과 반환
        sorted_ids = sorted(combined.keys(), key=lambda x: combined[x], reverse=True)[:n_results]
        
        results = []
        for doc_id in sorted_ids:
            idx = self.doc_ids.index(doc_id)
            results.append({
                "id": doc_id,
                "content": self.documents[idx],
                "metadata": self.metadatas[idx]
            })
        return results


# ============== RAG 엔진 ==============
class HandoverRAGEngine:
    def __init__(self, base_url: Optional[str] = None):
        import httpx
        self.base_url = base_url or config.LLM_API_URL
        # SSL 검증 무시 (RunPod 프록시 대응)
        http_client = httpx.Client(verify=False)
        self.client = OpenAI(base_url=self.base_url, api_key=config.API_KEY, http_client=http_client)
        self.collection = None
        self.searcher = None
        self.graph = None
        
    def setup(self):
        """시스템 초기화"""
        print("=" * 70)
        print("🏛️ 공공기관 인수인계 RAG 시스템 v3 (LangGraph)")
        print("=" * 70)
        
        # 서버 연결 확인
        print("[1/4] vLLM 서버 연결 확인...", end="", flush=True)
        try:
            self.client.models.list()
            print(" ✅")
        except Exception as e:
            print(f" ❌\n{e}")
            return False
        
        # ChromaDB 설정
        print("[2/4] ChromaDB 초기화...", end="", flush=True)
        ko_embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask"
        )
        db_client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.collection = db_client.get_or_create_collection(
            "handover_v3", embedding_function=ko_embedding
        )
        print(" ✅")
        
        # 문서 로드
        print("[3/4] 문서 로드 중...")
        # 검색 엔진 초기화
        print("[3/4] 하이브리드 검색 엔진 초기화...", end="", flush=True)
        self.searcher = HybridSearcher(self.collection)
        print(" ✅")
        
        # LangGraph 워크플로우 구성
        self._build_graph()
        
        print("\n✅ 시스템 준비 완료!")
        return True
    
    def load_directory(self, path: str):
        """
        [동적 로드] 사용자가 선택한 폴더의 문서를 색인합니다.
        가장 최신 정보를 유지하기 위해 기존 DB를 밀고 새로 만듭니다.
        """
        print(f"\n📂 AI 엔진 색인 업데이트: {path}")
        
        from local_rag import read_pdf, read_docx, read_excel, read_hwp, read_hwpx, read_text_file, split_text
        
        loaders = {
            ".pdf": read_pdf, ".docx": read_docx, ".xlsx": read_excel,
            ".xls": read_excel, ".hwp": read_hwp, ".hwpx": read_hwpx,
            ".txt": read_text_file, ".md": read_text_file
        }
        
        if not os.path.exists(path):
            return
        
        # 하위 디렉토리까지 재귀 검색
        all_files = glob.glob(os.path.join(path, "**", "*.*"), recursive=True)
        docs, metas, ids = [], [], []
        
        for file_path in all_files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in loaders: continue
            
            try:
                content = loaders[ext](file_path)
                if content and len(content.strip()) > 10:
                    chunks = split_text(content, chunk_size=1500, overlap=300)
                    for j, chunk in enumerate(chunks):
                        docs.append(chunk)
                        metas.append({
                            "fileId": f"file-{len(docs)}",
                            "source": os.path.basename(file_path),
                            "docType": self._infer_doc_type(file_path, chunk),
                            "chunk": j,
                            "date": self._extract_date(chunk)
                        })
                        ids.append(f"{os.path.basename(file_path)}_{j}")
            except Exception as e:
                print(f"   ! AI 색인 오류 ({os.path.basename(file_path)}): {e}")

        # 기존 데이터 초기화 (항상 최신 상태 보장)
        try:
            self.collection.delete(where={})
        except:
            pass

        if docs:
            self.collection.upsert(documents=docs, metadatas=metas, ids=ids)
            print(f"   📚 AI 엔진 색인 완료 (총 {len(docs)}개 청크)")
            self.searcher = HybridSearcher(self.collection)
    
    def _infer_doc_type(self, path: str, content: str) -> str:
        name = os.path.basename(path).lower()
        if any(kw in name for kw in ["예산", "결산", "산출"]):
            return "budget"
        elif any(kw in name for kw in ["계약", "용역"]):
            return "contract"
        elif any(kw in name for kw in ["규정", "지침"]):
            return "regulation"
        elif "원" in content and re.search(r'\d{1,3}(,\d{3})+', content):
            return "budget"
        return "general"
    
    def _extract_date(self, content: str) -> str:
        match = re.search(r'(\d{4})[-./](\d{1,2})[-./](\d{1,2})', content)
        if match:
            return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
        return ""
    
    def _build_graph(self):
        """LangGraph 워크플로우 구성"""
        
        def classify_query(state: ProjectState) -> ProjectState:
            """Step 1: 질문 유형 분류"""
            query_type, _ = QueryClassifier.classify(state["query"])
            state["query_type"] = query_type
            return state
        
        def retrieve_documents(state: ProjectState) -> ProjectState:
            """Step 2: 문서 검색"""
            results = self.searcher.search(state["query"], n_results=5)
            state["retrieved_docs"] = results
            return state
        
        def build_structure(state: ProjectState) -> ProjectState:
            """Step 3: 구조화된 데이터 생성"""
            docs = state["retrieved_docs"]
            
            # 파일 목록 구성
            files = []
            seen_sources = set()
            for doc in docs:
                source = doc["metadata"].get("source", "unknown")
                if source not in seen_sources:
                    seen_sources.add(source)
                    files.append({
                        "id": doc["metadata"].get("fileId", doc["id"]),
                        "name": source,
                        "docType": doc["metadata"].get("docType", "general"),
                        "date": doc["metadata"].get("date", ""),
                        "summary": doc["content"][:200] + "..."
                    })
            state["files"] = files
            
            # 타임라인 구성
            phases = [
                {"id": "plan", "name": "기획", "color": "#3b82f6"},
                {"id": "contract", "name": "계약", "color": "#8b5cf6"},
                {"id": "execute", "name": "집행", "color": "#10b981"},
                {"id": "close", "name": "정산", "color": "#f59e0b"}
            ]
            
            events = []
            for file in files:
                if file["date"]:
                    phase_id = "plan" if file["docType"] == "budget" else \
                               "contract" if file["docType"] == "contract" else "execute"
                    events.append({
                        "date": file["date"],
                        "label": file["name"],
                        "description": file["summary"][:100],
                        "phaseId": phase_id,
                        "fileId": file["id"],
                        "highlight": False
                    })
            
            state["timeline"] = {"phases": phases, "events": sorted(events, key=lambda x: x["date"])}
            
            # 이슈 분석 (간단 휴리스틱)
            issues = []
            for doc in docs:
                content = doc["content"]
                if "변경" in content and "계약" in content:
                    issues.append({
                        "level": "warn",
                        "title": "계약 변경 감지",
                        "description": "계약 변경 관련 내용이 포함되어 있습니다.",
                        "suggestion": "변경계약서 및 사유서를 확인하세요.",
                        "relatedFileIds": [doc["metadata"].get("fileId", doc["id"])]
                    })
            state["issues"] = issues
            
            return state
        
        def generate_response(state: ProjectState) -> ProjectState:
            """Step 4: AI 응답 생성 (JSON 형식)"""
            context = "\n\n".join([
                f"[{doc['metadata'].get('source', 'unknown')}]\n{doc['content']}"
                for doc in state["retrieved_docs"]
            ])
            
            system_prompt = f"""당신은 공공기관 업무 인수인계 AI 전문가입니다.

{PUBLIC_INSTITUTION_GUIDELINES}

## 응답 규칙
1. 반드시 JSON 형식으로 응답하세요.
2. 금액은 천 단위 쉼표 포함 (예: 20,377,728원)
3. 표 데이터는 items 배열로 구조화
4. 친절하고 상세하게 안내

## JSON 응답 형식
```json
{{
  "greeting": "안녕하세요! [질문 주제]에 대해 안내드리겠습니다.",
  "summary": {{
    "title": "제목",
    "totalAmount": 0,
    "period": "기간",
    "keyPoints": ["핵심 포인트 1", "핵심 포인트 2"]
  }},
  "details": {{
    "description": "상세 설명",
    "items": [
      {{"name": "항목명", "calculation": "산출식", "amount": 0}}
    ]
  }},
  "regulations": ["관련 규정 1", "관련 규정 2"],
  "tips": ["인수인계 팁 1", "실무 노하우"],
  "closing": "추가 질문이 있으시면 말씀해 주세요!"
}}
```"""

            user_prompt = f"""다음 문서를 참고하여 질문에 JSON 형식으로 답변하세요.

[참고 문서]
{context}

[질문]
{state["query"]}

반드시 위 JSON 형식을 지켜주세요."""

            try:
                response = self.client.chat.completions.create(
                    model=config.MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0
                )
                
                answer = response.choices[0].message.content
                
                # JSON 추출 시도
                json_match = re.search(r'\{[\s\S]*\}', answer)
                if json_match:
                    try:
                        response_json = json.loads(json_match.group())
                        state["response_json"] = response_json
                    except:
                        state["response_json"] = {"raw": answer}
                else:
                    state["response_json"] = {"raw": answer}
                
                state["final_answer"] = answer
                
            except Exception as e:
                state["final_answer"] = f"오류 발생: {e}"
                state["response_json"] = {"error": str(e)}
            
            return state
        
        # 그래프 구성
        workflow = StateGraph(ProjectState)
        
        workflow.add_node("classify", classify_query)
        workflow.add_node("retrieve", retrieve_documents)
        workflow.add_node("structure", build_structure)
        workflow.add_node("generate", generate_response)
        
        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "retrieve")
        workflow.add_edge("retrieve", "structure")
        workflow.add_edge("structure", "generate")
        workflow.add_edge("generate", END)
        
        self.graph = workflow.compile()
    
    def ask(self, query: str) -> Dict:
        """질문 처리 및 구조화된 응답 반환"""
        print(f"\n📝 질문: {query}")
        print("=" * 50)
        
        initial_state = {
            "query": query,
            "query_type": "",
            "files": [],
            "retrieved_docs": [],
            "timeline": {},
            "issues": [],
            "summary": {},
            "response_json": {},
            "final_answer": ""
        }
        
        print("🔄 처리 중...")
        result = self.graph.invoke(initial_state)
        
        # 최종 응답 구성
        final_response = {
            "project": {
                "id": f"proj-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "name": query[:30],
                "fileCount": len(result["files"]),
                "files": result["files"]
            },
            "summary": {
                "timeline": result["timeline"],
                "issues": result["issues"]
            },
            "answer": result["response_json"],
            "sources": [f["name"] for f in result["files"]]
        }
        
        # 결과 출력
        print("\n" + "=" * 50)
        print("📊 질문 유형:", result["query_type"])
        print("📚 참고 문서:", len(result["files"]), "개")
        print("⚠️  이슈:", len(result["issues"]), "개")
        print("=" * 50)
        
        # AI 응답 출력
        if "greeting" in result["response_json"]:
            print(f"\n🤖 {result['response_json']['greeting']}")
            
            if "summary" in result["response_json"]:
                summary = result["response_json"]["summary"]
                print(f"\n📋 {summary.get('title', '요약')}")
                if "totalAmount" in summary:
                    print(f"   💰 총액: {summary['totalAmount']:,}원" if isinstance(summary['totalAmount'], int) else f"   💰 총액: {summary['totalAmount']}")
                if "keyPoints" in summary:
                    for point in summary["keyPoints"]:
                        print(f"   • {point}")
            
            if "details" in result["response_json"] and "items" in result["response_json"]["details"]:
                print("\n📊 세부 항목:")
                print("-" * 60)
                for item in result["response_json"]["details"]["items"]:
                    print(f"   {item.get('name', '')} | {item.get('calculation', '')} | {item.get('amount', 0):,}원" if isinstance(item.get('amount', 0), int) else f"   {item}")
                print("-" * 60)
            
            if "tips" in result["response_json"]:
                print("\n💡 인수인계 팁:")
                for tip in result["response_json"]["tips"]:
                    print(f"   • {tip}")
            
            if "closing" in result["response_json"]:
                print(f"\n{result['response_json']['closing']}")
        else:
            print("\n🤖 AI 응답:")
            print(result["final_answer"])
        
        print(f"\n📄 출처: {', '.join(final_response['sources'])}")
        
        return final_response
    
    def run(self):
        """대화형 실행"""
        print("\n" + "=" * 70)
        print("💬 질문 예시:")
        print("   - 2026년 예산 세부 항목을 정리해줘")
        print("   - 계약 진행 절차를 알려줘")
        print("   - 담당자 업무 분장을 설명해줘")
        print("=" * 70)
        print("(종료: quit)\n")
        
        while True:
            query = input("\n질문: ")
            if query.lower() in ["quit", "exit", "종료"]:
                print("👋 종료합니다.")
                break
            
            if not query.strip():
                continue
            
            result = self.ask(query)
            
            # JSON 자동 저장
            filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n✅ JSON 저장됨: {filename}")


def main():
    # 의존성 확인
    try:
        from langgraph.graph import StateGraph
    except ImportError:
        print("⚠️ langgraph 설치 필요: pip install langgraph")
        return
    
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        print("⚠️ rank_bm25 설치 필요: pip install rank-bm25")
        return
    
    engine = HandoverRAGEngine()
    if engine.setup():
        engine.run()


if __name__ == "__main__":
    main()
