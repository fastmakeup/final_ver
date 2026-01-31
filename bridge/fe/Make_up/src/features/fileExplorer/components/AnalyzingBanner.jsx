import { cn } from '@/shared/utils/cn'

export default function AnalyzingBanner({ stage = 'local' }) {
  const isAi = stage === 'ai'

  return (
    <div className={cn(
      'shrink-0 px-4 py-2 flex items-center gap-3',
      isAi ? 'bg-amber-500 text-white' : 'bg-primary-600 text-white',
    )}>
      <div className={cn(
        'w-4 h-4 border-2 border-t-transparent rounded-full animate-spin shrink-0',
        isAi ? 'border-white' : 'border-white',
      )} />
      <p className="text-sm font-medium">
        {isAi ? 'AI 분석 진행 중' : '문서 분석 중'}
      </p>
      <span className={cn('text-xs', isAi ? 'text-amber-200' : 'text-primary-200')}>|</span>
      <p className={cn('text-xs', isAi ? 'text-amber-100' : 'text-primary-100')}>
        {isAi
          ? 'AI가 문서 요약, 타임라인, 이슈를 분석하고 있습니다. 완료되면 자동으로 업데이트됩니다.'
          : '파일을 파싱하고 업무를 분류하고 있습니다. 완료되면 자동으로 결과가 표시됩니다.'
        }
      </p>
    </div>
  )
}
