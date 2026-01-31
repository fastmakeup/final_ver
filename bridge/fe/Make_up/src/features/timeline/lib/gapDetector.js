/**
 * 중첩 파일 트리를 평탄화 (folder children 재귀 전개)
 * folder 자체는 제외하고 실제 파일만 반환
 */
export function flattenFiles(files) {
  const result = []
  for (const file of files) {
    if (file.children) {
      result.push(...flattenFiles(file.children))
    } else {
      result.push(file)
    }
  }
  return result
}

/**
 * 행정 절차상 누락된 문서를 탐지 (Rule Engine)
 *
 * @param {Array} files - 프로젝트 파일 트리
 * @returns {Array<{ id: string, level: 'error'|'warn', message: string, detail: string }>}
 */
export function detectGaps(files) {
  const flat = flattenFiles(files)
  const docTypes = flat.map(f => f.docType)
  const warnings = []
  let id = 0

  // Rule 1: 계약서 있으면 청렴서약서 필수
  if (docTypes.includes('계약서') && !docTypes.includes('청렴서약서')) {
    warnings.push({
      id: `gap-${++id}`,
      level: 'warn',
      message: '청렴서약서 누락',
      detail: '계약 체결 시 청렴서약서 첨부가 필수이나 폴더 내에서 확인되지 않았습니다.',
    })
  }

  // Rule 2: 설계변경 있으면 변경계약서 필수
  if (docTypes.includes('설계변경') && !docTypes.includes('변경계약서')) {
    warnings.push({
      id: `gap-${++id}`,
      level: 'error',
      message: '변경계약서 누락',
      detail: '설계변경 기안이 있으나 변경계약서가 확인되지 않았습니다. 감사 시 지적 가능성이 있습니다.',
    })
  }

  // Rule 3: 지출결의서 있으면 검수조서 필수
  if (docTypes.includes('지출결의서') && !docTypes.includes('검수조서')) {
    warnings.push({
      id: `gap-${++id}`,
      level: 'warn',
      message: '검수조서 누락',
      detail: '대금 지급(지출결의서) 전 검수 확인이 필요하나 검수조서가 확인되지 않았습니다.',
    })
  }

  // Rule 4: 기안 금액과 지출 금액 비교
  const 기안 = flat.find(f => f.docType === '기안' && f.amount)
  const 지출 = flat.find(f => f.docType === '지출결의서' && f.amount)
  const 설계변경 = flat.find(f => f.docType === '설계변경' && f.amount)

  if (기안 && 지출) {
    const expectedAmount = 기안.amount + (설계변경?.amount ?? 0)
    if (지출.amount !== 기안.amount && 지출.amount !== expectedAmount) {
      warnings.push({
        id: `gap-${++id}`,
        level: 'warn',
        message: '금액 불일치',
        detail: `기안 금액(${기안.amount.toLocaleString()}원)과 지출 금액(${지출.amount.toLocaleString()}원)이 일치하지 않습니다.`,
      })
    }
  }

  // Rule 5: 입찰공고 있으면 계약서 필수
  if (docTypes.includes('입찰공고') && !docTypes.includes('계약서')) {
    warnings.push({
      id: `gap-${++id}`,
      level: 'error',
      message: '계약서 누락',
      detail: '입찰 공고 후 계약 체결 기록이 확인되지 않았습니다.',
    })
  }

  return warnings
}
