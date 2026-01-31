"""
공공기관 인수인계 문서 자동 분석 시스템
- 파일 업로드 → 자동 JSON 생성
- 프론트엔드 대시보드 연동 스펙 준수
"""

import json
import os
import glob
import re
from datetime import datetime
from typing import List, Dict, Optional

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from rank_bm25 import BM25Okapi
import numpy as np

# ============== 설정 ==============
BASE_URL = "http://localhost:8000/v1"
API_KEY = "EMPTY"
MODEL_NAME = "mistralai/Mistral-Nemo-Instruct-2407"

CHROMA_DB_PATH = "./chroma_db_auto"
DATA_DIR = "./my_data"
OUTPUT_DIR = "./outputs"
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
1) 기획: 기본계획 수립 → 예산 확보
2) 계약: 사업자 선정 → 계약 체결
3) 집행: 사업 수행 → 중간점검
4) 정산: 검수 → 대금 지급 → 사업 종료

### 3. 주요 법령 및 규정
- 「국가재정법」: 예산 편성 및 집행
- 「국가를 당사자로 하는 계약에 관한 법률」
- 「공공기관의 운영에 관한 법률」
- 「정부업무평가 기본법」

### 4. 이슈 분류 기준
- 🔴 critical: 법령 위반, 금액 오류, 계약 위반
- 🟡 warn: 절차 누락, 서류 미비, 변경사항
- 🔵 info: 참고사항, 권고사항
"""


class DocumentAnalyzer:
    """문서 자동 분석기"""
    
    # 문서 유형별 페이즈 매핑
    DOC_TYPE_TO_PHASE = {
        "기안": "plan",
        "계획": "plan", 
        "예산": "plan",
        "계약": "contract",
        "용역": "contract",
        "입찰": "contract",
        "검수": "execute",
        "납품": "execute",
        "집행": "execute",
        "정산": "close",
        "결산": "close"
    }
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or BASE_URL
        self.client = OpenAI(base_url=self.base_url, api_key=API_KEY)
        self.collection = None
        self.files_data = []
        
    def setup(self):
        """시스템 초기화"""
        print("=" * 70)
        print("🏛️ 공공기관 인수인계 자동 분석 시스템")
        print("=" * 70)
        
        # 서버 연결 확인
        print("[1/3] vLLM 서버 연결 확인...", end="", flush=True)
        try:
            self.client.models.list()
            print(" ✅")
        except Exception as e:
            print(f" ❌\n{e}")
            return False
        
        # ChromaDB 설정
        print("[2/3] ChromaDB 초기화...", end="", flush=True)
        ko_embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask"
        )
        db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = db_client.get_or_create_collection(
            "auto_analysis", embedding_function=ko_embedding
        )
        print(" ✅")
        
        # 출력 폴더 생성
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        print("[3/3] 준비 완료!")
        return True
    
    def analyze_all(self) -> Dict:
        """모든 문서 자동 분석하여 JSON 생성"""
        print("\n📂 문서 분석 시작...")
        
        # 1. 문서 로드 및 파싱
        self._load_and_parse_documents()
        
        if not self.files_data:
            print("⚠️ 분석할 문서가 없습니다. my_data/ 폴더에 파일을 넣어주세요.")
            return {}
        
        # 2. 구조화된 데이터 생성
        project_data = self._build_project_structure()
        
        # 3. JSON 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{OUTPUT_DIR}/analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 분석 완료! JSON 저장됨: {filename}")
        
        return project_data
    
    def _load_and_parse_documents(self):
        """문서 로드 및 파싱"""
        from local_rag import (
            read_pdf, read_docx, read_excel, read_hwp, read_hwpx,
            read_text_file, split_text
        )
        
        loaders = {
            ".pdf": read_pdf, ".docx": read_docx, ".xlsx": read_excel,
            ".xls": read_excel, ".hwp": read_hwp, ".hwpx": read_hwpx,
            ".txt": read_text_file, ".md": read_text_file
        }
        
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            return
        
        all_files = glob.glob(os.path.join(DATA_DIR, "*.*"))
        self.files_data = []
        
        for idx, file_path in enumerate(all_files):
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in loaders:
                continue
            
            try:
                content = loaders[ext](file_path)
                if not content or len(content.strip()) < 10:
                    continue
                
                filename = os.path.basename(file_path)
                file_id = f"file-{idx + 1}"
                
                # 문서 분석
                doc_info = self._analyze_single_document(
                    file_id, filename, content
                )
                
                self.files_data.append(doc_info)
                print(f"   ✅ {filename}")
                
                # ChromaDB에 저장 (검색용)
                chunks = split_text(content, chunk_size=1500, overlap=300)
                for j, chunk in enumerate(chunks):
                    self.collection.upsert(
                        documents=[chunk],
                        metadatas=[{"fileId": file_id, "source": filename}],
                        ids=[f"{filename}_chunk_{j}"]
                    )
                    
            except Exception as e:
                print(f"   ❌ {os.path.basename(file_path)}: {e}")
        
        print(f"\n   📚 총 {len(self.files_data)}개 파일 분석 완료")
    
    def _analyze_single_document(self, file_id: str, filename: str, content: str) -> Dict:
        """단일 문서 분석"""
        
        # 문서 유형 추론
        doc_type = self._infer_doc_type(filename, content)
        
        # 날짜 추출
        date = self._extract_date(content)
        
        # 금액 추출
        amount = self._extract_amount(content)
        
        # 관련 업체/당사자 추출
        parties = self._extract_parties(content)
        
        # 키워드 추출
        keywords = self._extract_keywords(content)
        
        # 요약 생성 (content는 포함하지 않음 - 프론트엔드 스펙)
        summary = self._generate_summary(content[:2000])
        
        return {
            "id": file_id,
            "name": filename,
            "docType": doc_type,
            "date": date,
            "amount": amount,
            "parties": parties,
            "summary": summary,
            "keywords": keywords
        }
    
    def _infer_doc_type(self, filename: str, content: str) -> str:
        """문서 유형 추론"""
        name_lower = filename.lower()
        content_lower = content[:500].lower()
        
        type_keywords = {
            "기안": ["기안", "품의"],
            "계획": ["계획", "기본계획", "수립"],
            "계약": ["계약서", "계약", "용역"],
            "검수": ["검수", "납품", "검사"],
            "정산": ["정산", "결산", "종료"]
        }
        
        for doc_type, keywords in type_keywords.items():
            if any(kw in name_lower or kw in content_lower for kw in keywords):
                return doc_type
        
        return "일반"
    
    def _extract_date(self, content: str) -> str:
        """날짜 추출"""
        patterns = [
            r'(\d{4})[-./년]\s*(\d{1,2})[-./월]\s*(\d{1,2})',
            r'(\d{4})(\d{2})(\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                y, m, d = match.groups()
                return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        
        return ""
    
    def _extract_amount(self, content: str) -> Optional[int]:
        """금액 추출"""
        # 천 단위 쉼표 포함 금액 패턴
        patterns = [
            r'(\d{1,3}(?:,\d{3})+)\s*원',
            r'금\s*(\d{1,3}(?:,\d{3})+)\s*원',
            r'총\s*(\d{1,3}(?:,\d{3})+)\s*원'
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    amount = int(match.replace(',', ''))
                    if amount >= 10000:  # 1만원 이상만
                        amounts.append(amount)
                except:
                    pass
        
        return max(amounts) if amounts else None
    
    def _extract_parties(self, content: str) -> List[str]:
        """관련 업체/당사자 추출"""
        patterns = [
            r'\(주\)\s*([가-힣a-zA-Z]+)',
            r'주식회사\s*([가-힣a-zA-Z]+)',
            r'([가-힣]+)\s*(?:주식회사|㈜)'
        ]
        
        parties = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            parties.update(matches)
        
        return list(parties)[:5]  # 최대 5개
    
    def _extract_keywords(self, content: str) -> List[str]:
        """키워드 추출 (간단 버전)"""
        # 자주 등장하는 명사 추출 (간단한 방식)
        content = re.sub(r'[^\w\s]', ' ', content)
        words = content.split()
        
        # 2글자 이상 한글 단어
        korean_words = [w for w in words if re.match(r'^[가-힣]{2,}$', w)]
        
        # 빈도 계산
        from collections import Counter
        word_counts = Counter(korean_words)
        
        # 불용어 제거
        stopwords = {'있는', '하는', '되는', '이', '그', '저', '것', '수', '등', '및', '또는'}
        keywords = [word for word, _ in word_counts.most_common(20) 
                   if word not in stopwords and len(word) >= 2]
        
        return keywords[:10]
    
    def _generate_summary(self, content: str) -> str:
        """AI 요약 생성"""
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "문서의 핵심 내용을 1-2문장으로 요약하세요. 금액이 있으면 포함하세요."},
                    {"role": "user", "content": content}
                ],
                max_tokens=100,
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except:
            return content[:100] + "..."
    
    def _build_project_structure(self) -> Dict:
        """프론트엔드 스펙에 맞는 구조 생성"""

        # 1. 파일을 폴더 구조로 그룹화
        folders = self._group_files_by_phase()

        # 2. 타임라인 생성
        timeline = self._build_timeline()

        # 3. 이슈 분석
        issues = self._analyze_issues()

        # 4. 프로젝트명 추론
        project_name = self._infer_project_name()

        # 5. overview 생성
        overview = self._build_overview(project_name)

        # 6. 의사결정 추출
        decisions = self._extract_decisions()

        # 7. 가이드라인 생성
        guidelines = self._build_guidelines()

        # 8. 주요 문서 선정
        key_files = self._select_key_files()

        # 최종 구조 (프론트엔드 전체 스펙 준수)
        return {
            "id": f"proj-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": project_name,
            "fileCount": len(self.files_data),
            "files": folders,  # 트리 구조
            "summary": {
                "overview": overview,
                "timeline": timeline,
                "decisions": decisions,
                "issues": issues,
                "guidelines": guidelines,
                "keyFiles": key_files,
                "totalAmount": sum(f.get("amount") or 0 for f in self.files_data),
                "dateRange": self._get_date_range()
            }
        }
    
    def _group_files_by_phase(self) -> List[Dict]:
        """파일을 페이즈별 폴더 구조로 그룹화"""
        phase_folders = {
            "plan": {"name": "01_기획", "children": []},
            "contract": {"name": "02_계약", "children": []},
            "execute": {"name": "03_집행", "children": []},
            "close": {"name": "04_정산", "children": []},
            "etc": {"name": "05_기타", "children": []}
        }
        
        for file in self.files_data:
            doc_type = file.get("docType", "일반")
            
            # 문서 유형에서 페이즈 결정
            phase = "etc"
            for keyword, phase_id in self.DOC_TYPE_TO_PHASE.items():
                if keyword in doc_type:
                    phase = phase_id
                    break
            
            # content 제외 (프론트엔드 스펙)
            file_info = {k: v for k, v in file.items() if k != "content"}
            phase_folders[phase]["children"].append(file_info)
        
        # 빈 폴더 제외하고 반환
        return [folder for folder in phase_folders.values() if folder["children"]]
    
    def _build_timeline(self) -> Dict:
        """타임라인 생성"""
        phases = [
            {"id": "plan", "name": "기획", "color": "#3b82f6"},
            {"id": "contract", "name": "계약", "color": "#8b5cf6"},
            {"id": "execute", "name": "집행", "color": "#10b981"},
            {"id": "close", "name": "정산", "color": "#f59e0b"},
            {"id": "etc", "name": "기타", "color": "#6b7280"},
        ]

        events = []
        for file in self.files_data:
            doc_type = file.get("docType", "일반")

            # 페이즈 결정
            phase_id = "etc"
            for keyword, pid in self.DOC_TYPE_TO_PHASE.items():
                if keyword in doc_type:
                    phase_id = pid
                    break

            # 하이라이트 결정 (중요 이벤트)
            highlight = any(kw in file.get("name", "") for kw in ["변경", "추가", "정정"])

            # 라벨: 파일명에서 확장자 제거, 번호 접두사 정리
            raw_name = os.path.splitext(file["name"])[0]
            # "01_기본계획수립(기안)" → "기본계획수립(기안)" (앞의 번호_ 제거)
            label = re.sub(r'^\d+[_.\-]\s*', '', raw_name)
            if not label:
                label = raw_name

            # 날짜가 없는 파일도 이벤트에 포함 (날짜 없음 표시)
            event_date = file.get("date", "")

            events.append({
                "date": event_date,
                "label": label,
                "description": file.get("summary", "")[:100],
                "phaseId": phase_id,
                "fileId": file["id"],
                "amount": file.get("amount"),
                "highlight": highlight,
            })

        # 날짜 있는 것 먼저, 날짜순 정렬. 날짜 없는 것은 뒤에
        dated = [e for e in events if e["date"]]
        undated = [e for e in events if not e["date"]]
        dated.sort(key=lambda x: x["date"])

        return {"phases": phases, "events": dated + undated}
    
    def _build_overview(self, project_name: str) -> Dict:
        """프로젝트 개요 생성 (프론트엔드 overview 스펙)"""
        date_range = self._get_date_range()
        total_amount = sum(f.get("amount") or 0 for f in self.files_data)

        # LLM으로 설명 생성
        description = ""
        try:
            file_list = "\n".join(
                f"- {f['name']} ({f.get('docType', '일반')}): {f.get('summary', '')[:60]}"
                for f in self.files_data[:10]
            )
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "문서 목록을 보고 이 업무/프로젝트를 2~3문장으로 설명하세요. 한국어로 답하세요."},
                    {"role": "user", "content": f"프로젝트: {project_name}\n\n문서 목록:\n{file_list}"}
                ],
                max_tokens=150,
                temperature=0.0
            )
            description = response.choices[0].message.content.strip()
        except Exception:
            description = f"{len(self.files_data)}개 문서로 구성된 업무입니다."

        period = ""
        if date_range.get("start") and date_range.get("end"):
            period = f"{date_range['start']} ~ {date_range['end']}"
        elif date_range.get("start"):
            period = date_range["start"]

        return {
            "title": project_name,
            "description": description,
            "period": period,
            "budget": total_amount,
            "status": "unknown",
        }

    def _extract_decisions(self) -> List[Dict]:
        """주요 의사결정 추출 (변경, 추가, 정정 등)"""
        decisions = []
        for file in self.files_data:
            name = file.get("name", "")
            if any(kw in name for kw in ["변경", "추가", "정정", "수정", "증액", "감액"]):
                decisions.append({
                    "date": file.get("date", ""),
                    "title": os.path.splitext(name)[0],
                    "description": file.get("summary", "")[:150],
                    "impact": f"{file['amount']:,}원" if file.get("amount") else "",
                    "relatedFileIds": [file["id"]],
                })
        return decisions

    def _build_guidelines(self) -> List[Dict]:
        """가이드라인 생성"""
        items = []

        # 이슈 기반 가이드라인
        doc_types = [f.get("docType", "") for f in self.files_data]
        if "계약" in doc_types:
            items.append("계약 관련 문서의 유효기간 및 변경사항을 확인하세요.")
        if any("변경" in name for name in [f.get("name", "") for f in self.files_data]):
            items.append("변경 문서가 있습니다. 변경 사유와 승인 여부를 확인하세요.")

        dates_missing = sum(1 for f in self.files_data if not f.get("date"))
        if dates_missing > 0:
            items.append(f"{dates_missing}개 문서에서 날짜를 추출하지 못했습니다. 수동으로 확인하세요.")

        if not items:
            items.append("각 문서의 작성일과 금액을 교차 확인하세요.")
            items.append("누락된 후속 문서가 있는지 점검하세요.")

        return [{"title": "후속 업무", "items": items}]

    def _select_key_files(self) -> List[Dict]:
        """주요 문서 선정"""
        key_files = []

        # 금액이 큰 순으로 상위 3개
        files_with_amount = [f for f in self.files_data if f.get("amount")]
        files_with_amount.sort(key=lambda x: x["amount"], reverse=True)

        for f in files_with_amount[:3]:
            reason = f"금액 {f['amount']:,}원 — {f.get('docType', '문서')}"
            key_files.append({"fileId": f["id"], "reason": reason})

        # 금액 없으면 첫 번째 파일이라도
        if not key_files and self.files_data:
            f = self.files_data[0]
            key_files.append({"fileId": f["id"], "reason": "첫 번째 문서"})

        return key_files

    def _analyze_issues(self) -> List[Dict]:
        """이슈 자동 분석"""
        issues = []
        
        for file in self.files_data:
            name = file.get("name", "")
            doc_type = file.get("docType", "")
            
            # 변경계약 관련
            if "변경" in name or "수정" in name:
                issues.append({
                    "level": "warn",
                    "title": "변경사항 감지",
                    "description": f"{name}에서 변경 관련 내용이 확인됩니다.",
                    "suggestion": "변경 사유 및 승인 여부를 확인하세요.",
                    "relatedFileIds": [file["id"]]
                })
            
            # 금액 관련 (고액)
            amount = file.get("amount")
            if amount and amount >= 100000000:  # 1억 이상
                issues.append({
                    "level": "info",
                    "title": "고액 거래 확인",
                    "description": f"{name}에서 {amount:,}원 규모의 금액이 확인됩니다.",
                    "suggestion": "결재 권한 및 계약 방식을 검토하세요.",
                    "relatedFileIds": [file["id"]]
                })
            
            # 날짜 누락
            if not file.get("date"):
                issues.append({
                    "level": "warn",
                    "title": "일자 정보 누락",
                    "description": f"{name}에서 날짜 정보를 찾을 수 없습니다.",
                    "suggestion": "문서의 작성일 또는 시행일을 확인하세요.",
                    "relatedFileIds": [file["id"]]
                })
        
        return issues
    
    def _infer_project_name(self) -> str:
        """프로젝트명 추론"""
        # 첫 번째 파일의 키워드에서 추론
        if self.files_data:
            keywords = self.files_data[0].get("keywords", [])
            if keywords:
                return " ".join(keywords[:3]) + " 인수인계"
        
        return f"인수인계 프로젝트 {datetime.now().strftime('%Y%m%d')}"
    
    def _get_date_range(self) -> Dict:
        """날짜 범위 계산"""
        dates = [f["date"] for f in self.files_data if f.get("date")]
        
        if not dates:
            return {"start": "", "end": ""}
        
        return {
            "start": min(dates),
            "end": max(dates)
        }
    
    def query(self, question: str) -> Dict:
        """질문 답변 (기존 기능 유지)"""
        # ChromaDB 검색
        results = self.collection.query(
            query_texts=[question],
            n_results=5
        )
        
        if not results['documents'][0]:
            return {"answer": "관련 문서를 찾을 수 없습니다."}
        
        context = "\n\n".join(results['documents'][0])
        
        # AI 응답
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": f"인수인계 전문가입니다.\n{PUBLIC_INSTITUTION_GUIDELINES}"},
                    {"role": "user", "content": f"참고:\n{context}\n\n질문: {question}"}
                ],
                temperature=0.0
            )
            
            return {
                "question": question,
                "answer": response.choices[0].message.content,
                "sources": [m.get("source") for m in results['metadatas'][0]]
            }
        except Exception as e:
            return {"error": str(e)}


def main():
    print("\n🚀 문서 자동 분석 시스템 시작...\n")
    
    analyzer = DocumentAnalyzer()
    
    if not analyzer.setup():
        return
    
    # 자동 분석 실행
    print("\n" + "=" * 70)
    print("📊 문서 자동 분석을 시작합니다...")
    print("=" * 70)
    
    result = analyzer.analyze_all()
    
    if result:
        print("\n" + "=" * 70)
        print("📋 분석 결과 요약")
        print("=" * 70)
        print(f"   프로젝트: {result.get('name', 'N/A')}")
        print(f"   파일 수: {result.get('fileCount', 0)}개")
        print(f"   이슈: {len(result.get('summary', {}).get('issues', []))}개")
        
        if result.get('summary', {}).get('totalAmount'):
            print(f"   총 금액: {result['summary']['totalAmount']:,}원")
        
        date_range = result.get('summary', {}).get('dateRange', {})
        if date_range.get('start'):
            print(f"   기간: {date_range['start']} ~ {date_range['end']}")
        
        print("=" * 70)
        
        print("\n✅ JSON 분석 완료!")
        print("\n💡 챗봇 기능을 사용하려면:")
        print("   python handover_rag_v3.py")


if __name__ == "__main__":
    main()
