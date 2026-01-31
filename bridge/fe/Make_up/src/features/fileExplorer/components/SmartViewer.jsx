import { useMemo } from 'react'
import { cn } from '@/shared/utils/cn'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import { flattenFiles } from '@/features/timeline/lib/gapDetector'
import { DOC_TYPE_COLORS } from '@/shared/constants/docTypes'

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`
}

function findRelatedFiles(currentFile, allFiles) {
  const sorted = allFiles
    .filter(f => f.date != null)
    .sort((a, b) => new Date(a.date) - new Date(b.date))

  const idx = sorted.findIndex(f => f.id === currentFile.id)
  if (idx === -1) return { prev: null, next: null }

  return {
    prev: idx > 0 ? sorted[idx - 1] : null,
    next: idx < sorted.length - 1 ? sorted[idx + 1] : null,
  }
}

/**
 * 현재 파일과 관련된 issues를 프로젝트 summary에서 찾기
 */
function findRelatedIssues(fileId, summary) {
  if (!summary?.issues) return []
  // issues에 relatedFileIds가 있으면 매칭, 없으면 전체 표시하지 않음
  return summary.issues.filter(issue =>
    issue.relatedFileIds?.includes(fileId)
  )
}

/**
 * 현재 파일과 관련된 decisions를 프로젝트 summary에서 찾기
 */
function findRelatedDecisions(fileId, summary) {
  if (!summary?.decisions) return []
  return summary.decisions.filter(d =>
    d.relatedFileIds?.includes(fileId)
  )
}

export default function SmartViewer({ onBack, onFileSelect, onStartDocWriter }) {
  const { selectedFile, selectedProject } = useExplorer()

  const allFiles = useMemo(() => {
    if (!selectedProject) return []
    return flattenFiles(selectedProject.files)
  }, [selectedProject])

  const { prev, next } = useMemo(() => {
    if (!selectedFile) return { prev: null, next: null }
    return findRelatedFiles(selectedFile, allFiles)
  }, [selectedFile, allFiles])

  const relatedDecisions = useMemo(() => {
    if (!selectedFile) return []
    return findRelatedDecisions(selectedFile.id, selectedProject?.summary)
  }, [selectedFile, selectedProject])

  const relatedIssues = useMemo(() => {
    if (!selectedFile) return []
    return findRelatedIssues(selectedFile.id, selectedProject?.summary)
  }, [selectedFile, selectedProject])

  // 프로젝트의 가이드라인 (전체 공유)
  const guidelines = selectedProject?.summary?.guidelines ?? []

  if (!selectedFile) return null

  const badgeColor = DOC_TYPE_COLORS[selectedFile.docType] ?? 'bg-gray-100 text-gray-600'
  const parties = selectedFile.parties ?? []
  const keywords = selectedFile.keywords ?? []

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* 좌측: 문서 뷰어 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* 상단 네비 */}
        <div className="shrink-0 flex items-center gap-3 px-6 py-3 border-b border-gray-200 bg-white">
          <button
            type="button"
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors"
            onClick={onBack}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            대시보드
          </button>
          <span className="text-gray-300">|</span>
          <span className={cn('text-[10px] font-medium px-1.5 py-0.5 rounded', badgeColor)}>
            {selectedFile.docType}
          </span>
          <h2 className="text-sm font-medium text-gray-800 truncate">
            {selectedFile.name}
          </h2>
        </div>

        {/* 문서 본문 영역 */}
        <div className="flex-1 overflow-y-auto bg-gray-50 p-6">
          <div className="max-w-2xl mx-auto bg-white rounded-xl border border-gray-200 shadow-sm min-h-[600px]">
            {/* 문서 헤더 */}
            <div className="px-8 py-6 border-b border-gray-100">
              <div className="flex items-center gap-3 mb-3">
                <span className={cn('text-xs font-medium px-2 py-0.5 rounded', badgeColor)}>
                  {selectedFile.docType}
                </span>
                {selectedFile.date && (
                  <span className="text-xs text-gray-400">{formatDate(selectedFile.date)}</span>
                )}
              </div>
              <h1 className="text-lg font-bold text-gray-900">
                {selectedFile.name}
              </h1>
              {selectedFile.amount != null && (
                <p className="text-sm text-gray-600 mt-2">
                  금액: <span className="font-semibold">{selectedFile.amount.toLocaleString('ko-KR')}원</span>
                </p>
              )}
              {parties.length > 0 && (
                <p className="text-sm text-gray-500 mt-1">
                  관련 업체: {parties.join(', ')}
                </p>
              )}
            </div>

            {/* 본문 */}
            <div className="px-8 py-6">
              {selectedFile.summary ? (
                <div>
                  <p className="text-gray-700 leading-relaxed">{selectedFile.summary}</p>
                  <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-dashed border-gray-200 text-center">
                    <p className="text-sm text-gray-400">
                      HWP 본문 미리보기 영역
                    </p>
                    <p className="text-xs text-gray-300 mt-1">
                      백엔드 연동 시 실제 문서 내용이 표시됩니다
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-sm text-gray-400">본문 내용을 불러올 수 없습니다.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 우측: AI 가이드 패널 */}
      <aside className="w-80 border-l border-gray-200 bg-white overflow-y-auto shrink-0">
        <div className="p-5 space-y-5">

          {/* AI 요약 */}
          <section>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              AI 요약
            </h3>
            <div className="rounded-xl bg-primary-50/50 border border-primary-100 p-4">
              <p className="text-sm text-gray-700 leading-relaxed">
                {selectedFile.summary || '요약 정보가 없습니다.'}
              </p>
              {selectedFile.amount != null && (
                <p className="text-xs text-primary-600 font-medium mt-2">
                  관련 금액: {selectedFile.amount.toLocaleString('ko-KR')}원
                </p>
              )}
              {keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {keywords.map(kw => (
                    <span key={kw} className="text-[10px] px-1.5 py-0.5 bg-primary-100/50 text-primary-600 rounded">
                      {kw}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* 문서 맥락 */}
          <section>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              문서 맥락
            </h3>
            <div className="space-y-2">
              {prev && (
                <button
                  type="button"
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border border-gray-200 hover:border-primary-200 hover:bg-primary-50/30 transition-all text-left"
                  onClick={() => onFileSelect(prev.id)}
                >
                  <div className="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center shrink-0">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="15 18 9 12 15 6" />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs text-gray-400">이전 문서</p>
                    <p className="text-sm text-gray-700 truncate">{prev.name}</p>
                  </div>
                </button>
              )}
              {next && (
                <button
                  type="button"
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border border-gray-200 hover:border-primary-200 hover:bg-primary-50/30 transition-all text-left"
                  onClick={() => onFileSelect(next.id)}
                >
                  <div className="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center shrink-0">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="9 18 15 12 9 6" />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs text-gray-400">다음 문서</p>
                    <p className="text-sm text-gray-700 truncate">{next.name}</p>
                  </div>
                </button>
              )}
              {!prev && !next && (
                <p className="text-xs text-gray-400 text-center py-2">
                  연결된 문서가 없습니다
                </p>
              )}
            </div>
          </section>

          {/* 이 파일 관련 의사결정 */}
          {relatedDecisions.length > 0 && (
            <section>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                관련 의사결정
              </h3>
              <div className="space-y-2">
                {relatedDecisions.map((d, i) => (
                  <div key={i} className="rounded-lg bg-amber-50 border border-amber-100 px-3 py-2.5">
                    <p className="text-sm text-amber-900 font-medium">{d.title}</p>
                    <p className="text-xs text-amber-800 mt-0.5 leading-relaxed">{d.description}</p>
                    {d.impact && (
                      <p className="text-xs text-amber-600 font-medium mt-1">{d.impact}</p>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 이 파일 관련 확인 사항 */}
          {relatedIssues.length > 0 && (
            <section>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                확인 필요
              </h3>
              <div className="space-y-2">
                {relatedIssues.map((issue, i) => (
                  <div key={i} className="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2.5">
                    <p className="text-sm text-gray-700 font-medium">{issue.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{issue.description}</p>
                    {issue.suggestion && (
                      <p className="text-xs text-gray-400 mt-1 italic">{issue.suggestion}</p>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 가이드라인 */}
          {guidelines.length > 0 && (
            <section>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                활용 가이드
              </h3>
              <div className="rounded-xl bg-gray-50 p-4 space-y-3">
                {guidelines.map((group, gi) => (
                  <div key={gi}>
                    <p className="text-xs text-gray-500 font-medium mb-1">{group.title}</p>
                    <ul className="space-y-1">
                      {group.items.map((item, ii) => (
                        <li key={ii} className="flex items-start gap-2 text-xs text-gray-600 leading-relaxed">
                          <span className="text-gray-300 mt-0.5 shrink-0">·</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 액션 버튼 */}
          <section className="space-y-2">
            <button
              type="button"
              className="w-full px-4 py-2.5 text-sm font-medium text-primary-600 border border-primary-200 rounded-xl hover:bg-primary-50 transition-colors"
              onClick={() => onStartDocWriter(selectedFile)}
            >
              이 문서 기반으로 새 공문 작성
            </button>
          </section>
        </div>
      </aside>
    </div>
  )
}
