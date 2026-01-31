"""
공공기관 인수인계 시스템 - HTTP API 서버 (파일 업로드 지원)
RunPod에서 실행 - 로컬에서 파일 업로드 후 분석

실행 방법 (RunPod 터미널에서):
    pip install fastapi uvicorn python-multipart chromadb sentence-transformers rank-bm25 openai
    python api_server.py

접속 URL:
    https://yvfe7u20ltb89m-8888.proxy.runpod.net
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import shutil
import threading
import uuid
from datetime import datetime

# 설정
DATA_DIR = "./my_data"
os.makedirs(DATA_DIR, exist_ok=True)

# FastAPI 앱 생성
app = FastAPI(
    title="🏛️ 공공기관 인수인계 시스템 API",
    description="파일 업로드 → 자동 분석 → 챗봇 질문",
    version="3.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 요청/응답 모델 =====
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    success: bool

class DraftRequest(BaseModel):
    reference_content: str = ""
    reference_name: str = ""
    reference_summary: str = ""
    reference_amount: Optional[int] = None
    title: str = ""
    amount: str = ""
    date: str = ""
    extra: str = ""

# ===== 전역 변수 =====
analyzer = None
analyzer_ready = False
rag_engine = None
uploaded_files = []

# 비동기 작업 저장소
tasks = {}  # {task_id: {"status": "pending"|"running"|"done"|"error", "result": ..., "error": ...}}

# ===== 서버 시작 시 analyzer 초기화 =====
@app.on_event("startup")
def startup_init():
    """서버 시작 시 DocumentAnalyzer를 미리 초기화 (Ko-SBERT, ChromaDB 로드)"""
    global analyzer, analyzer_ready
    try:
        from auto_analyzer import DocumentAnalyzer
        print("[Startup] DocumentAnalyzer 초기화 중...")
        analyzer = DocumentAnalyzer()
        if analyzer.setup():
            analyzer_ready = True
            print("[Startup] DocumentAnalyzer 준비 완료!")
        else:
            print("[Startup] DocumentAnalyzer setup 실패 — /analyze 요청 시 재시도합니다")
    except Exception as e:
        print(f"[Startup] DocumentAnalyzer 초기화 오류: {e}")
        print("[Startup] /analyze 요청 시 재시도합니다")

# ===== API 엔드포인트 =====

@app.get("/")
def root():
    """서버 상태 확인"""
    return {
        "status": "running",
        "analyzer_ready": analyzer_ready,
        "message": "🏛️ 공공기관 인수인계 시스템 API",
        "uploaded_files": len(uploaded_files),
        "active_tasks": sum(1 for t in tasks.values() if t["status"] in ("pending", "running")),
        "endpoints": {
            "파일업로드": "POST /upload",
            "분석(비동기)": "POST /analyze → task_id 반환",
            "분석상태": "GET /analyze/status/{task_id}",
            "채팅": "POST /chat"
        }
    }

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """파일 업로드 (로컬 → 서버)"""
    global uploaded_files

    saved = []
    for file in files:
        try:
            file_path = os.path.join(DATA_DIR, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            saved.append(file.filename)
            uploaded_files.append(file.filename)
        except Exception as e:
            return {"error": f"{file.filename} 업로드 실패: {e}"}

    return {
        "success": True,
        "uploaded": saved,
        "total_files": len(uploaded_files),
        "message": f"✅ {len(saved)}개 파일 업로드 완료!"
    }

@app.get("/files")
def list_files():
    """업로드된 파일 목록"""
    files = os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else []
    return {"files": files, "count": len(files)}

@app.delete("/files")
def clear_files():
    """모든 파일 삭제"""
    global uploaded_files
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
        os.makedirs(DATA_DIR)
    uploaded_files = []
    return {"success": True, "message": "모든 파일이 삭제되었습니다."}

@app.post("/analyze")
def analyze_documents():
    """
    문서 자동 분석 (비동기)
    즉시 task_id를 반환하고, 백그라운드에서 분석 수행.
    GET /analyze/status/{task_id} 로 결과 조회.

    기존 동기 방식도 호환: 결과에 task_id가 있으면 폴링, 없으면 직접 결과.
    """
    global analyzer, analyzer_ready

    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {"status": "pending", "result": None, "error": None, "created": datetime.now().isoformat()}

    def run_analysis():
        global analyzer, analyzer_ready
        tasks[task_id]["status"] = "running"
        try:
            # analyzer가 아직 초기화 안 됐으면 여기서 초기화
            if not analyzer_ready:
                from auto_analyzer import DocumentAnalyzer
                analyzer = DocumentAnalyzer()
                if not analyzer.setup():
                    tasks[task_id]["status"] = "error"
                    tasks[task_id]["error"] = "분석 시스템 초기화 실패"
                    return
                analyzer_ready = True

            result = analyzer.analyze_all()
            tasks[task_id]["status"] = "done"
            tasks[task_id]["result"] = result if result else {}
            print(f"[Analyze] 작업 완료: {task_id}")

        except Exception as e:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = str(e)
            print(f"[Analyze] 작업 실패: {task_id} — {e}")

    threading.Thread(target=run_analysis, daemon=True).start()

    # 즉시 반환 — 524 방지
    return {
        "success": True,
        "async": True,
        "task_id": task_id,
        "message": "분석이 시작되었습니다. GET /analyze/status/{task_id}로 결과를 조회하세요."
    }

@app.get("/analyze/status/{task_id}")
def get_analyze_status(task_id: str):
    """분석 작업 상태 조회"""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"작업 '{task_id}'을 찾을 수 없습니다.")

    response = {
        "task_id": task_id,
        "status": task["status"],
    }

    if task["status"] == "done":
        response["success"] = True
        response["result"] = task["result"]
    elif task["status"] == "error":
        response["success"] = False
        response["error"] = task["error"]

    return response

@app.post("/chat")
def chat(request: ChatRequest):
    """챗봇 질문/답변"""
    global rag_engine

    try:
        if rag_engine is None:
            from handover_rag_v3 import HandoverRAGEngine

            rag_engine = HandoverRAGEngine()

            if not rag_engine.setup():
                raise HTTPException(status_code=500, detail="RAG 엔진 초기화 실패")

        # 질문에서 응답 받기
        result = rag_engine.ask(request.question)

        # result가 dict인 경우 처리
        if isinstance(result, dict):
            answer_data = result.get("answer", {})
            if isinstance(answer_data, dict):
                # dict에서 텍스트 추출 (JSON 문자열 대신 읽을 수 있는 텍스트)
                answer = (
                    answer_data.get("answer")
                    or answer_data.get("text")
                    or answer_data.get("content")
                    or answer_data.get("summary")
                    or answer_data.get("response")
                    or str(answer_data)
                )
            else:
                answer = str(answer_data)
        else:
            answer = str(result)

        return {"answer": answer, "success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/draft")
def generate_draft(request: DraftRequest):
    """참고 문서 기반 공문 초안 생성 (LLM)"""
    try:
        from openai import OpenAI

        client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
        model = "mistralai/Mistral-Nemo-Instruct-2407"

        # 참고 문서 컨텍스트 구성
        ref_context = ""
        if request.reference_content:
            ref_context = f"\n\n[참고 문서: {request.reference_name}]\n{request.reference_content[:3000]}"
        elif request.reference_summary:
            ref_context = f"\n\n[참고 문서: {request.reference_name}]\n요약: {request.reference_summary}"

        # 금액 포맷
        amount_num = int(''.join(c for c in request.amount if c.isdigit())) if request.amount else 0
        formatted_amount = f"{amount_num:,}" if amount_num else request.amount

        # 1단계: 문서 유형 판별
        type_prompt = f"""다음 정보를 보고 작성할 공문의 유형을 판별하세요.
