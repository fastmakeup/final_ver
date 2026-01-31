import { useDocWriter } from '@/features/docWriter/hooks/useDocWriter'
import DocWriterSidebar from '@/features/docWriter/components/DocWriterSidebar'
import { TEMPLATE_COMPONENTS } from '../constants/templates'
import { useRef } from 'react'

export default function DocWriterPanel({ referenceFile }) {
  const { form, setField, draft, isGenerating, generate, reset, resetAll, setDraft, enableEditing } = useDocWriter()
  const documentRef = useRef(null)

  // AI가 분석한 데이터(structured) 가져오기
  const s = draft?.structured

  // 1. AI 분석 결과(templateType)에 따라 어떤 템플릿을 보여줄지 결정
  // draft가 없을 때는 기본 양식인 DEFAULT를 사용합니다.
  const SelectedTemplate = TEMPLATE_COMPONENTS[draft?.templateType] || TEMPLATE_COMPONENTS.DEFAULT
  
  // 예시 문서 클릭 핸들러 (읽기 전용으로 표시)
  const handleExampleClick = (exampleDoc) => {
    setDraft({
      structured: exampleDoc.data,
      templateType: exampleDoc.templateType,
      referenceFileName: exampleDoc.title,
      isEditable: false, // 읽기 전용
    })
  }
  
  // 작성 시작 핸들러
  const handleStartEditing = () => {
    enableEditing()
  }
  
  // PDF 다운로드
  // PDF 다운로드 (브라우저 인쇄 기능 사용)
  const handleDownloadPDF = () => {
    if (!documentRef.current) return
    
    const printWindow = window.open('', '_blank')
    const docContent = documentRef.current.outerHTML
    
    // 현재 페이지의 모든 스타일 가져오기
    const styles = Array.from(document.styleSheets)
      .map(styleSheet => {
        try {
          return Array.from(styleSheet.cssRules)
            .map(rule => rule.cssText)
            .join('\n')
        } catch (e) {
          return ''
        }
      })
      .join('\n')
    
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <title>공문 다운로드</title>
          <style>
            @page { 
              size: A4;
              margin: 0;
            }
            * {
              box-sizing: border-box;
              -webkit-print-color-adjust: exact !important;
              print-color-adjust: exact !important;
              color-adjust: exact !important;
            }
            html, body { 
              margin: 0;
              padding: 0;
              width: 210mm;
              font-family: -apple-system, BlinkMacSystemFont, "맑은 고딕", "Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
            }
            body {
              background: white !important;
              display: flex;
              justify-content: center;
              align-items: flex-start;
            }
            /* 다운로드 시 버튼과 구분선 숨기기 */
            button {
              display: none !important;
            }
            .page-break-line {
              display: none !important;
            }
            .opacity-0 {
              opacity: 0 !important;
            }
            /* 미리보기 모드 배지 숨기기 */
            .absolute.top-4.right-4 {
              display: none !important;
            }
            /* placeholder 숨기기 */
            input::placeholder,
            textarea::placeholder {
              color: transparent !important;
            }
            @media print {
              html, body {
                width: 210mm;
                margin: 0;
                padding: 0;
              }
              body { 
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important;
                background: white !important;
              }
              * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important;
              }
              button {
                display: none !important;
              }
              .page-break-line {
                display: none !important;
              }
              input::placeholder,
              textarea::placeholder {
                color: transparent !important;
              }
            }
            ${styles}
          </style>
        </head>
        <body>
          ${docContent}
        </body>
      </html>
    `)
    printWindow.document.close()
    
    // 폰트 로딩 대기 후 인쇄
    setTimeout(() => {
      printWindow.print()
    }, 500)
  }
  
  // 이전 인쇄 방식 (사용하지 않음)
  const handleDownloadPDF_old = () => {
    if (documentRef.current) {
      const printWindow = window.open('', '_blank')
      const docContent = documentRef.current.outerHTML
      
      // 현재 페이지의 모든 스타일 가져오기
      const styles = Array.from(document.styleSheets)
        .map(styleSheet => {
          try {
            return Array.from(styleSheet.cssRules)
              .map(rule => rule.cssText)
              .join('\n')
          } catch (e) {
            return ''
          }
        })
        .join('\n')
      
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <title>공문 다운로드</title>
            <style>
              @page { 
                size: A4;
                margin: 20mm;
              }
              * {
                box-sizing: border-box;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
              }
              html, body { 
                margin: 0;
                padding: 0;
                width: 210mm;
              }
              body {
                background: white !important;
                display: flex;
                justify-content: center;
                align-items: flex-start;
              }
              /* 다운로드 시 버튼 숨기기 */
              button {
                display: none !important;
              }
              .opacity-0 {
                opacity: 0 !important;
              }
              /* 미리보기 모드 배지 숨기기 */
              .absolute.top-4.right-4 {
                display: none !important;
              }
              /* A4 사이즈에 맞게 조정 */
              .w-\\[210mm\\] {
                width: 100% !important;
                max-width: 210mm;
                box-shadow: none !important;
              }
              .p-\\[20mm\\] {
                padding: 0 !important;
              }
              @media print {
                html, body {
                  width: 210mm;
                  margin: 0;
                  padding: 0;
                }
                body { 
                  -webkit-print-color-adjust: exact; 
                  print-color-adjust: exact;
                  background: white !important;
                }
                * {
                  -webkit-print-color-adjust: exact;
                  print-color-adjust: exact;
                }
                button {
                  display: none !important;
                }
              }
              ${styles}
            </style>
          </head>
          <body>
            ${docContent}
          </body>
        </html>
      `)
      printWindow.document.close()
      setTimeout(() => {
        printWindow.print()
      }, 500)
    }
  }
  
  // HWPX 다운로드 (HTML 파일로 저장)
  const handleDownloadHWPX = () => {
    if (documentRef.current) {
      const docContent = documentRef.current.outerHTML
      
      // 현재 페이지의 모든 스타일 가져오기
      const styles = Array.from(document.styleSheets)
        .map(styleSheet => {
          try {
            return Array.from(styleSheet.cssRules)
              .map(rule => rule.cssText)
              .join('\n')
          } catch (e) {
            return ''
          }
        })
        .join('\n')
      
      const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>공문</title>
  <style>
    * {
      box-sizing: border-box;
    }
    html, body { 
      margin: 0;
      padding: 0;
      background: #f5f5f5;
    }
    body {
      display: flex;
      justify-content: center;
      align-items: flex-start;
      padding: 20px;
    }
    /* 다운로드 시 버튼 숨기기 */
    button {
      display: none !important;
    }
    .opacity-0 {
      opacity: 0 !important;
    }
    /* 미리보기 모드 배지 숨기기 */
    .absolute.top-4.right-4 {
      display: none !important;
    }
    ${styles}
  </style>
</head>
<body>
  ${docContent}
</body>
</html>`
      
      const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `공문_${new Date().toISOString().split('T')[0]}.html`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* 문서 헤더 바: 분석 결과에 따라 제목과 상태 표시 */}
      <header className="flex-none flex items-center justify-between whitespace-nowrap border-b border-gray-200 bg-white px-6 py-3 z-20 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-8 h-8 rounded bg-primary-500/10 text-primary-600">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <h2 className="text-gray-900 text-[16px] font-bold leading-tight tracking-tight">
              {s?.docTitle ?? '새 공문 작성'}
            </h2>
            <p className="text-xs text-gray-500 font-medium">
              {s ? `${s.formId || ''} ${s.subtitle || ''}` : '표준 양식 Ver. 2024.03'}
            </p>
          </div>
          {s?.status && (
            <span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10 ml-2">
              {s.status}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <button className="hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            <span>도움말</span>
          </button>
        </div>
      </header>

      {/* 본문 영역 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 좌측: 선택된 템플릿 렌더링 영역 */}
        <main className="flex-1 bg-gray-200 overflow-y-auto p-10 flex justify-center">
          {/* 2. 핵심 로직: 
             draft가 있으면 AI 분석 기반의 'SelectedTemplate'을 보여주고,
             onChange(수정 함수)로 setField를 넘겨주어 실시간 편집이 가능하게 합니다.
          */}
          <div ref={documentRef}>
            <SelectedTemplate 
              data={s || form} 
              onChange={setField}
              isEditable={draft?.isEditable !== false} // 명시적으로 false가 아니면 편집 가능
            />
          </div>
        </main>

        {/* 우측: 사이드바 (가이드 및 액션) */}
        <DocWriterSidebar
          hasDraft={!!draft}
          onReset={reset}
          onResetAll={resetAll}
          onGenerate={() => generate(referenceFile)}
          isGenerating={isGenerating}
          canGenerate={!!form.title.trim() || !!s?.docTitle}
          referenceFileName={draft?.referenceFileName ?? referenceFile?.name ?? null}
          templateType={draft?.templateType || 'DEFAULT'}
          onExampleClick={handleExampleClick}
          isEditable={draft?.isEditable !== false}
          onStartEditing={handleStartEditing}
          onDownloadPDF={handleDownloadPDF}
        />
      </div>
    </div>
  )
}