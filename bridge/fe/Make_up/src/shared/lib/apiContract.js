/**
 * Python 백엔드 ↔ React 프론트엔드 API 계약 (Contract)
 *
 * 이 파일은 pywebview를 통해 호출되는 Python 함수들의
 * 입출력 스키마를 정의합니다.
 * 백엔드 개발 시 이 스키마에 맞춰 반환값을 구성하세요.
 *
 * 호출 방식: callPython('메서드명', ...args)
 */

// ─── 공통 타입 ────────────────────────────────────

/**
 * @typedef {Object} FileNode
 * @property {string}      id       - 파일 고유 ID
 * @property {string}      name     - 파일명 (예: '01_기본계획수립(기안).hwp')
 * @property {string|null} date     - ISO 날짜 'YYYY-MM-DD' 또는 null
 * @property {number|null} amount   - 금액(원) 또는 null
 * @property {string}      docType  - 문서 유형: '기안'|'입찰공고'|'계약서'|'지출결의서'|'설계변경'|'청렴서약서'|'검수조서'|'심의'|'통보'|'folder'
 * @property {string|null} summary  - AI 요약 텍스트
 * @property {string[]}    parties  - 관련 당사자 목록
 * @property {string[]}    keywords - 핵심 키워드
 * @property {FileNode[]|null} children - 하위 파일 (폴더인 경우), 파일이면 null
 */

/**
 * @typedef {Object} TimelineEvent
 * @property {string}      date        - ISO 날짜
 * @property {string}      label       - 이벤트 제목
 * @property {string}      description - 상세 설명
 * @property {string}      phaseId     - 연결된 phase ID
 * @property {string}      fileId      - 연결된 파일 ID
 * @property {number|null} amount      - 관련 금액
 * @property {boolean}     [highlight] - 강조 표시 여부
 */

/**
 * @typedef {Object} Issue
 * @property {'error'|'warn'|'info'} level       - 심각도
 * @property {string}                title       - 제목
 * @property {string}                description - 설명
 * @property {string}                suggestion  - 제안 조치
 */

/**
 * @typedef {Object} ProjectSummary
 * @property {{ title, description, period, budget, status }} overview
 * @property {{ phases: Array<{id, name, color}>, events: TimelineEvent[] }} timeline
 * @property {Array<{ date, title, description, impact, relatedFileIds }>} decisions
 * @property {Issue[]} issues
 * @property {Array<{ title, items: string[] }>} guidelines
 * @property {Array<{ fileId, reason }>} keyFiles
 */

/**
 * @typedef {Object} Project
 * @property {string}         id        - 프로젝트 고유 ID
 * @property {string}         name      - 프로젝트명
 * @property {number}         fileCount - 파일 수
 * @property {FileNode[]}     files     - 파일 트리
 * @property {ProjectSummary} summary   - AI 분석 요약
 */

// ─── API 메서드별 스키마 ──────────────────────────

/**
 * 1. get_projects()
 *    - 인자: 없음
 *    - 반환: Project[]
 */

/**
 * 2. get_project_files(projectId: string)
 *    - 인자: projectId
 *    - 반환: FileNode[]
 */

/**
 * 3. analyze_folder(folderPath: string)
 *    - 인자: 사용자가 선택한 폴더 경로
 *    - 반환: { projects: Project[], totalFiles: number }
 */

/**
 * 4. chat_query(projectId: string, query: string)
 *    - 인자: 프로젝트 ID, 사용자 질문
 *    - 반환: {
 *        answer: string,                          // AI 답변 텍스트
 *        sources: Array<{ fileId, fileName, page }> // 근거 문서 목록
 *      }
 */

/**
 * 5. generate_draft(referenceFile: FileNode, formData: object)
 *    - 인자: 참고 문서 객체, 사용자 입력 폼 데이터
 *    - formData 예시: {
 *        title: '2025 봄꽃축제',
 *        budget: 60000000,
 *        date: '2025-03-01',
 *        notes: '야간 조명 추가'
 *      }
 *    - 반환: {
 *        html: string,       // 생성된 공문 HTML
 *        templateId: string   // 사용된 템플릿 ID
 *      }
 */

export {}
