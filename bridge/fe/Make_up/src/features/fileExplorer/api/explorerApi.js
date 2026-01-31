import { apiCall } from '@/shared/lib/mockApi'

export function fetchProjects() {
  return apiCall('get_projects')
}

export function fetchProjectFiles(projectId) {
  return apiCall('get_project_files', projectId)
}

export function analyzeFolder(folderPath) {
  return apiCall('analyze_folder', folderPath)
}

export function openFolderDialog() {
  return apiCall('open_folder_dialog')
}

export function fetchAnalysisStatus(projectId) {
  return apiCall('get_analysis_status', projectId)
}
