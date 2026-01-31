import { cn } from '@/shared/utils/cn'

export default function DraftViewer({ draft }) {
  const s = draft.structured

  if (!s) {
    // 구조화 데이터 없으면 plain text fallback
    return (
      <div className="document-paper relative w-full max-w-[800px] min-h-[900px] bg-white text-gray-900 p-12 sm:p-16 flex flex-col gap-8 shadow-lg">
        <pre className="text-sm whitespace-pre-wrap font-sans leading-relaxed">{draft.draft}</pre>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'relative w-full max-w-[800px] min-h-[900px]',
        'bg-white text-gray-900 p-12 sm:p-16',
        'flex flex-col gap-8',
        'shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-1px_rgba(0,0,0,0.06),0_0_40px_rgba(0,0,0,0.05)]',
      )}
    >
      {/* 문서 헤더 */}
      <div className="border-b-2 border-black pb-6 text-center">
        <h1 className="text-3xl font-bold tracking-widest mb-2">{s.docTitle}</h1>
        <p className="text-sm text-gray-500 tracking-wide">
          [{s.formId}] {s.subtitle}
        </p>
      </div>

      {/* 문서 본문 */}
      <div className="flex flex-col gap-6 text-[15px] leading-relaxed">
        {s.sections.map((section, idx) => (
          <div key={idx} className="flex flex-col gap-2 relative">
            <h3 className="font-bold text-lg flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-black rounded-full" />
              {section.title}
            </h3>

            {/* 테이블 타입 */}
            {section.type === 'table' && (
              <table className="w-full border-collapse border border-gray-300 text-sm">
                <tbody>
                  {section.rows.map((row, ri) => (
                    <tr key={ri}>
                      {row.map((cell, ci) =>
                        cell.colSpan ? (
                          <td key={ci} className="border border-gray-300" colSpan={cell.colSpan}>
                            <span className="inline-block bg-gray-50 font-bold text-center p-3 border-r border-gray-300 w-32">
                              {cell.label}
                            </span>
                            <span className="p-3">{cell.value}</span>
                          </td>
                        ) : (
                          [
                            <td key={`${ci}-label`} className="border border-gray-300 bg-gray-50 p-3 w-32 font-bold text-center">
                              {cell.label}
                            </td>,
                            <td key={`${ci}-value`} className="border border-gray-300 p-3">
                              {cell.value}
                            </td>,
                          ]
                        ),
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* 텍스트 타입 */}
            {section.type === 'text' && (
              <div className="relative">
                {/* AI 팁 인디케이터 */}
                {section.aiTip && (
                  <div className="absolute -left-10 top-1 hidden lg:flex items-center justify-center cursor-pointer group/tooltip z-10">
                    <span className="relative flex h-6 w-6">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-500 opacity-75" />
                      <span className="relative inline-flex rounded-full h-6 w-6 bg-primary-500 items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM4 11a1 1 0 100-2H3a1 1 0 000 2h1zM10 18a1 1 0 001-1v-1a1 1 0 10-2 0v1a1 1 0 001 1z" />
                          <path fillRule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z" clipRule="evenodd" />
                        </svg>
                      </span>
                    </span>
                    {/* 툴팁 */}
                    <div className="absolute left-8 top-0 w-72 p-4 bg-white rounded-xl shadow-xl border border-primary-500/20 z-50 opacity-0 group-hover/tooltip:opacity-100 transition-opacity pointer-events-none group-hover/tooltip:pointer-events-auto">
                      <div className="flex gap-3">
                        <svg className="w-5 h-5 text-primary-500 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zm7-10a1 1 0 01.967.744L14.146 7.2 17.5 8.512a1 1 0 010 1.876l-3.354 1.312-1.179 4.456a1 1 0 01-1.934 0L9.854 11.7 6.5 10.388a1 1 0 010-1.876l3.354-1.312L11.033 2.744A1 1 0 0112 2z" />
                        </svg>
                        <div className="flex flex-col gap-1">
                          <p className="text-sm font-bold text-gray-900">AI 작성 팁</p>
                          <p className="text-xs text-gray-600 leading-normal">{section.aiTip}</p>
                        </div>
                      </div>
                      <div className="absolute -left-2 top-2 w-4 h-4 bg-white border-l border-t border-primary-500/20 rotate-45 transform" />
                    </div>
                  </div>
                )}
                <div className="border border-gray-300 p-4 min-h-[80px] bg-blue-50/10">
                  <p className="text-gray-700">{section.content}</p>
                </div>
              </div>
            )}

            {/* 금액 변경 테이블 */}
            {section.type === 'amountTable' && (
              <table className="w-full border-collapse border border-gray-300 text-sm text-center">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-300 p-2">구분</th>
                    <th className="border border-gray-300 p-2">변경 전</th>
                    <th className="border border-gray-300 p-2">변경 후</th>
                    <th className="border border-gray-300 p-2">증감액</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="border border-gray-300 p-3 font-bold">금액 (VAT 포함)</td>
                    <td className="border border-gray-300 p-3 text-right">{section.prevAmount}</td>
                    <td className="border border-gray-300 p-3 text-right bg-blue-50/20">{section.newAmount}</td>
                    <td className={cn(
                      'border border-gray-300 p-3 text-right font-medium',
                      section.diff !== '-' ? 'text-red-600' : '',
                    )}>
                      {section.diff}
                    </td>
                  </tr>
                </tbody>
              </table>
            )}
          </div>
        ))}

        {/* 추가 사항 */}
        {s.extra && (
          <div className="flex flex-col gap-2">
            <h3 className="font-bold text-lg flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-black rounded-full" />
              4. 추가 사항
            </h3>
            <div className="border border-gray-300 p-4 bg-blue-50/10">
              <p className="text-gray-700">{s.extra}</p>
            </div>
          </div>
        )}

        {/* 서명 영역 */}
        <div className="mt-8 pt-8 border-t border-gray-300 text-center flex flex-col gap-8">
          <p>위와 같이 기안합니다.</p>
          <p>{s.signature.date}</p>
          <div className="flex justify-around mt-8">
            <div className="flex flex-col items-center gap-4">
              <p className="font-bold">발주자 (갑)</p>
              <p>{s.signature.issuer}</p>
              <div className="w-24 h-24 border-2 border-gray-200 rounded-full flex items-center justify-center text-gray-300 text-xs relative">
                (인)
                <div className="absolute inset-0 flex items-center justify-center opacity-10">
                  <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
            <div className="flex flex-col items-center gap-4">
              <p className="font-bold">계약상대자 (을)</p>
              <p>{s.signature.contractor}</p>
              <div className="w-24 h-24 border-2 border-gray-200 rounded-full flex items-center justify-center text-gray-300 text-xs">
                (인)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 페이지 번호 */}
      <div className="absolute bottom-6 left-0 right-0 text-center text-xs text-gray-400">
        - 1 -
      </div>
    </div>
  )
}
