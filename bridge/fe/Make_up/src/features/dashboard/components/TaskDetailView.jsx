import { useEffect, useRef } from 'react'
import { cn } from '@/shared/utils/cn'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import { useChat } from '@/features/chat/hooks/useChat'
import { flattenFiles } from '@/features/timeline/lib/gapDetector'
import ChatMessage from '@/features/chat/components/ChatMessage'
import ChatInput from '@/features/chat/components/ChatInput'

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
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}월 ${d.getDate()}일`
}

/**
 * 2분할 상세 뷰: 좌측 업무 상세 + 우측 AI 채팅
 */
export default function TaskDetailView({ onBack, onFileSelect }) {
  const { selectedProject, dispatch } = useExplorer()
  const projectId = selectedProject?.id
  const { messages, isLoading, sendMessage } = useChat(projectId)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  if (!selectedProject) return null

  const { summary } = selectedProject
  const overview = summary?.overview
  const decisions = summary?.decisions ?? []
  const issues = summary?.issues ?? []
  const guidelines = summary?.guidelines ?? []
  const keyFiles = summary?.keyFiles ?? []
  const allFiles = flattenFiles(selectedProject.files)

  function handleSourceClick(fileId) {
    dispatch({ type: 'SELECT_FILE', fileId })
    onFileSelect?.(fileId)
  }

  return (
    <div className="flex flex-1 overflow-hidden animate-expand-in">
      {/* ── 좌측: 업무 상세 ── */}
      <section className="w-1/2 flex flex-col border-r border-gray-200 bg-white overflow-y-auto">
        <div className="max-w-2xl mx-auto w-full p-8 pb-20">
          {/* 뒤로가기 */}
          <div className="flex items-center gap-2 mb-6 text-sm text-gray-500">
            <button
              type="button"
              className="flex items-center gap-1 hover:text-gray-700 transition-colors"
              onClick={onBack}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6" />
              </svg>
              대시보드
            </button>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-300">
              <polyline points="9 18 15 12 9 6" />
            </svg>
            <span className="text-primary-600 font-medium text-xs bg-primary-50 px-2 py-0.5 rounded">
              상세
            </span>
          </div>

          {/* 업무 제목 */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight mb-2">
              {selectedProject.name}
            </h1>
            {overview && (
              <p className="text-gray-500 text-sm">
                {overview.period} · {STATUS_LABELS[overview.status] ?? overview.status}
              </p>
            )}
          </div>

          {/* 메타데이터 그리드 */}
          {overview && (
            <div className="mb-10 rounded-xl border border-gray-200 bg-gray-50/50 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500">업무 상세 정보</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-gray-200">
                <div className="p-5">
                  <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-1">기간</p>
                  <p className="text-gray-900 font-medium">{overview.period}</p>
                </div>
                {overview.budget > 0 && (
                  <div className="p-5">
                    <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-1">예산</p>
                    <p className="text-gray-900 font-medium text-lg">
                      {overview.budget.toLocaleString('ko-KR')}원
                    </p>
                  </div>
                )}
                <div className="p-5">
                  <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-1">상태</p>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'size-2 rounded-full',
                      overview.status === 'completed' ? 'bg-emerald-500' : 'bg-amber-500',
                    )} />
                    <p className="text-gray-900 font-medium">
                      {STATUS_LABELS[overview.status] ?? overview.status}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 업무 요약 */}
          {overview?.description && (
            <div className="mb-8">
              <h3 className="text-gray-900 text-lg font-bold mb-4">업무 요약</h3>
              <p className="text-gray-600 leading-relaxed">{overview.description}</p>
            </div>
          )}

          {/* 주요 의사결정 */}
          {decisions.length > 0 && (
            <div className="mb-8">
              <h3 className="text-gray-900 text-lg font-bold mb-4">주요 의사결정</h3>
              <div className="space-y-3">
                {decisions.map((d, i) => (
                  <div
                    key={i}
                    className="rounded-xl bg-amber-50 border border-amber-100 p-4"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-amber-500 font-medium">
                        {formatShortDate(d.date)}
                      </span>
                    </div>
                    <p className="text-sm text-amber-900 font-semibold">{d.title}</p>
                    <p className="text-sm text-amber-800 mt-1 leading-relaxed">{d.description}</p>
                    {d.impact && (
                      <p className="text-xs text-amber-600 font-medium mt-2 p-2 bg-amber-100/50 rounded-lg">
                        {d.impact}
                      </p>
                    )}
                    {d.relatedFileIds?.length > 0 && (
                      <div className="flex items-center gap-3 pt-3 mt-3 border-t border-amber-200/50">
                        <span className="text-[10px] text-amber-400 font-medium uppercase tracking-wider">출처</span>
                        {d.relatedFileIds.map(fid => {
                          const file = allFiles?.find(f => f.id === fid)
                          if (!file) return null
                          return (
                            <button
                              key={fid}
                              type="button"
                              className="flex items-center gap-1 bg-white/70 hover:bg-white text-amber-700 px-2.5 py-1 rounded-full text-xs font-medium transition-colors border border-amber-200"
                              onClick={() => handleSourceClick(fid)}
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                                <polyline points="14 2 14 8 20 8" />
                              </svg>
                              {file.name}
                            </button>
                          )
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 확인 필요 사항 */}
          {issues.length > 0 && (
            <div className="mb-8">
              <h3 className="text-gray-900 text-lg font-bold mb-4">확인 필요</h3>
              <div className="space-y-3">
                {issues.map((issue, i) => (
                  <div
                    key={i}
                    className={cn(
                      'rounded-xl border p-4',
                      issue.level === 'warn'
                        ? 'bg-amber-50 border-amber-100'
                        : 'bg-gray-50 border-gray-200',
                    )}
                  >
                    <p className="text-sm text-gray-800 font-semibold">{issue.title}</p>
                    <p className="text-sm text-gray-600 mt-1 leading-relaxed">{issue.description}</p>
                    {issue.suggestion && (
                      <p className="text-xs text-gray-400 mt-2 italic p-2 bg-white/50 rounded-lg">
                        {issue.suggestion}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 가이드라인 */}
          {guidelines.length > 0 && (
            <div className="mb-8">
              <h3 className="text-gray-900 text-lg font-bold mb-4">가이드</h3>
              <div className="space-y-4">
                {guidelines.map((group, gi) => (
                  <div key={gi}>
                    <p className="text-sm text-gray-500 font-medium mb-2">{group.title}</p>
                    <ul className="space-y-1.5">
                      {group.items.map((item, ii) => (
                        <li key={ii} className="flex items-start gap-2 text-sm text-gray-600 leading-relaxed">
                          <span className="text-gray-300 mt-0.5 shrink-0">·</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 주요 문서 바로가기 */}
          {keyFiles.length > 0 && (
            <div>
              <h3 className="text-gray-900 text-lg font-bold mb-4">주요 문서</h3>
              <div className="grid grid-cols-1 gap-2">
                {keyFiles.map(({ fileId, reason }) => {
                  const file = allFiles?.find(f => f.id === fileId)
                  if (!file) return null
                  return (
                    <button
                      key={fileId}
                      type="button"
                      className="w-full flex items-center gap-3 px-4 py-3 rounded-xl border border-gray-200 hover:border-primary-200 hover:bg-primary-50/30 transition-all text-left"
                      onClick={() => handleSourceClick(fileId)}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                      <div className="min-w-0">
                        <p className="text-sm text-gray-700 font-medium truncate">{file.name}</p>
                        <p className="text-xs text-gray-400">{reason}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ── 우측: AI 채팅 ── */}
      <section className="w-1/2 flex flex-col bg-gray-50 relative">
        {/* 채팅 헤더 */}
        <div className="flex items-center justify-between px-6 py-3 bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-primary-50 text-primary-600 rounded-md">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <span className="font-semibold text-gray-700 text-sm">AI 채팅</span>
          </div>
          <button
            type="button"
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors px-2 py-1 rounded-lg hover:bg-gray-100"
            onClick={onBack}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="4 14 10 14 10 20" />
              <polyline points="20 10 14 10 14 4" />
              <line x1="14" y1="10" x2="21" y2="3" />
              <line x1="3" y1="21" x2="10" y2="14" />
            </svg>
            축소
          </button>
        </div>

        {/* 메시지 영역 */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 pb-28">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-10 h-10 rounded-full bg-primary-50 text-primary-600 flex items-center justify-center mb-4">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <p className="text-sm text-gray-500 mb-1">
                <strong>{selectedProject.name}</strong> 업무에 대해 질문해보세요.
              </p>
              <p className="text-xs text-gray-400">
                예: "예산 왜 증액됐어?", "계약 언제 했어?"
              </p>
              {/* 추천 질문 */}
              <div className="flex flex-wrap gap-2 mt-4 justify-center">
                <button
                  type="button"
                  className="text-xs bg-white border border-gray-200 hover:border-primary-300 hover:text-primary-600 px-3 py-1.5 rounded-full transition-colors text-gray-500"
                  onClick={() => sendMessage('이 업무 요약해줘')}
                >
                  업무 요약
                </button>
                <button
                  type="button"
                  className="text-xs bg-white border border-gray-200 hover:border-primary-300 hover:text-primary-600 px-3 py-1.5 rounded-full transition-colors text-gray-500"
                  onClick={() => sendMessage('확인해야 할 사항이 뭐야?')}
                >
                  확인 사항
                </button>
              </div>
            </div>
          )}
          {messages.map(msg => (
            <ChatMessage
              key={msg.id}
              message={msg}
              onSourceClick={handleSourceClick}
            />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 text-sm text-gray-400 shadow-sm">
                답변 생성 중...
              </div>
            </div>
          )}
        </div>

        {/* 입력 영역 */}
        <div className="absolute bottom-0 left-0 w-full bg-white/80 backdrop-blur-md border-t border-gray-200 p-4">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
          <p className="text-center text-[10px] text-gray-400 mt-2">
            AI는 실수를 할 수 있습니다. 중요한 정보를 확인하세요.
          </p>
        </div>
      </section>
    </div>
  )
}
