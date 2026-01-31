import { apiCall } from '@/shared/lib/mockApi'

export function generateDraft(referenceFile, formData) {
  return apiCall('generate_draft', referenceFile, formData)
}
