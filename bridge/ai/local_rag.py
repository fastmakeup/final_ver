import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
import os
import glob
import pandas as pd
from pypdf import PdfReader
from docx import Document
import olefile
import zlib
import zipfile
import xml.etree.ElementTree as ET

# 상위 디렉토리(bridge)를 sys.path에 추가하여 config 접근
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# [설정] config에서 가져오기
BASE_URL = config.BASE_URL
API_KEY = config.API_KEY
MODEL_NAME = config.MODEL_NAME

# [중요] 경로 설정
CHROMA_DB_PATH = config.CHROMA_DB_PATH
DATA_DIR = config.DEFAULT_DATA_DIR

# --- 파일 읽기 함수들 ---

def read_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf(path):
    """PDF를 페이지 구분과 함께 읽기"""
    try:
        reader = PdfReader(path)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n[Page {i+1}]\n{page_text}\n"
        return text
    except Exception as e:
        return f"[PDF 읽기 실패] {e}"

def read_docx(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_excel(path):
    # 모든 시트를 읽어서 텍스트로 변환
    dfs = pd.read_excel(path, sheet_name=None)
    text = ""
    for sheet_name, df in dfs.items():
        text += f"Sheet: {sheet_name}\n"
        text += df.to_string(index=False) + "\n\n"
    return text

def read_hwp(path):
    # HWP 5.0 형식 파싱 (olefile + zlib)
    try:
        f = olefile.OleFileIO(path)
        dirs = f.listdir()
        
        # BodyText 섹션 찾기
        body_sections = [d for d in dirs if d[0] == "BodyText"]
        text = ""
        
        for section in body_sections:
            stream = f.openstream(section)
            data = stream.read()
            
            # HWP 파일 스트림 압축 해제 (zlib)
            unpacked_data = zlib.decompress(data, -15)
            
            # UTF-16LE 인코딩 (HWP 내부 텍스트 인코딩)
            decoded = unpacked_data.decode('utf-16-le', errors='ignore')
            
            # 일반 텍스트만 필터링
            clean_text = ""
            for char in decoded:
                if 32 <= ord(char) or ord(char) in [10, 13]: 
                    clean_text += char
            text += clean_text + "\n"
            
        return text
    except Exception as e:
        return f"[HWP 읽기 실패] {e}"

def read_hwpx(path):
    # HWPX는 ZIP 포맷. Contents/section0.xml 등의 XML 파싱
    try:
        text = ""
        with zipfile.ZipFile(path, 'r') as z:
            # 섹션 파일 찾기
            section_files = [n for n in z.namelist() if n.startswith("Contents/section") and n.endswith(".xml")]
            
            for section in section_files:
                xml_data = z.read(section)
                root = ET.fromstring(xml_data)
                # 모든 텍스트 노드 추출
                for node in root.iter():
                    if node.text:
                        text += node.text
                text += "\n"
        return text
    except Exception as e:
        return f"[HWPX 읽기 실패] {e}"

# --- 텍스트 청킹 (Chunking) 함수 ---

def split_text(text, chunk_size=2500, overlap=400):
    """
    긴 텍스트를 작은 덩어리로 나눕니다.
    표 데이터 보존을 위해 큰 단위로 자릅니다.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        
        # 텍스트 끝에 도달한 경우
        if end >= text_len:
            chunks.append(text[start:])
            break
            
        # 줄바꿈 기준으로 자연스럽게 분할
        last_newline = text.rfind('\n', start, end)
        if last_newline != -1 and last_newline > start + chunk_size * 0.5:
            end = last_newline + 1
        else:
            # 줄바꿈이 없으면 공백 확인
            last_space = text.rfind(' ', start, end)
            if last_space != -1 and last_space > start + chunk_size * 0.5:
                end = last_space + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 겹치게 이동 (overlap)
        start = end - overlap
        
    return chunks

def load_documents_from_folder(folder_path):
    docs = []
    metadatas = []
    ids = []
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"[알림] '{folder_path}' 폴더가 없어 생성했습니다.")
        return [], [], []

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
    
    all_files = glob.glob(os.path.join(folder_path, "*.*"))
    print(f"[시스템] '{folder_path}' 폴더 스캔 중...")
    
    for i, file_path in enumerate(all_files):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in loaders:
            try:
                print(f"   - 읽는 중: {os.path.basename(file_path)}", end="", flush=True)
                content = loaders[ext](file_path)
                
                if content and len(content.strip()) > 10:
                    # [핵심] 읽은 내용을 청킹(Chunking)하여 저장
                    chunks = split_text(content, chunk_size=2500, overlap=400)
                    print(f" -> {len(chunks)}개 조각으로 분할 저장 [성공]")
                    
                    for j, chunk in enumerate(chunks):
                        docs.append(chunk)
                        # 메타데이터에 원본 파일명과 조각 번호 저장
                        metadatas.append({"source": os.path.basename(file_path), "type": ext, "chunk": j})
                        ids.append(f"{os.path.basename(file_path)}_chunk_{j}")
                else:
                    print(" [건너뜀: 내용 없음]")
            except Exception as e:
                print(f" [실패: {e}]")
            
    return docs, metadatas, ids

def main():
    print("=" * 70)
    print("🚀 vLLM RAG 시스템 (보안 강화 + 한국어 정밀 분석)")
    print("=" * 70)
    print(f"📍 서버: {BASE_URL}")
    print(f"💾 DB 경로: {CHROMA_DB_PATH}")
    print(f"📁 문서 경로: {DATA_DIR}")
    print()

    # 서버 연결 테스트
    print("[연결 테스트] vLLM 서버 확인 중...", end="", flush=True)
    try:
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        models = client.models.list()
        print(" ✅ 연결 성공!")
    except Exception as e:
        print(f" ❌ 실패!\n")
        print("🔴 오류:", str(e))
        print("\n💡 해결 방법:")
        print("1. RunPod 서버에서 vLLM이 실행 중인지 확인")
        print("2. SSH 터널링이 켜져 있는지 확인")
        return

    # [추가] 한국어 전용 임베딩 엔진
    print("\n[1/3] 한국어 정밀 검색 엔진 로드 중...")
    ko_embedding_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="jhgan/ko-sroberta-multitask"
    )

    print(f"[2/3] ChromaDB 로드 중... ({CHROMA_DB_PATH})")
    db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # [수정] 한국어 임베딩을 사용하는 컬렉션 생성
    collection = db_client.get_or_create_collection(
        "my_documents_ko",
        embedding_function=ko_embedding_ef
    )

    print("\n문서를 확인합니다(변경사항 반영을 위해 매번 다시 로드)...")
    docs, metas, ids = load_documents_from_folder(DATA_DIR)
    
    if docs:
        print(f"총 {len(docs)}개의 텍스트 조각(Chunk)을 DB에 저장 중...")
        collection.upsert(documents=docs, metadatas=metas, ids=ids)
        print("✅ 완료!")
    else:
        print("⚠️ 로드된 문서가 없습니다. my_data 폴더에 파일을 넣어주세요.")
        return

    # [수정] 예산 분석 특화 시스템 프롬프트
    system_prompt = """당신은 공공기관 예산 정밀 분석 전문가입니다.

[핵심 원칙]
1. 한국어로 정중하고 상세하게 답변하세요.
2. 예산·수치는 천 단위 쉼표 포함, 1원 단위까지 정확히 인용하세요. (예: 20,377,728원)
3. 표 데이터는 '항목-산출식-금액'의 논리를 끝까지 추적하여 정확히 연결하세요.
4. 세부 항목 합계와 문서의 '총계'가 일치하는지 반드시 검산하세요.
5. [참고 정보]에 없는 내용은 "문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요.
6. 답변 시 가독성을 위해 표(Table) 형식을 적극 활용하세요.
7. 답변 끝에는 참고한 파일명을 언급하세요."""

    print("\n[3/3] ✅ 준비 완료! 질문을 입력하세요. (종료: quit)")
    print("\n💡 추천 질문:")
    print("   - 대한민국역사박물관 예산의 세부 항목을 표로 정리해줘")
    print("   - 인건비 산출 내역을 상세히 알려줘")
    print()

    while True:
        query = input("\n질문: ")
        if query.lower() in ["quit", "exit"]:
            print("👋 종료합니다.")
            break

        print("   🔍 문서 정밀 검색 중...", end="", flush=True)
        # 16k 컨텍스트에 맞춰 5개로 제한
        results = collection.query(
            query_texts=[query],
            n_results=5 
        )
        
        retrieved_docs = results['documents'][0]
        retrieved_metas = results['metadatas'][0]
        
        if not retrieved_docs:
            print(" 관련 문서를 찾지 못했습니다.")
            continue

        # 검색된 내용 조합 (출처 포함)
        context_text = ""
        sources = set()
        for doc, meta in zip(retrieved_docs, retrieved_metas):
            if meta is None:
                meta = {}
            source = meta.get('source', 'unknown')
            sources.add(source)
            context_text += f"[출처: {source}]\n{doc}\n\n"
            
        print(f" 완료! (참고 문서: {len(retrieved_docs)}개 조각)")

        augmented_prompt = f"""아래 정보를 면밀히 분석하여 질문에 아주 상세하게 답변해 주세요.

[참고 정보]
{context_text}

[질문]
{query}"""

        print("   🤖 AI 분석 중:\n")
        
        try:
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": augmented_prompt}
                ],
                temperature=0.0,  # 사실 기반 고정 (예산 분석용)
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            
            print(f"\n\n   📄 참고 파일: {', '.join(sources)}\n")
            
        except Exception as e:
            print(f"\n❌ 오류: {e}")
            print("💡 서버 연결을 확인하세요. SSH 터널링이 켜져 있나요?\n")

if __name__ == "__main__":
    main()
