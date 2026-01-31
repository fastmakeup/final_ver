import { useState, useCallback } from 'react'
import { cn } from '@/shared/utils/cn'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import TaskList from '@/features/fileExplorer/components/TaskList'
import { TaskDashboard, TaskDetailView } from '@/features/dashboard'
import SmartViewer from '@/features/fileExplorer/components/SmartViewer'
import FileGrid from '@/features/fileExplorer/components/FileGrid'
import ChatPanel from '@/features/chat/components/ChatPanel'
import DocWriterPanel from '@/features/docWriter/components/DocWriterPanel'
import AnalyzingBanner from '@/features/fileExplorer/components/AnalyzingBanner'
import AnalyzingPlaceholder from '@/features/fileExplorer/components/AnalyzingPlaceholder'
import SidebarSkeleton from '@/features/fileExplorer/components/SidebarSkeleton'

/**
 * 메인 뷰 상태:
 * - 'dashboard'   : 업무 타임라인 + 요약 (기본)
 * - 'taskDetail'  : 2분할 상세 (업무 상세 + AI 채팅)
 * - 'fileView'    : 파일 상세 + AI 가이드
 * - 'chat'        : AI 질문-답변
 * - 'docWriter'   : 공문 작성
 */

/* ── 사이드바 하단 도구 버튼 ── */
function SidebarTools({ activeView, onViewChange }) {
  const tools = [
    {
      id: 'dashboard',
      label: '대시보드',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
        </svg>
      ),
    },
    {
      id: 'fileGrid',
      label: '파일 목록',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
      ),
    },
    {
      id: 'chat',
      label: 'AI 질문',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      ),
    },
    {
      id: 'docWriter',
      label: '공문 작성',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
      ),
    },
  ]

  return (
    <div className="p-3 space-y-1">
      {tools.map(tool => (
        <button
          key={tool.id}
          type="button"
          className={cn(
            'w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors',
            activeView === tool.id
              ? 'bg-primary-50 text-primary-700 font-medium'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100',
          )}
          onClick={() => onViewChange(tool.id)}
        >
          {tool.icon}
          {tool.label}
        </button>
      ))}
    </div>
  )
}


export default function ExplorerLayout() {
  const { state, dispatch, selectedProject } = useExplorer()
  const [activeView, setActiveView] = useState('dashboard')
  const [referenceFile, setReferenceFile] = useState(null)

  const isAnalyzing = state.isAnalyzing
  const hasProjects = state.projects.length > 0
  const aiInProgress = state.aiStatus === 'pending' || state.aiStatus === 'analyzing'

  const handleFileSelect = useCallback((fileId) => {
    dispatch({ type: 'SELECT_FILE', fileId })
    setActiveView('fileView')
  }, [dispatch])

  const handleBackToDashboard = useCallback(() => {
    dispatch({ type: 'SELECT_FILE', fileId: null })
    setActiveView('dashboard')
  }, [dispatch])

  const handleStartDocWriter = useCallback((file) => {
    setReferenceFile(file || null)
    setActiveView('docWriter')
  }, [])

  const handleViewChange = useCallback((view) => {
    if (view !== 'fileView') {
      dispatch({ type: 'SELECT_FILE', fileId: null })
    }
    setActiveView(view)
  }, [dispatch])

  // 업무 선택 시 대시보드로 복귀
  const handleTaskSelect = useCallback(() => {
    setActiveView('dashboard')
  }, [])

  // SummaryPanel 최대화 → 2분할 상세 뷰
  const handleExpand = useCallback(() => {
    setActiveView('taskDetail')
  }, [])

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {isAnalyzing && <AnalyzingBanner stage="local" />}
      {!isAnalyzing && aiInProgress && <AnalyzingBanner stage="ai" />}

      <div className="flex flex-1 overflow-hidden">
        {/* ── 사이드바 ── */}
        <aside className="w-[240px] border-r border-gray-200 bg-white flex flex-col shrink-0">
          {/* 헤더 */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
            <h1 className="text-sm font-bold text-gray-800">HandOver AI</h1>
            <button
              type="button"
              className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
              onClick={() => dispatch({ type: 'RESET' })}
            >
              새 분석
            </button>
          </div>

          {/* 업무 목록 */}
          {hasProjects ? (
            <div className="flex-1 overflow-y-auto">
              <TaskList onTaskSelect={handleTaskSelect} />
            </div>
          ) : isAnalyzing ? (
            <SidebarSkeleton />
          ) : (
            <div className="flex-1" />
          )}

          {/* 하단 도구 버튼 */}
          {selectedProject && (
            <div className="border-t border-gray-200">
              <SidebarTools activeView={activeView} onViewChange={handleViewChange} />
            </div>
          )}
        </aside>

        {/* ── 메인 영역 ── */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {selectedProject ? (
            <>
              {activeView === 'dashboard' && (
                <TaskDashboard onFileSelect={handleFileSelect} onExpand={handleExpand} />
              )}
              {activeView === 'taskDetail' && (
                <TaskDetailView
                  onBack={handleBackToDashboard}
                  onFileSelect={handleFileSelect}
                />
              )}
              {activeView === 'fileGrid' && (
                <FileGrid
                  onFileSelect={handleFileSelect}
                  onBack={handleBackToDashboard}
                />
              )}
              {activeView === 'fileView' && (
                <SmartViewer
                  onBack={handleBackToDashboard}
                  onFileSelect={handleFileSelect}
                  onStartDocWriter={handleStartDocWriter}
                />
              )}
              {activeView === 'chat' && (
                <div className="flex-1 overflow-hidden">
                  <ChatPanel projectId={selectedProject.id} />
                </div>
              )}
              {activeView === 'docWriter' && (
                <div className="flex-1 overflow-hidden">
                  <DocWriterPanel referenceFile={referenceFile} />
                </div>
              )}
            </>
          ) : isAnalyzing ? (
            <AnalyzingPlaceholder />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center mb-4">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <p className="text-sm text-gray-500 font-medium">업무를 선택하세요</p>
              <p className="text-xs text-gray-400 mt-1">좌측 목록에서 확인할 업무를 선택합니다</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
