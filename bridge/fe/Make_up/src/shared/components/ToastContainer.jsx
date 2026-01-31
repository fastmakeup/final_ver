import { createPortal } from 'react-dom'
import Toast from '@/shared/components/Toast'

export default function ToastContainer({ toasts, onRemove }) {
  if (toasts.length === 0) return null

  return createPortal(
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2.5">
      {toasts.map(t => (
        <Toast
          key={t.id}
          type={t.type}
          message={t.message}
          exiting={t.exiting}
          onRemove={() => onRemove(t.id)}
        />
      ))}
    </div>,
    document.getElementById('toast-root') || document.body,
  )
}
