import { useRef, useState, useEffect } from 'react'
import { cn } from '@/shared/utils/cn'
import { isDev } from '@/shared/lib/env'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import { analyzeFolder, openFolderDialog } from '@/features/fileExplorer/api/explorerApi'

const RECENT_KEY = 'handover-recent-projects'

function loadRecentProjects() {
  try {
    return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]')
  } catch {
    return []
  }
}

function saveRecentProject(project) {
  const list = loadRecentProjects().filter(p => p.path !== project.path)
  list.unshift(project)
  localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, 5)))
}

export default function FolderUpload() {
  const { dispatch } = useExplorer()
  const inputRef = useRef(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [recentProjects, setRecentProjects] = useState([])

  useEffect(() => {
    setRecentProjects(loadRecentProjects())
  }, [])

  async function handleAnalyze(folderPath) {
    const name = folderPath.split(/[/\\]/).filter(Boolean).pop() || folderPath
    saveRecentProject({ path: folderPath, name, date: new Date().toISOString() })

    dispatch({ type: 'ANALYZE_START' })
    try {
      const result = await analyzeFolder(folderPath)
      dispatch({ type: 'ANALYZE_SUCCESS', projects: result.projects })
    } catch (err) {
      console.error('[FolderUpload] 분석 실패:', err)
      dispatch({ type: 'ANALYZE_FAIL' })
    }
  }

  function handleDrop(e) {
    e.preventDefault()
    setIsDragOver(false)
    const items = e.dataTransfer?.items
    if (!items?.length) return
    const entry = items[0].webkitGetAsEntry?.()
    if (entry?.isDirectory) {
      handleAnalyze(entry.fullPath || entry.name)
    }
  }

  function handleDragOver(e) {
    e.preventDefault()
    setIsDragOver(true)
  }

  function handleDragLeave(e) {
    e.preventDefault()
    setIsDragOver(false)
  }

  async function handleNativeFolderSelect() {
    try {
      const folderPath = await openFolderDialog()
      if (folderPath) {
        handleAnalyze(folderPath)
      }
    } catch (err) {
      console.error('[FolderUpload] 폴더 선택 실패:', err)
    }
  }

  function handleBrowseClick(e) {
    e.stopPropagation()
    if (!isDev) {
      // pywebview 모드: 네이티브 폴더 다이얼로그 사용
      handleNativeFolderSelect()
    } else {
      // 개발 모드: HTML file input 사용
      inputRef.current?.click()
    }
  }

  function handleInputChange(e) {
    const files = e.target.files
    if (files?.length > 0) {
      const path = files[0].webkitRelativePath?.split('/')[0] || 'uploaded-folder'
      handleAnalyze(path)
    }
  }

  function handleRecentClick(project) {
    handleAnalyze(project.path)
  }

  function handleRemoveRecent(e, path) {
    e.stopPropagation()
    const updated = recentProjects.filter(p => p.path !== path)
    localStorage.setItem(RECENT_KEY, JSON.stringify(updated))
    setRecentProjects(updated)
  }

  const hasRecent = recentProjects.length > 0

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 왼쪽: 브랜드 영역 */}
      <aside className="hidden lg:flex w-80 bg-gray-900 text-white flex-col shrink-0">
        <div className="flex-1 flex flex-col justify-center px-10">
          <div className="mb-8">
            <div className="w-10 h-10 rounded-xl bg-primary-500 flex items-center justify-center mb-5">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold tracking-tight leading-tight">
              HandOver AI
            </h1>
            <p className="text-sm text-gray-400 mt-2 leading-relaxed">
              흩어진 업무 문서를 정리하고,<br />
              숨겨진 맥락을 찾아드립니다.
            </p>
          </div>

          <div className="space-y-4 text-sm">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 w-5 h-5 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-xs text-gray-400 shrink-0">1</span>
              <div>
                <p className="text-gray-300 font-medium">폴더 업로드</p>
                <p className="text-xs text-gray-500 mt-0.5">인수인계 폴더를 그대로 넣으세요</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="mt-0.5 w-5 h-5 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-xs text-gray-400 shrink-0">2</span>
              <div>
                <p className="text-gray-300 font-medium">자동 분석</p>
                <p className="text-xs text-gray-500 mt-0.5">업무별 분류와 타임라인 생성</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="mt-0.5 w-5 h-5 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-xs text-gray-400 shrink-0">3</span>
              <div>
                <p className="text-gray-300 font-medium">업무 파악</p>
                <p className="text-xs text-gray-500 mt-0.5">AI에게 질문하며 맥락을 이해하세요</p>
              </div>
            </div>
          </div>
        </div>

        <div className="px-10 py-6 border-t border-gray-800">
          <p className="text-xs text-gray-600">v0.1.0 · 완전 로컬 실행</p>
        </div>
      </aside>

      {/* 오른쪽: 메인 콘텐츠 */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 overflow-y-auto">
        <div className="w-full max-w-lg">
          {/* 모바일/소형 화면용 타이틀 */}
          <div className="lg:hidden text-center mb-8">
            <h1 className="text-xl font-bold text-gray-800">HandOver AI</h1>
            <p className="text-sm text-gray-400 mt-1">업무 인수인계 도우미</p>
          </div>

          {/* 업로드 영역 */}
          <div className="text-center mb-2">
            <h2 className="text-lg font-bold text-gray-800">
              인수인계 폴더를 올려주세요
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              AI가 문서를 분석하고 업무 맥락을 정리해드립니다
            </p>
          </div>

          <div
            className={cn(
              'mt-5 rounded-2xl border-2 border-dashed p-10 text-center transition-all cursor-pointer',
              'hover:border-primary-500 hover:bg-primary-50/30',
              isDragOver
                ? 'border-primary-500 bg-primary-50/50 scale-[1.01]'
                : 'border-gray-300 bg-white',
            )}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => handleBrowseClick({ stopPropagation: () => {} })}
          >
            <div className={cn(
              'mx-auto w-14 h-14 rounded-2xl flex items-center justify-center mb-4 transition-colors',
              isDragOver ? 'bg-primary-100' : 'bg-gray-100',
            )}>
              <svg
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
                stroke={isDragOver ? '#3b82f6' : '#9ca3af'}
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>

            <p className="text-sm font-medium text-gray-700 mb-1">
              {isDragOver ? '여기에 놓으세요' : '폴더를 드래그하여 놓으세요'}
            </p>
            <p className="text-xs text-gray-400 mb-5">
              HWP, Excel 등 업무 문서가 담긴 폴더
            </p>

            <button
              type="button"
              className="btn-primary text-sm"
              onClick={handleBrowseClick}
            >
              폴더 찾아보기
            </button>

            <input
              ref={inputRef}
              type="file"
              className="hidden"
              webkitdirectory=""
              onChange={handleInputChange}
            />
          </div>

          {/* 최근 업무 */}
          {hasRecent && (
            <div className="mt-8">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                최근 분석한 업무
              </h3>
              <div className="space-y-2">
                {recentProjects.map((project) => (
                  <button
                    key={project.path}
                    type="button"
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-3 rounded-xl',
                      'bg-white border border-gray-200 text-left',
                      'hover:border-gray-300 hover:shadow-sm transition-all group',
                    )}
                    onClick={() => handleRecentClick(project)}
                  >
                    <div className="w-9 h-9 rounded-lg bg-gray-100 flex items-center justify-center shrink-0">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-700 truncate">
                        {project.name}
                      </p>
                      <p className="text-xs text-gray-400 truncate">
                        {new Date(project.date).toLocaleDateString('ko-KR', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                    </div>
                    <button
                      type="button"
                      className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-gray-100 transition-all"
                      onClick={(e) => handleRemoveRecent(e, project.path)}
                      title="목록에서 제거"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
