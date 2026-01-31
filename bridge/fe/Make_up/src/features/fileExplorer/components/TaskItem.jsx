import { cn } from '@/shared/utils/cn'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'

export default function TaskItem({ project, onSelect }) {
  const { state, dispatch } = useExplorer()
  const isSelected = state.selectedProjectId === project.id

  function handleClick() {
    dispatch({ type: 'SELECT_PROJECT', projectId: project.id })
    onSelect?.()
  }

  return (
    <button
      type="button"
      className={cn(
        'w-full text-left px-3 py-2 rounded-lg transition-colors',
        isSelected
          ? 'bg-primary-50 text-primary-700'
          : 'hover:bg-gray-100 text-gray-700',
      )}
      onClick={handleClick}
    >
      <div className="font-medium text-sm truncate">{project.name}</div>
      <div className="flex items-center gap-2 mt-1 text-xs text-gray-400">
        <span>{project.fileCount}개 파일</span>
        {project.summary?.issues?.length > 0 && (
          <span className="text-amber-500 font-medium">
            {project.summary.issues.length}건 확인 필요
          </span>
        )}
      </div>
    </button>
  )
}
