import { createContext, useReducer, useMemo, useEffect, useRef } from 'react'
import { fetchAnalysisStatus } from '@/features/fileExplorer/api/explorerApi'

const initialState = {
  phase: 'upload',          // 'upload' | 'exploring'
  isAnalyzing: false,
  projects: [],
  selectedProjectId: null,
  selectedFileId: null,
  expandedFolders: new Set(),
  aiStatus: null,           // null | 'pending' | 'analyzing' | 'done' | 'error'
  analysisProjectId: null,  // 현재 AI 분석 중인 프로젝트 ID
}

function explorerReducer(state, action) {
  switch (action.type) {
    case 'ANALYZE_START':
      return { ...state, isAnalyzing: true, phase: 'exploring' }

    case 'ANALYZE_SUCCESS': {
      const projectId = action.projects?.[0]?.id ?? null
      return {
        ...state,
        isAnalyzing: false,
        phase: 'exploring',
        projects: action.projects,
        aiStatus: 'pending',
        analysisProjectId: projectId,
      }
    }

    case 'ANALYZE_FAIL':
      return { ...state, isAnalyzing: false, phase: 'upload', aiStatus: null, analysisProjectId: null }

    case 'AI_ANALYSIS_COMPLETE': {
      const updated = action.project
      if (!updated) return { ...state, aiStatus: 'done' }
      return {
        ...state,
        aiStatus: 'done',
        projects: state.projects.map(p =>
          p.id === updated.id ? updated : p,
        ),
      }
    }

    case 'AI_ANALYSIS_ERROR':
      return { ...state, aiStatus: 'error' }

    case 'SELECT_PROJECT':
      return {
        ...state,
        selectedProjectId: action.projectId,
        selectedFileId: null,
      }

    case 'SELECT_FILE':
      return { ...state, selectedFileId: action.fileId }

    case 'TOGGLE_FOLDER': {
      const next = new Set(state.expandedFolders)
      if (next.has(action.folderId)) {
        next.delete(action.folderId)
      } else {
        next.add(action.folderId)
      }
      return { ...state, expandedFolders: next }
    }

    case 'RESET':
      return initialState

    default:
      return state
  }
}

export const ExplorerContext = createContext(null)

function findFileInTree(files, fileId) {
  for (const file of files) {
    if (file.id === fileId) return file
    if (file.children) {
      const found = findFileInTree(file.children, fileId)
      if (found) return found
    }
  }
  return null
}

export function ExplorerProvider({ children }) {
  const [state, dispatch] = useReducer(explorerReducer, initialState)
  const pollingRef = useRef(null)

  // AI 분석 결과 폴링
  useEffect(() => {
    const { analysisProjectId, aiStatus } = state
    if (!analysisProjectId || aiStatus === 'done' || aiStatus === 'error') {
      return
    }

    pollingRef.current = setInterval(async () => {
      try {
        const res = await fetchAnalysisStatus(analysisProjectId)
        if (res?.status === 'done') {
          dispatch({ type: 'AI_ANALYSIS_COMPLETE', project: res.project })
          clearInterval(pollingRef.current)
        } else if (res?.status === 'error') {
          dispatch({ type: 'AI_ANALYSIS_ERROR' })
          clearInterval(pollingRef.current)
        }
      } catch (err) {
        console.error('[ExplorerContext] AI 분석 상태 조회 실패:', err)
      }
    }, 3000)

    return () => clearInterval(pollingRef.current)
  }, [state.analysisProjectId, state.aiStatus])

  const selectedProject = useMemo(
    () => state.projects.find(p => p.id === state.selectedProjectId) ?? null,
    [state.projects, state.selectedProjectId],
  )

  const selectedFile = useMemo(() => {
    if (!selectedProject || !state.selectedFileId) return null
    return findFileInTree(selectedProject.files, state.selectedFileId)
  }, [selectedProject, state.selectedFileId])

  const value = useMemo(
    () => ({ state, dispatch, selectedProject, selectedFile }),
    [state, selectedProject, selectedFile],
  )

  return (
    <ExplorerContext.Provider value={value}>
      {children}
    </ExplorerContext.Provider>
  )
}
