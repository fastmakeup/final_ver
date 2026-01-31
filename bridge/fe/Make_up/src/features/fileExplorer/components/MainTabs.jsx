import { cn } from '@/shared/utils/cn'

const TABS = [
  { id: 'timeline', label: '타임라인' },
  { id: 'chat', label: '질문하기' },
  { id: 'docWriter', label: '공문 작성' },
]

export default function MainTabs({ activeTab, onTabChange }) {
  return (
    <div className="flex border-b border-gray-200 px-6">
      {TABS.map(tab => (
        <button
          key={tab.id}
          type="button"
          className={cn(
            'px-4 py-2.5 text-sm font-medium transition-colors relative',
            activeTab === tab.id
              ? 'text-primary-600'
              : 'text-gray-500 hover:text-gray-700',
          )}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
          {activeTab === tab.id && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600" />
          )}
        </button>
      ))}
    </div>
  )
}
