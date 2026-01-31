import { apiCall } from '@/shared/lib/mockApi'

export function queryChatBot(projectId, query) {
  return apiCall('chat_query', projectId, query)
}
