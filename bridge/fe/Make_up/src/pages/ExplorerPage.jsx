import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'
import FolderUpload from '@/features/fileExplorer/components/FolderUpload'
import ExplorerLayout from '@/features/fileExplorer/components/ExplorerLayout'

export default function ExplorerPage() {
  const { state } = useExplorer()

  if (state.phase === 'upload') {
    return <FolderUpload />
  }

  return <ExplorerLayout />
}
