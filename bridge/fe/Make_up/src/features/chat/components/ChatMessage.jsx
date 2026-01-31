import { cn } from '@/shared/utils/cn'

export default function ChatMessage({ message, onSourceClick }) {
  const isUser = message.role === 'user'
  const isError = !isUser && message.isError

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-3 py-2 text-sm',
          isUser
            ? 'bg-primary-500 text-white'
            : isError
              ? 'bg-red-50 border border-red-200 text-red-700'
              : 'bg-white border border-gray-200 text-gray-800',
        )}
      >
        <p className="whitespace-pre-line">{message.content}</p>

        {message.sources?.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <p className="text-[10px] text-gray-400 mb-1">근거 문서</p>
            <div className="flex flex-wrap gap-1">
              {message.sources.map(src => (
                <button
                  key={src.fileId}
                  type="button"
                  className="text-[11px] text-primary-600 hover:text-primary-700 bg-primary-50 px-1.5 py-0.5 rounded hover:underline"
                  onClick={() => onSourceClick(src.fileId)}
                >
                  {src.fileName}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
