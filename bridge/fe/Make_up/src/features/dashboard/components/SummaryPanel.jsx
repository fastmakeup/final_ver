import { cn } from '@/shared/utils/cn'

const ISSUE_STYLES = {
  warn: 'bg-amber-50 border-amber-100',
  info: 'bg-gray-50 border-gray-200',
}

const STATUS_LABELS = {
  completed: '완료',
  in_progress: '진행 중',
  unknown: '확인 필요',
}

function formatShortDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}월 ${d.getDate()}일`
}

export default function SummaryPanel({ summary, allFiles, onFileSelect, onExpand }) {
  if (!summary) return null

  const overview = summary.overview
  const decisions = summary.decisions ?? []
  const issues = summary.issues ?? []
  const guidelines = summary.guidelines ?? []
  const keyFiles = summary.keyFiles ?? []
  const fileCount = allFiles?.length ?? 0

  return (
    <aside className="w-80 border-l border-gray-200 bg-white overflow-y-auto shrink-0">
      <div className="p-5 space-y-5">

        {/* 패널 헤더 + 최대화 버튼 */}
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            업무 요약
          </h2>
          {onExpand && (
            <button
              type="button"
              className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-primary-600 transition-colors px-2 py-1 rounded-lg hover:bg-primary-50"
              onClick={onExpand}
              title="상세 보기"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 3 21 3 21 9" />
                <polyline points="9 21 3 21 3 15" />
                <line x1="21" y1="3" x2="14" y2="10" />
                <line x1="3" y1="21" x2="10" y2="14" />
              </svg>
              상세
            </button>
          )}
        </div>

        {/* 업무 개요 */}
        {overview && (
          <section>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              업무 개요
            </h3>
            <div className="rounded-xl bg-gray-50 p-4 space-y-3">
              <p className="text-sm text-gray-700 leading-relaxed">
                {overview.description}
              </p>
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-gray-200">
                <div>
                  <p className="text-[10px] text-gray-400 uppercase">기간</p>
                  <p className="text-xs text-gray-700 font-medium">{overview.period}</p>
                </div>
                {overview.budget > 0 && (
                  <div>
                    <p className="text-[10px] text-gray-400 uppercase">예산</p>
                    <p className="text-xs text-gray-700 font-medium">
                      {overview.budget.toLocaleString('ko-KR')}원
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-[10px] text-gray-400 uppercase">문서</p>
                  <p className="text-xs text-gray-700 font-medium">{fileCount}건</p>
                </div>
                <div>
                  <p className="text-[10px] text-gray-400 uppercase">상태</p>
                  <p className="text-xs text-gray-700 font-medium">
                    {STATUS_LABELS[overview.status] ?? overview.status}
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* 주요 의사결정 */}
        {decisions.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              주요 의사결정
            </h3>
            <div className="space-y-2">
              {decisions.map((d, i) => (
                <div
                  key={i}
                  className="rounded-lg bg-amber-50 border border-amber-100 px-3 py-2.5"
                >
                  <p className="text-xs text-amber-500 font-medium mb-0.5">
                    {formatShortDate(d.date)}
                  </p>
                  <p className="text-sm text-amber-900 font-medium">{d.title}</p>
                  <p className="text-xs text-amber-800 mt-0.5 leading-relaxed">{d.description}</p>
                  {d.impact && (
                    <p className="text-xs text-amber-600 font-medium mt-1">{d.impact}</p>
                  )}
                  {d.relatedFileIds?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {d.relatedFileIds.map(fid => {
                        const file = allFiles?.find(f => f.id === fid)
                        if (!file) return null
                        return (
                          <button
                            key={fid}
                            type="button"
                            className="text-[10px] text-amber-700 underline hover:no-underline"
                            onClick={() => onFileSelect(fid)}
                          >
                            {file.name}
                          </button>
                        )
                      })}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* 확인 필요 사항 */}
        {issues.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              확인 필요
            </h3>
            <div className="space-y-2">
              {issues.map((issue, i) => (
                <div
                  key={i}
                  className={cn(
                    'rounded-lg border px-3 py-2.5',
                    ISSUE_STYLES[issue.level] ?? ISSUE_STYLES.info,
                  )}
                >
                  <p className="text-sm text-gray-700 font-medium">{issue.title}</p>
                  <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{issue.description}</p>
                  {issue.suggestion && (
                    <p className="text-xs text-gray-400 mt-1.5 italic">{issue.suggestion}</p>
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
              가이드
            </h3>
            <div className="space-y-3">
              {guidelines.map((group, gi) => (
                <div key={gi}>
                  <p className="text-xs text-gray-500 font-medium mb-1.5">{group.title}</p>
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

        {/* 주요 문서 바로가기 */}
        {keyFiles.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              주요 문서
            </h3>
            <div className="space-y-1.5">
              {keyFiles.map(({ fileId, reason }) => {
                const file = allFiles?.find(f => f.id === fileId)
                if (!file) return null
                return (
                  <button
                    key={fileId}
                    type="button"
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-left"
                    onClick={() => onFileSelect(fileId)}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                    <div className="min-w-0">
                      <p className="text-sm text-gray-700 truncate">{file.name}</p>
                      <p className="text-xs text-gray-400">{reason}</p>
                    </div>
                  </button>
                )
              })}
            </div>
          </section>
        )}
      </div>
    </aside>
  )
}
