/**
 * 참고 문서 + 폼 데이터를 기반으로 mock 공문 초안 생성
 * @param {object|null} referenceFile - 참고 문서 (null이면 빈 참고)
 * @param {{ title: string, amount: string, date: string, extra: string }} formData
 * @returns {{ draft: string, referenceFileName: string|null, structured: object }}
 */
export function generateMockDraft(referenceFile, formData) {
  const { title, amount, date, extra } = formData
  const amountNum = Number(amount.replace(/[^0-9]/g, ''))
  const formattedAmount = amountNum
    ? amountNum.toLocaleString('ko-KR')
    : amount

  const prevAmount = referenceFile?.amount
    ? referenceFile.amount.toLocaleString('ko-KR')
    : null

  const diff = referenceFile?.amount && amountNum
    ? amountNum - referenceFile.amount
    : null

  const diffFormatted = diff
    ? `${diff >= 0 ? '+' : ''}${diff.toLocaleString('ko-KR')}`
    : null

  // 구조화된 데이터
  const structured = {
    docTitle: '기  안  문',
    formId: 'Form-2024-A',
    subtitle: '공공 행정 표준 서식',
    status: '검토 중',
    sections: [
      {
        title: '1. 사업 개요',
        type: 'table',
        rows: [
          [
            { label: '사업명', value: title },
            { label: '시행일자', value: date || '-' },
          ],
          [
            { label: '사업비', value: `${formattedAmount}원`, colSpan: 3 },
          ],
        ],
      },
      {
        title: '2. 추진배경',
        type: 'text',
        content: `${referenceFile?.summary ?? '관련 사업'}과 관련하여 ${title}을(를) 아래와 같이 추진하고자 합니다.`,
        aiTip: '추진배경에 구체적인 정책 근거(조례, 계획 등)를 포함하면 기안 승인률이 높아집니다.',
      },
      {
        title: '3. 사업비 변경 내역',
        type: 'amountTable',
        prevAmount: prevAmount ? `${prevAmount}원` : '-',
        newAmount: `${formattedAmount}원`,
        diff: diffFormatted ? `${diffFormatted}원` : '-',
      },
    ],
    extra: extra?.trim() || null,
    signature: {
      date: date || '-',
      issuer: '○○시청',
      contractor: referenceFile?.summary?.match(/\(주\)[^\s,]+/)?.[0] ?? '(주)○○○',
    },
  }

  // 하위 호환 plain text
  const refSection = referenceFile
    ? `\n참고 문서: ${referenceFile.name}\n(${referenceFile.summary ?? '요약 없음'})`
    : ''

  const prevInfo = referenceFile?.amount
    ? `\n3. 전년 대비 변경사항\n   가. 예산 변경: ${referenceFile.amount.toLocaleString('ko-KR')}원 → ${formattedAmount}원`
    : ''

  const extraSection = extra?.trim()
    ? `\n   나. 추가 사항: ${extra.trim()}`
    : ''

  const draft = `                    기  안  문

제목: ${title} 기본계획 수립(안)

1. 추진배경
   ${referenceFile?.summary ?? '관련 사업'}과 관련하여
   ${title}을(를) 아래와 같이 추진하고자 합니다.

2. 사업개요
   가. 사 업 명: ${title}
   나. 사 업 비: 금${formattedAmount}원
   다. 시행일자: ${date}
   라. 장    소: ○○ 일원
${prevInfo}${extraSection}

4. 행정사항
   가. 관련 예산 확보 후 집행
   나. 관련 부서 협조 요청

붙임  1. 세부 추진계획 1부.  끝.
${refSection}`

  return {
    draft,
    referenceFileName: referenceFile?.name ?? null,
    templateType: 'GOV_ELECTRONIC',
    structured,
  }
}
