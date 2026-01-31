import { useMemo } from 'react'
import { cn } from '@/shared/utils/cn'
import { MOCK_PROJECTS } from '@/mocks/projects'

function countFiles(files) {
  let count = 0
  for (const f of files) {
    if (f.children) count += countFiles(f.children)
    else count += 1
  }
  return count
}

function FileCheckNode({ file, depth = 0 }) {
  const isFolder = Boolean(file.children)

  return (
    <>
      <div
        className="flex items-center gap-2 py-1.5 px-2 rounded-md text-sm"
        style={{ paddingLeft: `${depth * 20 + 8}px` }}
      >
        <span className="text-gray-400 text-xs">
          {isFolder ? '📁' : '📄'}
        </span>
        <span className={cn('truncate', isFolder ? 'font-medium text-gray-700' : 'text-gray-600')}>
          {file.name}
        </span>
        {file.docType && file.docType !== 'folder' && (
          <span className="ml-auto text-xs text-gray-400 shrink-0">{file.docType}</span>
        )}
      </div>
      {isFolder && file.children.map(child => (
        <FileCheckNode key={child.id} file={child} depth={depth + 1} />
      ))}
    </>
  )
}

export default function FolderSelectUpload({ selectedProjects, onChangeSelection }) {
  const totalSelected = useMemo(() => {
    let count = 0
    for (const p of MOCK_PROJECTS) {
      if (selectedProjects.has(p.id)) count += countFiles(p.files)
    }
    return count
  }, [selectedProjects])

  function toggleProject(projectId) {
    const next = new Set(selectedProjects)
    if (next.has(projectId)) next.delete(projectId)
    else next.add(projectId)
    onChangeSelection(next)
  }

  function handleSelectAll() {
    onChangeSelection(new Set(MOCK_PROJECTS.map(p => p.id)))
  }

  function handleDeselectAll() {
    onChangeSelection(new Set())
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-8 pt-8 pb-4">
        <h2 className="text-lg font-bold text-gray-800 mb-1">분석할 업무 선택</h2>
        <p className="text-sm text-gray-400">
          분석이 필요한 업무만 체크하세요. 불필요한 항목은 해제할 수 있습니다.
        </p>
      </div>

      <div className="px-8 py-2 flex items-center gap-3 border-b border-gray-100">
        <button
          type="button"
          className="text-xs text-primary-600 hover:text-primary-700 font-medium"
          onClick={handleSelectAll}
        >
          전체 선택
        </button>
        <span className="text-gray-300">|</span>
        <button
          type="button"
          className="text-xs text-gray-400 hover:text-gray-600"
          onClick={handleDeselectAll}
        >
          전체 해제
        </button>
        <span className="ml-auto text-xs text-gray-400">
          {totalSelected}개 파일 ({selectedProjects.size}개 업무)
        </span>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
        {MOCK_PROJECTS.map(project => {
          const isChecked = selectedProjects.has(project.id)
          const fileCount = countFiles(project.files)

          return (
            <div
              key={project.id}
              className={cn(
                'rounded-xl border-2 transition-all',
                isChecked ? 'border-primary-500/30 bg-primary-50/20' : 'border-gray-200',
              )}
            >
              <label className="flex items-center gap-3 px-4 py-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => toggleProject(project.id)}
                  className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-800">{project.name}</p>
                  <p className="text-xs text-gray-400">{fileCount}개 파일</p>
                </div>
                {project.warnings > 0 && (
                  <span className="text-xs text-amber-500 shrink-0">⚠ {project.warnings}건 경고</span>
                )}
              </label>

              {isChecked && (
                <div className="border-t border-gray-100 px-2 py-2">
                  {project.files.map(file => (
                    <FileCheckNode key={file.id} file={file} depth={1} />
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
