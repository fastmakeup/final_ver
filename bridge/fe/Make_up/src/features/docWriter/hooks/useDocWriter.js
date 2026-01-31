import { useState, useCallback } from 'react'
import { generateDraft } from '@/features/docWriter/api/docWriterApi'

const INITIAL_FORM = {
  title: '',
  amount: '',
  date: '',
  extra: '',
}

export function useDocWriter() {
  const [form, setForm] = useState(INITIAL_FORM)
  const [draft, setDraft] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)

  function setField(name, value) {
    // 편집 가능 상태가 아니면 무시
    if (draft && !draft.isEditable) return;
    
    // draft가 있으면 structured 데이터를 업데이트
    if (draft?.structured) {
      setDraft(prev => ({
        ...prev,
        structured: { ...prev.structured, [name]: value }
      }))
    } else {
      setForm(prev => ({ ...prev, [name]: value }))
    }
  }
  
  function enableEditing() {
    if (draft) {
      setDraft(prev => ({ ...prev, isEditable: true }))
    }
  }

  const generate = useCallback(async (referenceFile) => {
    if (!form.title.trim()) return
    setIsGenerating(true)

    try {
      const res = await generateDraft(referenceFile, form)
      setDraft(res)
    } catch {
      setDraft({
        draft: '초안 생성 중 오류가 발생했습니다. 다시 시도해주세요.',
        referenceFileName: null,
      })
    } finally {
      setIsGenerating(false)
    }
  }, [form])

  function reset() {
    setDraft(null)
  }

  function resetAll() {
    setDraft(null)
    setForm(INITIAL_FORM)
  }

  return { form, setField, draft, setDraft, isGenerating, generate, reset, resetAll, enableEditing }
}
