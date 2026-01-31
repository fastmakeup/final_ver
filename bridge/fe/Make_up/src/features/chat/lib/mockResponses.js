import { flattenFiles } from '@/features/timeline/lib/gapDetector'

const KEYWORD_RULES = [
  {
    keywords: ['예산', '금액', '얼마', '비용', '돈'],
    filter: f => f.amount != null,
    template: (files) => {
      const items = files.map(f =>
        `- ${f.name}: ${f.amount.toLocaleString('ko-KR')}원 (${f.summary})`
      )
      return `관련 금액 정보를 찾았습니다.\n\n${items.join('\n')}`
    },
  },
  {
    keywords: ['증액', '변경', '설계변경', '추가'],
    filter: f => f.docType === '설계변경' || f.docType === '변경계약서',
    template: (files) => {
      if (files.length === 0) return '설계변경 관련 문서를 찾지 못했습니다.'
      const f = files[0]
      return `${f.date} "${f.name}"에 따르면, ${f.summary}.\n\n금액: ${f.amount?.toLocaleString('ko-KR') ?? '미기재'}원`
    },
  },
  {
    keywords: ['계약', '업체', '체결'],
    filter: f => f.docType === '계약서',
    template: (files) => {
      const items = files.map(f =>
        `- ${f.date} ${f.name}: ${f.summary}`
      )
      return `계약 관련 문서입니다.\n\n${items.join('\n')}`
    },
  },
  {
    keywords: ['언제', '날짜', '일정', '기간'],
    filter: f => f.date != null,
    template: (files) => {
      const sorted = [...files].sort((a, b) => new Date(a.date) - new Date(b.date))
      const items = sorted.map(f => `- ${f.date} ${f.name}`)
      return `문서 일정 순서입니다.\n\n${items.join('\n')}`
    },
  },
  {
    keywords: ['지출', '결의', '지급'],
    filter: f => f.docType === '지출결의서',
    template: (files) => {
      const items = files.map(f =>
        `- ${f.date} ${f.name}: ${f.amount?.toLocaleString('ko-KR') ?? '미기재'}원`
      )
      return `지출 관련 문서입니다.\n\n${items.join('\n')}`
    },
  },
  {
    keywords: ['검수', '완료', '확인'],
    filter: f => f.docType === '검수조서',
    template: (files) => {
      if (files.length === 0) return '검수조서를 찾지 못했습니다. 누락 가능성이 있습니다.'
      const items = files.map(f => `- ${f.date} ${f.name}: ${f.summary}`)
      return `검수 관련 문서입니다.\n\n${items.join('\n')}`
    },
  },
]

/**
 * 프로젝트 문서와 질문을 기반으로 mock 응답 생성
 * @param {{ files: Array }} project
 * @param {string} query
 * @returns {{ answer: string, sources: Array<{ fileId: string, fileName: string }> }}
 */
export function generateMockResponse(project, query) {
  const flat = flattenFiles(project.files)
  const q = query.toLowerCase()

  // 키워드 규칙 매칭
  for (const rule of KEYWORD_RULES) {
    if (rule.keywords.some(kw => q.includes(kw))) {
      const matched = flat.filter(rule.filter)
      if (matched.length > 0) {
        return {
          answer: rule.template(matched),
          sources: matched.map(f => ({ fileId: f.id, fileName: f.name })),
        }
      }
    }
  }

  // 기본 응답: 프로젝트 전체 요약
  const fileList = flat.map(f => `- ${f.name} (${f.docType}): ${f.summary ?? '요약 없음'}`)
  return {
    answer: `"${project.name}" 업무에는 총 ${flat.length}개의 문서가 있습니다.\n\n${fileList.join('\n')}\n\n더 구체적인 질문을 해주시면 관련 문서를 찾아드리겠습니다.`,
    sources: flat.slice(0, 3).map(f => ({ fileId: f.id, fileName: f.name })),
  }
}
