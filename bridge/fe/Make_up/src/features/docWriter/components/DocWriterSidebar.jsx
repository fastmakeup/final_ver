import { useState, useEffect } from 'react'
import { cn } from '@/shared/utils/cn'

const EXAMPLE_DOCS = [
  {
    id: 1,
    title: '2023 벚꽃 축제 계약서',
    desc: '예산 증액 사유 및 산출 근거 우수 사례',
    highlight: true,
    templateType: 'PLANNING_REPORT',
    data: {
      docTitle: '2023년 벚꽃 축제 계약 변경 계획',
      date: '2023. 3. 15.(수)',
      department: '문화관광과',
      purpose1: '(예산조정) 축제 규모 확대에 따른 추가 예산 확보',
      purpose2: '(사업개선) 관광객 편의 시설 보강 및 안전 관리 강화',
      projectName: '2023년 벚꽃 축제 계약 변경 사업',
      period: '2023. 3. 20. ~ 2023. 4. 30.',
      budget: '50,000천원(부가세 포함)',
    }
  },
  {
    id: 2,
    title: '2023 하반기 도로 정비 공사',
    desc: '공기 연장 및 자재비 변동 반영',
    highlight: false,
    templateType: 'GOV_ELECTRONIC',
    data: {
      slogan: '시민과 함께하는 미래',
      institution: '서울특별시도시관리본부',
      title: '2023년 하반기 도로 정비 공사 일정 변경 안내',
      receiver: '내부결재',
      related: '도로관리과-234(2023.7.15.) ‘2023년 하반기 도로 정비 계획’',
      mainContent: '자재비 변동 및 기상 악화로 인한 공사 기간 연장을 다음과 같이 안내드립니다.',
      period: '2023. 8. 1. ~ 2023. 10. 31.',
      location: '서울시 전역 주요 도로',
    }
  },
]

const CHECKLIST_BY_TYPE = {
  'PLANNING_REPORT': [
    { id: 1, label: '사업 목적 및 기대효과 명시', checked: false },
    { id: 2, label: '예산 산출 내역 세부 작성', checked: false },
    { id: 3, label: '추진 일정 및 단계별 계획 포함', checked: false },
    { id: 4, label: '참고 자료 및 선행 사례 첨부', checked: false },
  ],
  'GOV_ELECTRONIC': [
    { id: 1, label: '발신 및 수신 기관 명확히 명시', checked: false },
    { id: 2, label: '관련 규정 및 근거 법령 표기', checked: false },
    { id: 3, label: '결재선 및 결재자 정보 확인', checked: false },
    { id: 4, label: '문서 번호 및 시행 일자 작성', checked: false },
  ],
  'DEFAULT': [
    { id: 1, label: '변경 전후 금액 대비표 작성', checked: false },
    { id: 2, label: '법인 인감 날인 여부 확인', checked: false },
    { id: 3, label: '귀책 사유 명시 (계약 일반조건 제 5조)', checked: false },
  ],
}

