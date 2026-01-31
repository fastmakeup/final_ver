import { cn } from '@/shared/utils/cn'

const DOC_TYPE_COLORS = {
  '기안': 'bg-blue-100 text-blue-700',
  '입찰공고': 'bg-purple-100 text-purple-700',
  '계약서': 'bg-green-100 text-green-700',
  '지출결의서': 'bg-orange-100 text-orange-700',
  '설계변경': 'bg-red-100 text-red-700',
  '청렴서약서': 'bg-teal-100 text-teal-700',
  '검수조서': 'bg-cyan-100 text-cyan-700',
  '심의': 'bg-indigo-100 text-indigo-700',
  '통보': 'bg-gray-100 text-gray-700',
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${m}.${day}`
}

export default function TimelineNode({ file, isSelected, isLast, onSelect }) {
  const badgeColor = DOC_TYPE_COLORS[file.docType] ?? 'bg-gray-100 text-gray-600'

  return (
    <div className="flex gap-4">
      {/* 날짜 */}
      <div className="w-12 flex-shrink-0 text-right">
        <span className="text-xs text-gray-400 font-mono">
          {formatDate(file.date)}
        </span>
      </div>

      {/* 연결선 */}
      <div className="flex flex-col items-center">
        <div className={cn(
          'w-2.5 h-2.5 rounded-full border-2 flex-shrink-0',
          isSelected
            ? 'bg-primary-500 border-primary-500'
            : 'bg-white border-gray-300',
        )} />
        {!isLast && <div className="w-px flex-1 bg-gray-200" />}
      </div>

      {/* 문서 카드 */}
      <button
        type="button"
        className={cn(
          'flex-1 text-left rounded-lg border px-3 py-2 mb-3 transition-colors',
          isSelected
            ? 'border-primary-500/30 bg-primary-50'
            : 'border-gray-200 bg-white hover:border-gray-300',
        )}
        onClick={() => onSelect(file.id)}
      >
        <div className="flex items-center gap-2">
          <span className={cn('text-[10px] font-medium px-1.5 py-0.5 rounded', badgeColor)}>
            {file.docType}
          </span>
          <span className="text-sm text-gray-800 truncate">{file.name}</span>
        </div>
        {(file.summary || file.amount != null) && (
          <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
            {file.summary && <span className="truncate">{file.summary}</span>}
            {file.amount != null && (
              <span className="flex-shrink-0 font-medium text-gray-600">
                {file.amount.toLocaleString('ko-KR')}원
              </span>
            )}
          </div>
        )}
      </button>
    </div>
  )
}
