import { useEffect, useRef } from 'react'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import { useChat } from '@/features/chat/hooks/useChat'
import ChatMessage from '@/features/chat/components/ChatMessage'
import ChatInput from '@/features/chat/components/ChatInput'

export default function ChatPanel({ projectId }) {
  const { dispatch } = useExplorer()
  const { messages, isLoading, sendMessage } = useChat(projectId)
  const scrollRef = useRef(null)

  // 새 메시지 시 자동 스크롤
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  function handleSourceClick(fileId) {
    dispatch({ type: 'SELECT_FILE', fileId })
  }

  return (
    <div className="flex flex-col h-full">
      {/* 메시지 영역 */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-400 text-sm">
              <p className="mb-1">업무 문서에 대해 질문해보세요.</p>
              <p className="text-xs text-gray-300">
                예: "예산 왜 증액됐어?", "계약 언제 했어?"
              </p>
            </div>
          </div>
        )}
        {messages.map(msg => (
          <ChatMessage
            key={msg.id}
            message={msg}
            onSourceClick={handleSourceClick}
          />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-400">
              답변 생성 중...
            </div>
          </div>
        )}
      </div>

      {/* 입력 영역 */}
      <div className="border-t border-gray-200 p-4">
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  )
}
