import { cn } from '@/shared/utils/cn'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import { flattenFiles } from '@/features/timeline/lib/gapDetector'
import StoryTimeline from '@/features/dashboard/components/StoryTimeline'
import SummaryPanel from '@/features/dashboard/components/SummaryPanel'

export default function TaskDashboard({ onFileSelect, onExpand }) {
  const { selectedProject } = useExplorer()

  if (!selectedProject) return null

  const { summary } = selectedProject
  const timeline = summary?.timeline
  const allFiles = flattenFiles(selectedProject.files)

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* 좌측: 타임라인 (업무 흐름) */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl">
          <h2 className="text-base font-bold text-gray-800 mb-1">업무 흐름</h2>
          <p className="text-xs text-gray-400 mb-5">
            문서를 클릭하면 상세 내용과 AI 분석을 확인할 수 있습니다
          </p>

          {timeline ? (
            <StoryTimeline
              timeline={timeline}
              onFileSelect={onFileSelect}
            />
          ) : (
            <p className="text-sm text-gray-400">타임라인 정보가 없습니다.</p>
          )}
        </div>
      </div>

      {/* 우측: 요약 패널 */}
      <SummaryPanel
        summary={summary}
        allFiles={allFiles}
        onFileSelect={onFileSelect}
        onExpand={onExpand}
      />
    </div>
  )
}