사업명: {request.title}
금액: {formatted_amount}원
시행일: {request.date}
참고문서: {request.reference_name}
{ref_context[:500]}

반드시 다음 중 하나만 답하세요:
- GOV_ELECTRONIC (전자결재 공문: 시행문, 안내문, 통보문 등)
- PLANNING_REPORT (계획서/보고서: 기본계획, 사업계획, 추진계획 등)

답:"""

        type_resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "공문서 유형 분류기입니다. GOV_ELECTRONIC 또는 PLANNING_REPORT 중 하나만 답하세요."},
                {"role": "user", "content": type_prompt}
            ],
            max_tokens=20,
            temperature=0.0
        )
        type_text = type_resp.choices[0].message.content.strip()
        template_type = "PLANNING_REPORT" if "PLANNING" in type_text.upper() else "GOV_ELECTRONIC"

        # 2단계: 문서 내용 생성
        if template_type == "GOV_ELECTRONIC":
            structured = _generate_electronic_doc(client, model, request, ref_context, formatted_amount)
        else:
            structured = _generate_planning_report(client, model, request, ref_context, formatted_amount, amount_num)

        return {
            "success": True,
            "templateType": template_type,
            "structured": structured,
            "referenceFileName": request.reference_name or None,
        }

    except Exception as e:
        print(f"[Draft] 공문 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_electronic_doc(client, model, req, ref_context, formatted_amount):
    """전자결재 공문 구조 생성"""
    prompt = f"""다음 정보를 바탕으로 전자결재 공문(시행문)의 본문을 작성하세요.

사업명: {req.title}
금액: {formatted_amount}원
시행일: {req.date}
추가사항: {req.extra}
{ref_context}

다음 형식으로 작성하세요:
1. 관련 근거 (1~2문장)
2. 본문 내용 (목적 설명 후 세부사항을 가, 나, 다 항목으로)

