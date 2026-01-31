import { cn } from '@/shared/utils/cn'
import { DOC_TYPE_COLORS, DOC_TYPE_ICONS } from '@/shared/constants/docTypes'

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

export default function FileCard({ file, isSelected, onClick }) {
  const badgeColor = DOC_TYPE_COLORS[file.docType] ?? 'bg-gray-100 text-gray-600'
  const iconBg = DOC_TYPE_ICONS[file.docType] ?? 'bg-gray-500'

  return (
    <button
      type="button"
      className={cn(
        'w-full text-left rounded-xl border p-4 transition-all',
        'hover:shadow-md hover:border-primary-200',
        isSelected
          ? 'border-primary-300 bg-primary-50/30 shadow-sm'
          : 'border-gray-200 bg-white',
      )}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        {/* 문서 유형 아이콘 */}
        <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center shrink-0', iconBg)}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
        </div>

        <div className="min-w-0 flex-1">
          {/* 파일명 */}
          <p className="text-sm font-medium text-gray-800 truncate">
            {file.name}
          </p>

          {/* 날짜 + 유형 배지 */}
          <div className="flex items-center gap-2 mt-1.5">
            <span className={cn('text-[10px] font-medium px-1.5 py-0.5 rounded', badgeColor)}>
              {file.docType}
            </span>
            {file.date && (
              <span className="text-[11px] text-gray-400">
                {formatDate(file.date)}
              </span>
            )}
          </div>

          {/* 금액 */}
          {file.amount != null && (
            <p className="text-xs text-gray-500 mt-1.5">
              {file.amount.toLocaleString('ko-KR')}원
            </p>
          )}
        </div>
      </div>
    </button>
  )
}
