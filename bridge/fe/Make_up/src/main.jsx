import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { initBridge } from '@/shared/lib/bridge'
import { ExplorerProvider } from '@/features/fileExplorer'
import { ToastProvider } from '@/shared/context/ToastContext'

// pywebview 브릿지 초기화 (연결 실패해도 앱은 정상 렌더링)
initBridge()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ToastProvider>
      <ExplorerProvider>
        <App />
      </ExplorerProvider>
    </ToastProvider>
  </StrictMode>,
)
