import { isDev } from '@/shared/lib/env'
import { callPython } from '@/shared/lib/bridge'
import { delay } from '@/mocks/delay'
import { MOCK_PROJECTS } from '@/mocks/projects'
import { generateMockResponse } from '@/features/chat/lib/mockResponses'
import { generateMockDraft } from '@/features/docWriter/lib/mockDraftGenerator'

const mockHandlers = {
  get_projects: async () => delay(MOCK_PROJECTS),

  get_project_files: async (projectId) => {
    const project = MOCK_PROJECTS.find(p => p.id === projectId)
    return delay(project?.files ?? [])
  },

  analyze_folder: async () => {
    return delay({ projects: MOCK_PROJECTS, totalFiles: 13 }, 5000)
  },

  chat_query: async (projectId, query) => {
    const project = MOCK_PROJECTS.find(p => p.id === projectId)
    if (!project) return delay({ answer: '업무를 찾을 수 없습니다.', sources: [] })
    return delay(generateMockResponse(project, query), 800)
  },

  generate_draft: async (referenceFile, formData) => {
    return delay(generateMockDraft(referenceFile, formData), 1000)
  },

  open_folder_dialog: async () => {
    return delay('C:\\mock\\sample_folder', 500)
  },

  get_analysis_status: async (projectId) => {
    const project = MOCK_PROJECTS.find(p => p.id === projectId) || MOCK_PROJECTS[0]
    return delay({
      status: 'done',
      projectId,
      project,
    }, 3000)
  },
}

export async function apiCall(method, ...args) {
  try {
    if (!isDev) {
      return await callPython(method, ...args)
    }

    const handler = mockHandlers[method]
    if (handler) {
      console.info(`[mockApi] ${method}(${JSON.stringify(args)})`)
      return await handler(...args)
    }

    console.warn(`[mockApi] No mock handler for '${method}'`)
    return null
  } catch (err) {
    console.error(`[apiCall] ${method} 실패:`, err)
    throw err
  }
}
