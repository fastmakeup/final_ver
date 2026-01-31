import { useMemo } from 'react'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import { flattenFiles } from '@/features/timeline/lib/gapDetector'
import TimelineNode from '@/features/timeline/components/TimelineNode'

export default function Timeline({ files }) {
  const { state, dispatch } = useExplorer()

  const sortedFiles = useMemo(() => {
    return flattenFiles(files)
      .filter(f => f.date != null)
      .sort((a, b) => new Date(a.date) - new Date(b.date))
  }, [files])

  if (sortedFiles.length === 0) {
    return (
      <p className="text-sm text-gray-400">
        타임라인에 표시할 문서가 없습니다.
      </p>
    )
  }

  function handleSelect(fileId) {
    dispatch({ type: 'SELECT_FILE', fileId })
  }

  return (
    <div>
      <h2 className="text-sm font-bold text-gray-800 mb-4">타임라인</h2>
      <div>
        {sortedFiles.map((file, i) => (
          <TimelineNode
            key={file.id}
            file={file}
            isSelected={state.selectedFileId === file.id}
            isLast={i === sortedFiles.length - 1}
            onSelect={handleSelect}
          />
        ))}
      </div>
    </div>
  )
}
