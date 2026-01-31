import { useMemo } from 'react'
import { cn } from '@/shared/utils/cn'
import { detectGaps } from '@/features/timeline/lib/gapDetector'

const LEVEL_STYLES = {
  error: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    badge: 'bg-red-100 text-red-700',
    text: 'text-red-800',
    detail: 'text-red-600',
  },
  warn: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    badge: 'bg-amber-100 text-amber-700',
    text: 'text-amber-800',
    detail: 'text-amber-600',
  },
}

export default function WarningPanel({ files }) {
  const warnings = useMemo(() => detectGaps(files), [files])

  if (warnings.length === 0) {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3">
        <span className="text-sm font-medium text-green-700">
          이상 없음 — 누락 문서가 발견되지 않았습니다.
        </span>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <h2 className="text-sm font-bold text-gray-800">
        경고 {warnings.length}건
      </h2>
      {warnings.map(w => {
        const s = LEVEL_STYLES[w.level]
        return (
          <div
            key={w.id}
            className={cn('rounded-lg border px-4 py-3', s.bg, s.border)}
          >
            <div className="flex items-center gap-2">
              <span className={cn('text-xs font-medium px-1.5 py-0.5 rounded', s.badge)}>
                {w.level === 'error' ? '누락' : '주의'}
              </span>
              <span className={cn('text-sm font-medium', s.text)}>
                {w.message}
              </span>
            </div>
            <p className={cn('text-xs mt-1', s.detail)}>{w.detail}</p>
          </div>
        )
      })}
    </div>
  )
}
