import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'

export default function FileDetail({ onStartDocWriter }) {
  const { selectedFile } = useExplorer()

  if (!selectedFile) {
    return (
      <div className="p-4 text-sm text-gray-300 text-center">
        파일을 선택하세요
      </div>
    )
  }

  return (
    <div className="p-4 animate-fade-in">
      <h3 className="text-sm font-semibold text-gray-800 truncate mb-3">
        {selectedFile.name}
      </h3>
      <dl className="space-y-2 text-xs">
        {selectedFile.date && (
          <div className="flex justify-between">
            <dt className="text-gray-400">날짜</dt>
            <dd className="text-gray-700">{selectedFile.date}</dd>
          </div>
        )}
        {selectedFile.amount != null && (
          <div className="flex justify-between">
            <dt className="text-gray-400">금액</dt>
            <dd className="text-gray-700">{selectedFile.amount.toLocaleString('ko-KR')}원</dd>
          </div>
        )}
        {selectedFile.docType && (
          <div className="flex justify-between">
            <dt className="text-gray-400">유형</dt>
            <dd>
              <span className="inline-block px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                {selectedFile.docType}
              </span>
            </dd>
          </div>
        )}
        {selectedFile.summary && (
          <div className="pt-2 border-t border-gray-100">
            <dt className="text-gray-400 mb-1">요약</dt>
            <dd className="text-gray-600 leading-relaxed">{selectedFile.summary}</dd>
          </div>
        )}
      </dl>
      {onStartDocWriter && (
        <button
          type="button"
          className="mt-3 w-full px-3 py-1.5 text-xs font-medium text-primary-600 border border-primary-500/30 rounded-lg hover:bg-primary-50 transition-colors"
          onClick={onStartDocWriter}
        >
          새 공문 작성
        </button>
      )}
    </div>
  )
}
