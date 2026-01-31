import os
import sys
import threading
import glob
import requests
from datetime import datetime
from typing import List, Optional

# 중앙 설정 및 코어 모듈 로드
import config
from core.analyzer import analyze_folder_interface
from core.adapter import adapt_be_list_to_fe

class BridgeAPI:
    """
    Frontend(React)와 Backend(Python)를 연결하는 핵심 브릿지 클래스
    Local Logic과 Remote AI Server를 통합
    """
    def __init__(self):
        self.is_processing = False
        self._projects_cache = {}  # 분석 결과 캐시 {project_id: project_data}
        self._analysis_status = {}  # {project_id: 'pending'|'analyzing'|'done'|'error'}
        print(f"[Bridge] 초기화 완료 (Server: {config.BRIDGE_API_URL})")

    def _safe_json(self, data):
        """PyWebView 직렬화 안전성 확보"""
        import json
        return json.loads(json.dumps(data, default=str, ensure_ascii=False))

    def _upload_files_to_remote(self, path: str):
        """폴더 내 파일을 원격 서버로 업로드"""
        print(f"[Bridge] Remote Upload 시작: {path}")
        files_to_upload = []
        for ext in config.SUPPORTED_EXTENSIONS:
            files_to_upload.extend(glob.glob(os.path.join(path, ext)))
        
        if not files_to_upload:
            print("[Bridge] 업로드할 파일 없음")
            return

        files = []
        try:
            for file_path in files_to_upload:
                filename = os.path.basename(file_path)
                files.append(('files', (filename, open(file_path, 'rb'))))
            
            # verify=False는 개발 단계에서 SSL 문제 회피용
            response = requests.post(
                f"{config.BRIDGE_API_URL}/upload", 
                files=files, 
                timeout=300
            ) 
            
            if response.status_code == 200:
                print(f"[Bridge] Upload 성공: {len(files)}개 파일")
            else:
                print(f"[Bridge] Upload 실패: {response.text}")
                
        except Exception as e:
            print(f"[Bridge] Upload 중 오류: {e}")
        finally:
            for _, (_, f) in files:
                f.close()

    def _merge_remote_result(self, project_id, ai_result):
        """원격 AI 분석 결과를 캐시된 프로젝트에 병합"""
        project = self._projects_cache.get(project_id)
        if not project:
            return

        # AI가 생성한 summary(타임라인, 이슈, 총금액 등) 병합
        summary = ai_result.get("summary", {})

        ai_name = ai_result.get("name")
        if ai_name:
            project["name"] = ai_name

        # AI가 생성한 파일별 정보(요약, 키워드 등) 병합
        # + AI fileId → 로컬 fileId 매핑 테이블 구축
        ai_files = {}          # name → ai_file_data
        ai_id_to_local = {}    # ai_file_id → local_file_id

        for folder in ai_result.get("files", []):
            if isinstance(folder, dict):
                for f in folder.get("children", []):
                    if isinstance(f, dict) and "name" in f:
                        ai_files[f["name"]] = f
                if "name" in folder and "children" not in folder:
                    ai_files[folder["name"]] = folder

        # 로컬 파일과 이름으로 매칭하여 ID 매핑
        for fe_file in project.get("files", []):
            ai_file = ai_files.get(fe_file.get("name"))
            if ai_file:
                if ai_file.get("id"):
                    ai_id_to_local[ai_file["id"]] = fe_file["id"]
                if ai_file.get("summary"):
                    fe_file["summary"] = ai_file["summary"]
                if ai_file.get("keywords"):
                    fe_file["keywords"] = ai_file["keywords"]
                if ai_file.get("parties"):
                    fe_file["parties"] = ai_file["parties"]

        # summary 내 모든 fileId 참조를 로컬 ID로 변환
        if ai_id_to_local:
            self._remap_file_ids(summary, ai_id_to_local)

        project["summary"] = summary
        print(f"[Bridge] 원격 결과 병합 완료 (project: {project_id}, ID매핑: {len(ai_id_to_local)}건)")

    @staticmethod
    def _remap_file_ids(obj, id_map):
        """summary 내 fileId/relatedFileIds 참조를 로컬 ID로 재매핑"""
        if isinstance(obj, dict):
            # fileId 필드
            if "fileId" in obj and obj["fileId"] in id_map:
                obj["fileId"] = id_map[obj["fileId"]]
            # relatedFileIds 필드
            if "relatedFileIds" in obj and isinstance(obj["relatedFileIds"], list):
                obj["relatedFileIds"] = [
                    id_map.get(fid, fid) for fid in obj["relatedFileIds"]
                ]
            for v in obj.values():
                BridgeAPI._remap_file_ids(v, id_map)
        elif isinstance(obj, list):
            for item in obj:
                BridgeAPI._remap_file_ids(item, id_map)

    def get_analysis_status(self, project_id: str) -> dict:
        """AI 분석 상태 조회 (FE 폴링용)"""
        status = self._analysis_status.get(project_id, 'unknown')
        result = {"status": status, "projectId": project_id}

        if status == 'done':
            result["project"] = self._projects_cache.get(project_id)

        return self._safe_json(result)

    def analyze_folder(self, path: str) -> dict:
        """폴더를 분석하고 결과를 FE에 반환"""
        if self.is_processing:
            return {"error": "현재 처리 중입니다."}
            
        self.is_processing = True
        print(f"[Bridge] 폴더 분석 요청: {path}")
        
        try:
            # 1. 문서 분석 (BE 로컬 파서) - UI 즉각 반응용
            be_results = analyze_folder_interface(path)
            fe_results = adapt_be_list_to_fe(be_results)

            # 2. 문서 검증 (Rule Engine - 누락 탐지)
            validation = {"status": "ok", "warnings": [], "errors": [], "summary": ""}
            try:
                from be.core.rules import DocumentValidator
                validator = DocumentValidator(be_results)
                validation = validator.validate_all()
                print(f"[Bridge] 검증 결과: {validation['summary']}")

                # 검증 경고를 관련 파일의 status/message에 병합
                for warning in validation.get('warnings', []) + validation.get('errors', []):
                    msg = warning.get('message', '')
                    severity = warning.get('severity', 'warning')
                    # 모든 파일에 프로젝트 레벨 경고 표시 (첫 번째 파일에 부착)
                    if fe_results:
                        fe_results[0]['status'] = 'warning'
                        existing = fe_results[0].get('message', '')
                        prefix = '🚨' if severity == 'error' else '⚠️'
                        new_msg = f"{prefix} {msg}"
                        fe_results[0]['message'] = f"{existing}\n{new_msg}".strip() if existing else new_msg
            except ImportError:
                print("[Bridge] DocumentValidator 로드 실패 - 검증 생략")

            # 3. 프로젝트 데이터 구성 및 캐시 (1차: 로컬 파싱 결과)
            project_id = os.path.basename(path)
            project_data = {
                "id": project_id,
                "name": project_id,
                "fileCount": len(fe_results),
                "warnings": sum(1 for d in fe_results if d['status'] == 'warning'),
                "files": fe_results,
                "validation": validation,
                "summary": None,  # AI 분석 전이므로 null
            }
            self._projects_cache[project_id] = project_data
            self._analysis_status[project_id] = 'pending'

            # 4. Remote AI Sync (백그라운드 비동기 + 서버 폴링)
            def background_analyze():
                self._analysis_status[project_id] = 'analyzing'
                try:
                    # 4-1. 파일 업로드
                    self._upload_files_to_remote(path)

                    # 4-2. 분석 요청 → 신버전: task_id 즉시 반환 / 구버전: 동기 응답
                    #       524(Cloudflare timeout) 등 프록시 오류 시 재시도
                    import time as _time
                    max_analyze_retries = 3
                    response = None
                    for attempt in range(max_analyze_retries):
                        try:
                            print(f"[Bridge] Remote Analyze 요청 (project: {project_id}, 시도 {attempt+1}/{max_analyze_retries})...")
                            response = requests.post(
                                f"{config.BRIDGE_API_URL}/analyze",
                                timeout=60,
                            )
                            if response.status_code == 200:
                                break
                            # 524(프록시 타임아웃), 502, 503 등은 재시도
                            if response.status_code in (502, 503, 504, 524) and attempt < max_analyze_retries - 1:
                                print(f"[Bridge] AI 분석 요청 {response.status_code}, {10*(attempt+1)}초 후 재시도...")
                                _time.sleep(10 * (attempt + 1))
                                continue
                            # 그 외 에러는 바로 실패
                            self._analysis_status[project_id] = 'error'
                            print(f"[Bridge] AI 분석 요청 실패: {response.status_code}")
                            return
                        except requests.exceptions.ConnectionError:
                            if attempt < max_analyze_retries - 1:
                                print(f"[Bridge] 서버 연결 실패, {10*(attempt+1)}초 후 재시도...")
                                _time.sleep(10 * (attempt + 1))
                                continue
                            self._analysis_status[project_id] = 'error'
                            print(f"[Bridge] AI 서버 연결 불가 (project: {project_id})")
                            return
                        except requests.exceptions.ReadTimeout:
                            if attempt < max_analyze_retries - 1:
                                print(f"[Bridge] 분석 요청 타임아웃, {10*(attempt+1)}초 후 재시도...")
                                _time.sleep(10 * (attempt + 1))
                                continue
                            self._analysis_status[project_id] = 'error'
                            print(f"[Bridge] AI 분석 요청 타임아웃 (project: {project_id})")
                            return

                    if response is None or response.status_code != 200:
                        self._analysis_status[project_id] = 'error'
                        print(f"[Bridge] AI 분석 요청 최종 실패 (project: {project_id})")
                        return

                    resp_data = response.json()
                    task_id = resp_data.get("task_id")

                    if not task_id:
                        # 서버가 동기 방식으로 직접 결과 반환한 경우 (구버전 호환)
                        if resp_data.get("success") and resp_data.get("result"):
                            self._merge_remote_result(project_id, resp_data["result"])
                            self._analysis_status[project_id] = 'done'
                            print(f"[Bridge] AI 분석 완료 — 동기 응답 (project: {project_id})")
                        else:
                            self._analysis_status[project_id] = 'error'
                        return

                    # 4-3. 서버 폴링: /analyze/status/{task_id}
                    import time
                    print(f"[Bridge] AI 분석 작업 시작됨 (task: {task_id}), 폴링 시작...")
                    max_polls = 120  # 최대 10분 (5초 × 120)
                    for i in range(max_polls):
                        time.sleep(5)
                        try:
                            status_resp = requests.get(
                                f"{config.BRIDGE_API_URL}/analyze/status/{task_id}",
                                timeout=10,
                            )
                            if status_resp.status_code != 200:
                                continue

                            status_data = status_resp.json()
                            status = status_data.get("status")

                            if status == "done":
                                ai_result = status_data.get("result", {})
                                self._merge_remote_result(project_id, ai_result)
                                self._analysis_status[project_id] = 'done'
                                print(f"[Bridge] AI 분석 완료 (project: {project_id}, poll: {i+1})")
                                return
                            elif status == "error":
                                self._analysis_status[project_id] = 'error'
                                print(f"[Bridge] AI 분석 서버 오류: {status_data.get('error')}")
                                return
                            # pending / running → 계속 폴링
                        except Exception as poll_err:
                            print(f"[Bridge] 폴링 오류 (재시도): {poll_err}")

                    # 폴링 제한 초과
                    self._analysis_status[project_id] = 'error'
                    print(f"[Bridge] AI 분석 시간 초과 (project: {project_id})")

                except Exception as e:
                    self._analysis_status[project_id] = 'error'
                    print(f"[Bridge] AI 분석 중 예외: {e}")

            threading.Thread(target=background_analyze, daemon=True).start()

            # 5. 1차 결과 즉시 반환
            return self._safe_json({
                "projects": [project_data],
                "totalFiles": len(fe_results),
            })
        except Exception as e:
            print(f"[Bridge] 분석 중 오류: {e}")
            return {"error": "분석 실패", "detail": str(e)}
        finally:
            self.is_processing = False

    def search_documents(self, query: str) -> dict:
        """AI 엔진에 질문 쿼리 (Remote) — 재시도 포함"""
        import time

        max_retries = 2
        timeout_secs = 180  # RAG 엔진 첫 초기화 시 시간이 오래 걸림

        for attempt in range(max_retries + 1):
            try:
                print(f"[Bridge] Chat 요청 (시도 {attempt + 1}/{max_retries + 1}): {query}")

                # 서버 상태 사전 확인 (빠른 실패)
                try:
                    health = requests.get(
                        f"{config.BRIDGE_API_URL}/health",
                        timeout=10
                    )
                    if health.status_code != 200:
                        print(f"[Bridge] 서버 헬스체크 실패: {health.status_code}")
                except requests.exceptions.ConnectionError:
                    return self._safe_json({
                        "answer": "AI 서버에 연결할 수 없습니다.\nRunPod 인스턴스가 실행 중인지 확인해주세요.",
                        "sources": []
                    })

                response = requests.post(
                    f"{config.BRIDGE_API_URL}/chat",
                    json={"question": query},
                    timeout=timeout_secs
                )

                if response.status_code == 200:
                    remote_data = response.json()
                    answer_text = remote_data.get("answer", "응답 없음")
                    sources = remote_data.get("sources", [])

                    # 서버가 answer를 JSON 문자열로 보낸 경우 텍스트 추출
                    if isinstance(answer_text, str) and answer_text.strip().startswith("{"):
                        try:
                            import json as _json
                            parsed = _json.loads(answer_text)
                            if isinstance(parsed, dict):
                                # 흔한 키에서 텍스트 추출
                                answer_text = (
                                    parsed.get("answer")
                                    or parsed.get("text")
                                    or parsed.get("content")
                                    or parsed.get("summary")
                                    or parsed.get("response")
                                    or answer_text
                                )
                                # sources가 비어 있으면 parsed에서 가져오기
                                if not sources and parsed.get("sources"):
                                    sources = parsed["sources"]
                        except (ValueError, TypeError):
                            pass

                    return self._safe_json({
                        "answer": answer_text,
                        "sources": sources
                    })
                else:
                    error_detail = ""
                    try:
                        error_detail = response.json().get("detail", "")
                    except Exception:
                        error_detail = response.text[:200]

                    # 500 에러는 재시도
                    if response.status_code >= 500 and attempt < max_retries:
                        print(f"[Bridge] 서버 오류 {response.status_code}, 재시도...")
                        time.sleep(3)
                        continue

                    return self._safe_json({
                        "answer": f"서버 오류가 발생했습니다. (HTTP {response.status_code})\n{error_detail}",
                        "sources": []
                    })

            except requests.exceptions.ReadTimeout:
                if attempt < max_retries:
                    print(f"[Bridge] 타임아웃, 재시도 중... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
                return self._safe_json({
                    "answer": "AI 서버 응답 시간이 초과되었습니다.\n잠시 후 다시 시도해주세요. (서버에서 모델을 로딩 중일 수 있습니다)",
                    "sources": []
                })

            except requests.exceptions.ConnectionError:
                return self._safe_json({
                    "answer": "AI 서버에 연결할 수 없습니다.\nRunPod 인스턴스가 실행 중인지 확인해주세요.",
                    "sources": []
                })

            except Exception as e:
                return self._safe_json({
                    "answer": f"오류가 발생했습니다: {e}",
                    "sources": []
                })

        return self._safe_json({
            "answer": "AI 서버 응답에 실패했습니다. 잠시 후 다시 시도해주세요.",
            "sources": []
        })

    def chat_query(self, project_id: str, query: str) -> dict:
        return self.search_documents(query)

    def open_folder_dialog(self) -> Optional[str]:
        """네이티브 폴더 브라우저 열기"""
        import webview
        window = webview.windows[0] if webview.windows else None
        if not window: return None
        
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else None

    def get_projects(self) -> list:
        """캐시된 프로젝트 목록 반환"""
        return self._safe_json(list(self._projects_cache.values()))

    def get_project_files(self, project_id: str) -> list:
        """특정 프로젝트의 파일 목록 반환"""
        project = self._projects_cache.get(project_id)
        if not project:
            return []
        return self._safe_json(project.get('files', []))

    def generate_draft(self, reference_file: dict, form_data: dict) -> dict:
        """기존 문서를 참고하여 공문 초안 생성 (원격 AI 서버 호출)"""
        try:
            title = form_data.get('title', '')
            amount = form_data.get('amount', '')
            date = form_data.get('date', '')
            extra = form_data.get('extra', '')

            ref_name = reference_file.get('name', '') if reference_file else ''
            ref_summary = reference_file.get('summary', '') if reference_file else ''
            ref_amount = reference_file.get('amount') if reference_file else None

            # 캐시에서 참고 문서 원문 찾기
            ref_content = ''
            ref_id = reference_file.get('id', '') if reference_file else ''
            if ref_id:
                for project in self._projects_cache.values():
                    for f in project.get('files', []):
                        if f.get('id') == ref_id:
                            ref_content = f.get('raw_text', '')
                            if not ref_summary:
                                ref_summary = f.get('summary', '')
                            if ref_amount is None:
                                ref_amount = f.get('amount')
                            break
                    if ref_content:
                        break

            # 원격 AI 서버에 공문 생성 요청
            payload = {
                "reference_content": ref_content[:4000],
                "reference_name": ref_name,
                "reference_summary": ref_summary or '',
                "reference_amount": ref_amount,
                "title": title,
                "amount": amount,
                "date": date,
                "extra": extra,
            }

            print(f"[Bridge] 공문 생성 요청: {title} (참고: {ref_name})")
            resp = requests.post(
                f"{config.BRIDGE_API_URL}/draft",
                json=payload,
                timeout=120,
                verify=False,
            )

            if resp.status_code == 200:
                data = resp.json()
                print(f"[Bridge] 공문 생성 완료: templateType={data.get('templateType')}")
                return self._safe_json({
                    "templateType": data.get("templateType", "GOV_ELECTRONIC"),
                    "structured": data.get("structured", {}),
                    "referenceFileName": data.get("referenceFileName") or ref_name or None,
                })
            else:
                print(f"[Bridge] 공문 생성 서버 오류: {resp.status_code}")
                return self._generate_draft_fallback(title, amount, date, extra, ref_name, ref_summary, ref_amount)

        except (requests.ConnectionError, requests.Timeout) as e:
            print(f"[Bridge] 공문 생성 서버 연결 실패: {e}")
            return self._generate_draft_fallback(
                form_data.get('title', ''), form_data.get('amount', ''),
                form_data.get('date', ''), form_data.get('extra', ''),
                reference_file.get('name', '') if reference_file else '',
                reference_file.get('summary', '') if reference_file else '',
                reference_file.get('amount') if reference_file else None,
            )
        except Exception as e:
            print(f"[Bridge] 공문 생성 오류: {e}")
            return {"error": "공문 생성 실패", "detail": str(e)}

    def _generate_draft_fallback(self, title, amount, date, extra, ref_name, ref_summary, ref_amount):
        """AI 서버 연결 실패 시 로컬 폴백 생성"""
        amount_num = int(''.join(c for c in amount if c.isdigit())) if amount else 0
        formatted_amount = f"{amount_num:,}" if amount_num else amount

        return self._safe_json({
            "templateType": "GOV_ELECTRONIC",
            "structured": {
                "slogan": "",
                "institution": "○○시청",
                "title": f"{title} 기본계획 수립(안)",
                "receiver": "수신자 참조",
                "related": "",
                "mainSections": [
                    {
                        "label": "추진배경",
                        "type": "simple",
                        "content": f"{ref_summary or '관련 사업'}과 관련하여 {title}을(를) 아래와 같이 추진하고자 합니다.",
                    },
                    {
                        "label": "사업개요",
                        "type": "detailed",
                        "content": "",
                        "detailItems": [
                            {"label": "사업명", "value": title},
                            {"label": "사업비", "value": f"금{formatted_amount}원"},
                            {"label": "시행일자", "value": date or "-"},
                            {"label": "장소", "value": "○○ 일원"},
                        ],
                    },
                    {
                        "label": "행정사항",
                        "type": "simple",
                        "content": "가. 관련 예산 확보 후 집행\n나. 관련 부서 협조 요청",
                    },
                ],
            },
            "referenceFileName": ref_name or None,
        })

    def ping(self) -> dict:
        return {"status": "ok", "timestamp": datetime.now().isoformat()}
