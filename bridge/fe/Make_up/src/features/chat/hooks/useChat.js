import { useState, useCallback, useEffect, useRef } from 'react'
import { queryChatBot } from '@/features/chat/api/chatApi'

let msgId = 0
function nextId() {
  msgId += 1
  return `msg-${msgId}`
}

// 프로젝트별 메시지 캐시 (컴포넌트 언마운트 후에도 유지)
const messageCache = {}

export function useChat(projectId) {
  const [messages, setMessages] = useState(() => messageCache[projectId] ?? [])
  const [isLoading, setIsLoading] = useState(false)
  const prevProjectId = useRef(projectId)

  // 메시지 변경 시 캐시 동기화
  useEffect(() => {
    if (projectId) {
      messageCache[projectId] = messages
    }
  }, [messages, projectId])

  // 프로젝트 변경 시 해당 프로젝트 캐시 복원
  useEffect(() => {
    if (prevProjectId.current !== projectId) {
      setMessages(messageCache[projectId] ?? [])
      prevProjectId.current = projectId
    }
  }, [projectId])

  const sendMessage = useCallback(async (query) => {
    const trimmed = query.trim()
    if (!trimmed || !projectId) return

    const userMsg = {
      id: nextId(),
      role: 'user',
      content: trimmed,
      sources: null,
      timestamp: Date.now(),
    }

    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    try {
      const res = await queryChatBot(projectId, trimmed)
      const answer = res?.answer ?? '응답을 받지 못했습니다.'
      const isError = answer.includes('연결할 수 없습니다') ||
                      answer.includes('시간이 초과') ||
                      answer.includes('오류가 발생')
      const assistantMsg = {
        id: nextId(),
        role: 'assistant',
        content: answer,
        sources: res?.sources ?? null,
        isError,
        timestamp: Date.now(),
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch {
      const errorMsg = {
        id: nextId(),
        role: 'assistant',
        content: '응답을 생성하는 중 오류가 발생했습니다.\n다시 시도해주세요.',
        sources: null,
        isError: true,
        timestamp: Date.now(),
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }, [projectId])

  return { messages, isLoading, sendMessage }
}
