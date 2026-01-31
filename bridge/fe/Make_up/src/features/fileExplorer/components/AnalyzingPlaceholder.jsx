import { useState, useEffect } from 'react'
import { cn } from '@/shared/utils/cn'

const STEPS = [
  { label: '파일 파싱 중', description: 'HWP, Excel 문서를 읽고 있습니다' },
  { label: '메타데이터 추출', description: '날짜, 금액, 문서 유형을 분석합니다' },
  { label: '업무 분류 중', description: '프로젝트 단위로 문서를 그룹핑합니다' },
  { label: '누락 문서 탐지', description: '행정 절차상 빠진 문서를 확인합니다' },
]

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function Spinner({ className }) {
  return (
    <div className={cn('border-2 border-current border-t-transparent rounded-full animate-spin', className)} />
  )
}

export default function AnalyzingPlaceholder() {
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < STEPS.length - 1) return prev + 1
        return prev
      })
    }, 1200)
    return () => clearInterval(timer)
  }, [])

  const progress = Math.min(((currentStep + 1) / STEPS.length) * 100, 100)

  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <div className="w-full max-w-md">
        {/* 상단 아이콘 + 제목 */}
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 rounded-2xl bg-primary-50 border border-primary-100 flex items-center justify-center mb-4">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
          </div>
          <h2 className="text-lg font-bold text-gray-800">문서를 분석하고 있습니다</h2>
          <p className="text-sm text-gray-400 mt-1">잠시만 기다려주세요</p>
        </div>

        {/* 프로그레스 바 */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-gray-500">진행률</span>
            <span className="text-xs font-semibold text-primary-600">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* 단계 목록 */}
        <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
          {STEPS.map((step, i) => {
            const isDone = i < currentStep
            const isActive = i === currentStep
            const isPending = i > currentStep

            return (
              <div
                key={i}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 transition-all duration-300',
                  isActive && 'bg-primary-50/40',
                )}
              >
                {/* 상태 아이콘 */}
                <div className={cn(
                  'w-7 h-7 rounded-full flex items-center justify-center shrink-0 transition-all duration-300',
                  isDone && 'bg-primary-500 text-white',
                  isActive && 'bg-white border-2 border-primary-500 text-primary-500',
                  isPending && 'bg-gray-100 text-gray-300',
                )}>
                  {isDone && <CheckIcon />}
                  {isActive && <Spinner className="w-3.5 h-3.5" />}
                  {isPending && <span className="text-xs font-medium">{i + 1}</span>}
                </div>

                {/* 텍스트 */}
                <div className="min-w-0 flex-1">
                  <p className={cn(
                    'text-sm transition-colors duration-300',
                    isDone && 'text-gray-500',
                    isActive && 'text-gray-800 font-medium',
                    isPending && 'text-gray-400',
                  )}>
                    {step.label}
                  </p>
                  {isActive && (
                    <p className="text-xs text-gray-400 mt-0.5">{step.description}</p>
                  )}
                </div>

                {/* 완료 표시 */}
                {isDone && (
                  <span className="text-[10px] text-primary-500 font-medium shrink-0">완료</span>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