간결하고 공식적인 행정 문체로 한국어로 작성하세요."""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "공공기관 행정문서 작성 전문가입니다. 간결하고 정확한 공문을 작성합니다."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.2
    )
    generated = resp.choices[0].message.content.strip()

    # 생성된 텍스트를 구조화
    lines = generated.split('\n')
    sections = []
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # 번호로 시작하는 항목 감지
        if stripped[:2] in ('1.', '2.', '3.', '4.', '5.'):
            if current_section:
                sections.append(current_section)
            current_section = {
                "label": stripped[:2],
                "content": stripped[2:].strip(),
                "type": "simple"
            }
        elif stripped[:2] in ('가.', '나.', '다.', '라.', '마.'):
            if current_section and current_section.get("type") == "simple":
                current_section["type"] = "detailed"
                current_section["detailItems"] = []
            if current_section:
                current_section.setdefault("detailItems", []).append({
                    "label": stripped[:2],
                    "content": stripped[2:].strip()
                })
        elif current_section:
            current_section["content"] += " " + stripped

    if current_section:
        sections.append(current_section)

    # 섹션이 비었으면 기본 구조
    if not sections:
        sections = [
            {"label": "1.", "content": f"{req.title} 관련 사항을 다음과 같이 시행하고자 합니다.", "type": "detailed",
             "detailItems": [
                 {"label": "가.", "content": f"사업명: {req.title}"},
                 {"label": "나.", "content": f"사업비: {formatted_amount}원"},
                 {"label": "다.", "content": f"시행일: {req.date}"},
             ]}
        ]

    return {
        "slogan": "",
        "institution": "○○시청",
        "title": f"{req.title} 시행 안내",
        "receiver": "내부결재",
        "related": f"{req.reference_name}" if req.reference_name else "",
        "mainSections": sections,
    }


def _generate_planning_report(client, model, req, ref_context, formatted_amount, amount_num):
    """계획서/보고서 구조 생성"""
    prompt = f"""다음 정보를 바탕으로 사업 기본계획서의 본문을 작성하세요.

사업명: {req.title}
금액: {formatted_amount}원
시행일: {req.date}
추가사항: {req.extra}
{ref_context}

다음 항목을 포함하여 작성하세요:
1. 추진 목적 (2~3개 항목, 각각 괄호로 핵심어 시작)
2. 사업 개요 (사업명, 기간, 예산)
3. 예산 내역 (항목별 금액)
4. 추진 일정 (시기별 내용)

간결하고 공식적인 행정 문체로 한국어로 작성하세요."""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "공공기관 사업계획서 작성 전문가입니다. 구조화된 계획서를 작성합니다."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.2
    )
    generated = resp.choices[0].message.content.strip()

    # 목적 항목 추출
    purpose_items = []
    for line in generated.split('\n'):
        stripped = line.strip()
        if stripped.startswith('ㅇ') or stripped.startswith('-') or stripped.startswith('•'):
            purpose_items.append({
                "bullet": "ㅇ",
                "content": stripped.lstrip('ㅇ-•').strip()
            })

    if not purpose_items:
        purpose_items = [
            {"bullet": "ㅇ", "content": f"(사업추진) {req.title} 추진을 위한 기본계획 수립"},
            {"bullet": "ㅇ", "content": f"(예산확보) 사업비 {formatted_amount}원 확보 및 집행 계획"},
        ]

    # 예산 항목
    budget_items = []
    if amount_num:
        # 단순 분할
        budget_items = [
            {"category": "직접비", "detail": "사업 수행 비용", "amount": f"{int(amount_num * 0.7):,}"},
            {"category": "간접비", "detail": "관리운영비 등", "amount": f"{int(amount_num * 0.2):,}"},
            {"category": "부가세", "detail": "부가가치세", "amount": f"{int(amount_num * 0.1):,}"},
        ]
    else:
        budget_items = [
            {"category": "직접비", "detail": "사업 수행 비용", "amount": "0"},
        ]

    return {
        "docTitle": f"{req.title} 기본계획 수립(안)",
        "date": req.date or "-",
        "department": "○○과",
        "purposeItems": purpose_items,
        "overviewTable": {
            "rows": [
                {"cells": ["사 업 명", req.title]},
                {"cells": ["사업기간", f"{req.date} ~" if req.date else "-"]},
                {"cells": ["필요예산", f"{formatted_amount}원(부가세 포함)" if formatted_amount else "-"]},
            ]
        },
        "budgetItems": budget_items,
        "scheduleItems": [
            {"period": "1단계", "content": "계획 수립 및 계약 체결"},
            {"period": "2단계", "content": "사업 수행 및 중간 점검"},
            {"period": "3단계", "content": "최종 결과보고 및 정산"},
        ],
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "analyzer_ready": analyzer_ready}


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🏛️ 공공기관 인수인계 시스템 - HTTP API 서버 v3")
    print("=" * 70)
    print("\n📌 서버 시작...")
    print("   URL: https://yvfe7u20ltb89m-8888.proxy.runpod.net")
    print("   API 문서: https://yvfe7u20ltb89m-8888.proxy.runpod.net/docs")
    print("\n💡 사용법:")
    print("   1. POST /upload - 파일 업로드")
    print("   2. POST /analyze - 분석 시작 (비동기, task_id 반환)")
    print("   3. GET  /analyze/status/{task_id} - 분석 결과 조회")
    print("   4. POST /chat - 질문하기")
    print("=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8888)