export default function DocWriterSidebar({ 
  hasDraft, 
  onReset, 
  onResetAll, 
  onGenerate, 
  isGenerating, 
  canGenerate, 
  referenceFileName,
  templateType = 'DEFAULT',
  onExampleClick,
  isEditable = true,
  onStartEditing,
  onDownloadPDF,
}) {
  const [checklist, setChecklist] = useState(CHECKLIST_BY_TYPE[templateType] || CHECKLIST_BY_TYPE.DEFAULT)

  // templateType이 변경될 때 checklist 업데이트
  useEffect(() => {
    setChecklist(CHECKLIST_BY_TYPE[templateType] || CHECKLIST_BY_TYPE.DEFAULT)
  }, [templateType])

  const uncheckedCount = checklist.filter(c => !c.checked).length

  function toggleCheck(id) {
    setChecklist(prev =>
      prev.map(item => (item.id === id ? { ...item, checked: !item.checked } : item)),
    )
  }

  return (
    <aside className="w-[380px] flex-none bg-white border-l border-gray-200 flex flex-col z-10">
      {/* 헤더 */}
      <div className="p-6 pb-2">
        <h3 className="text-gray-900 text-lg font-bold leading-tight">미리보기 및 가이드</h3>
        <p className="text-gray-500 text-sm mt-1">작성 전 AI 팁과 유사 사례를 참고하세요.</p>
      </div>

      {/* 스크롤 콘텐츠 */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* 참고 문서 */}
        {referenceFileName && (
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
            <div className="flex gap-2 items-center mb-1">
              <svg className="w-4 h-4 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
              </svg>
              <p className="text-xs font-bold text-primary-600">참고 문서</p>
            </div>
            <p className="text-sm text-gray-700">{referenceFileName}</p>
          </div>
        )}

        {/* 추천 예시 */}
        <div className="space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">
            추천 예시 (Recommended)
          </h4>
          <div className="flex flex-col gap-3">
            {EXAMPLE_DOCS.map(doc => (
              <div
                key={doc.id}
                onClick={() => onExampleClick?.(doc)}
                className="group flex items-start gap-3 p-3 rounded-lg border border-gray-200 bg-gray-50 hover:border-primary-500/50 hover:shadow-md cursor-pointer transition-all"
              >
                <div className="bg-white p-2 rounded border border-gray-100 shrink-0">
                  <svg
                    className={cn('w-5 h-5', doc.highlight ? 'text-primary-500' : 'text-gray-400')}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                    {doc.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{doc.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 구분선 */}
        <div className="h-px bg-gray-100" />

        {/* 필수 포함 항목 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">
              필수 포함 항목 (Checklist)
            </h4>
            {uncheckedCount > 0 && (
              <span className="text-[10px] bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-bold">
                미충족 {uncheckedCount}건
              </span>
            )}
          </div>
          <div className="flex flex-col gap-2">
            {checklist.map(item => (
              <label
                key={item.id}
                className="flex items-start gap-3 p-2 rounded hover:bg-gray-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={item.checked}
                  onChange={() => toggleCheck(item.id)}
                  className="mt-1 rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                />
                <span
                  className={cn(
                    'text-sm text-gray-700',
                    item.checked && 'line-through opacity-50',
                  )}
                >
                  {item.label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* AI 팁 박스 */}
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
          <div className="flex gap-2 items-center mb-2">
            <svg className="w-4 h-4 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <p className="text-xs font-bold text-primary-600">규정 업데이트 알림</p>
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">
            2024년 1월부로 계약 금액 10% 이상 변경 시, 별도의 사유서 첨부가 의무화되었습니다.
          </p>
        </div>
      </div>

      {/* 하단 액션 바 */}
      <div className="p-6 bg-gray-50 border-t border-gray-200 space-y-3">
        {hasDraft ? (
          <>
            {!isEditable ? (
              <>
                <button
                  type="button"
                  className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-bold py-3 px-4 rounded-lg shadow-sm transition-all active:scale-[0.98]"
                  onClick={onStartEditing}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                  이 양식으로 작성 시작
                </button>
                <button
                  type="button"
                  className="w-full flex items-center justify-center gap-2 bg-white border border-gray-200 text-gray-700 font-bold py-2.5 px-4 rounded-lg hover:bg-gray-50 transition-all"
                  onClick={onResetAll}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                  </svg>
                  새로 작성
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg transition-all"
                  onClick={onDownloadPDF}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  PDF 다운로드
                </button>
                <button
                  type="button"
                  className="w-full flex items-center justify-center gap-2 bg-white border border-gray-200 text-gray-700 font-bold py-2.5 px-4 rounded-lg hover:bg-gray-50 transition-all"
                  onClick={onResetAll}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                  </svg>
                  새로 작성
                </button>
              </>
            )}
          </>
        ) : (
          <>
            <button
              type="button"
              disabled={!canGenerate || isGenerating}
              className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-bold py-3 px-4 rounded-lg shadow-sm transition-all active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed"
              onClick={onGenerate}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
              {isGenerating ? '초안 생성 중...' : '이 양식으로 작성 시작'}
            </button>
            <button
              type="button"
              className="w-full flex items-center justify-center gap-2 bg-white border border-gray-200 text-gray-700 font-bold py-2.5 px-4 rounded-lg hover:bg-gray-50 transition-all"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              PDF 양식 다운로드
            </button>
          </>
        )}
      </div>
    </aside>
  )
}
