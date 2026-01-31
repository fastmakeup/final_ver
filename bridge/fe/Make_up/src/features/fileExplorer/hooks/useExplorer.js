import { useContext } from 'react'
import { ExplorerContext } from '@/features/fileExplorer/context/ExplorerContext'

export function useExplorer() {
  const ctx = useContext(ExplorerContext)
  if (!ctx) throw new Error('useExplorer must be used within ExplorerProvider')
  return ctx
}
