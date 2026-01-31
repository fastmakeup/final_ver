import { useMemo } from 'react'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import { flattenFiles } from '@/features/timeline/lib/gapDetector'
import FileCard from '@/features/fileExplorer/components/FileCard'

export default function FileGrid({ onFileSelect, onBack }) {
  const { selectedProject, selectedFile } = useExplorer()

  const files = useMemo(() => {
    if (!selectedProject) return []
    return flattenFiles(selectedProject.files)
  }, [selectedProject])

  if (!selectedProject) return null

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {/* 헤더 */}
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
        <h2 className="text-sm font-medium text-gray-800">파일 목록</h2>
        <span className="text-[11px] text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
          {files.length}개
        </span>
      </div>

      {/* 그리드 */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {files.map(file => (
            <FileCard
              key={file.id}
              file={file}
              isSelected={selectedFile?.id === file.id}
              onClick={() => onFileSelect(file.id)}
            />
          ))}

          {/* 업로드 플레이스홀더 */}
          <div className="rounded-xl border-2 border-dashed border-gray-200 p-4 flex flex-col items-center justify-center text-center min-h-[100px] hover:border-gray-300 transition-colors">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#d1d5db" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            <p className="text-xs text-gray-400 mt-2">파일 추가</p>
            <p className="text-[10px] text-gray-300 mt-0.5">백엔드 연동 시 활성화</p>
          </div>
        </div>
      </div>
    </div>
  )
}
