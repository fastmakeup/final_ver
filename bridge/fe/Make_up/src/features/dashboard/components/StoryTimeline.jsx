import { cn } from '@/shared/utils/cn'

function isValidDate(dateStr) {
  if (!dateStr) return false
  const d = new Date(dateStr)
  return !Number.isNaN(d.getTime())
}

function formatShortDate(dateStr) {
  if (!isValidDate(dateStr)) return '날짜 없음'
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}월 ${d.getDate()}일`
}

function formatYear(dateStr) {
  if (!isValidDate(dateStr)) return null
  return new Date(dateStr).getFullYear()
}

/**
 * AI가 제공한 timeline.phases + timeline.events를 렌더링
 * 프론트는 데이터를 해석하지 않고 그대로 표시
 */
export default function StoryTimeline({ timeline, onFileSelect }) {
  const { phases = [], events = [] } = timeline ?? {}

  // phaseId → phase 색상 맵
  const phaseMap = Object.fromEntries(phases.map(p => [p.id, p]))

  // 날짜 있는 이벤트를 날짜순 정렬 + 날짜 없는 이벤트는 뒤에 배치
  const sortedEvents = [...events].sort((a, b) => {
    const aValid = isValidDate(a.date)
    const bValid = isValidDate(b.date)
    if (aValid && bValid) return new Date(a.date) - new Date(b.date)
    if (aValid) return -1
    if (bValid) return 1
    return 0
  })

  if (sortedEvents.length === 0) {
    return <p className="text-sm text-gray-400">표시할 이벤트가 없습니다.</p>
  }

  // 연도 변경 감지용
  let lastYear = null

  return (
    <div>
      {/* 단계 범례 */}
      {phases.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-5">
          {phases.map(phase => (
            <div key={phase.id} className="flex items-center gap-1.5">
              <div
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: phase.color }}
              />
              <span className="text-xs text-gray-500">{phase.name}</span>
            </div>
          ))}
        </div>
      )}

      {/* 이벤트 목록 */}
      <div>
        {sortedEvents.map((event, i) => {
          const phase = phaseMap[event.phaseId]
          const color = phase?.color ?? '#9ca3af'
          const isLast = i === sortedEvents.length - 1
          const year = formatYear(event.date)
          const showYear = year != null && year !== lastYear
          if (year != null) lastYear = year

          return (
            <div key={`${event.fileId}-${i}`}>
              {/* 연도 구분 */}
              {showYear && (
                <div className="flex items-center gap-3 mb-3 mt-1">
                  <span className="text-xs font-bold text-gray-800 bg-gray-100 px-2 py-0.5 rounded">
                    {year}
                  </span>
                  <div className="flex-1 h-px bg-gray-200" />
                </div>
              )}

              <div className="flex gap-4 group">
                {/* 타임라인 도트 + 연결선 */}
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      'w-3 h-3 rounded-full border-2 shrink-0 transition-all',
                      event.highlight
                        ? 'ring-2 ring-offset-1'
                        : 'group-hover:scale-125',
                    )}
                    style={{
                      backgroundColor: event.highlight ? color : '#fff',
                      borderColor: color,
                      ringColor: event.highlight ? color : undefined,
                    }}
                  />
                  {!isLast && (
                    <div className="w-px flex-1 bg-gray-200 min-h-[24px]" />
                  )}
                </div>

                {/* 이벤트 카드 */}
                <button
                  type="button"
                  className={cn(
                    'flex-1 text-left rounded-xl border bg-white',
                    'px-4 py-3 mb-3 transition-all',
                    event.highlight
                      ? 'border-amber-200 bg-amber-50/30 hover:border-amber-300'
                      : 'border-gray-200 hover:border-primary-200 hover:shadow-sm',
                  )}
                  onClick={() => event.fileId && onFileSelect(event.fileId)}
                >
                  {/* 상단: 날짜 + 단계 */}
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-400 font-mono shrink-0">
                      {formatShortDate(event.date)}
                    </span>
                    {phase && (
                      <span
                        className="text-[10px] font-medium px-1.5 py-0.5 rounded"
                        style={{
                          backgroundColor: `${color}18`,
                          color: color,
                        }}
                      >
                        {phase.name}
                      </span>
                    )}
                    {event.highlight && (
                      <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-amber-100 text-amber-700">
                        주요
                      </span>
                    )}
                  </div>

                  {/* 라벨 */}
                  <p className="text-sm font-medium text-gray-800">{event.label}</p>

                  {/* 설명 */}
                  {event.description && (
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed line-clamp-2">
                      {event.description}
                    </p>
                  )}

                  {/* 금액 */}
                  {event.amount != null && (
                    <p className="text-xs text-gray-600 font-medium mt-1">
                      {event.amount.toLocaleString('ko-KR')}원
                    </p>
                  )}
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
