import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import TaskItem from '@/features/fileExplorer/components/TaskItem'

export default function TaskList({ onTaskSelect }) {
  const { state } = useExplorer()

  return (
    <div className="p-3">
      <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-3">
        업무 목록 ({state.projects.length})
      </h2>
      <div className="flex flex-col gap-1">
        {state.projects.map(project => (
          <TaskItem key={project.id} project={project} onSelect={onTaskSelect} />
        ))}
      </div>
    </div>
  )
}
