import { cn } from '@/shared/utils/cn'
import { useExplorer } from '@/features/fileExplorer/hooks/useExplorer'

export default function FileTreeNode({ node, depth = 0 }) {
  const { state, dispatch } = useExplorer()
  const isFolder = node.children !== null
  const isExpanded = state.expandedFolders.has(node.id)
  const isSelected = state.selectedFileId === node.id

  function handleClick() {
    if (isFolder) {
      dispatch({ type: 'TOGGLE_FOLDER', folderId: node.id })
    } else {
      dispatch({ type: 'SELECT_FILE', fileId: node.id })
    }
  }

  return (
    <>
      <button
        type="button"
        className={cn(
          'w-full text-left py-1.5 pr-3 text-sm truncate transition-colors',
          isSelected && !isFolder
            ? 'bg-primary-50 text-primary-700'
            : 'hover:bg-gray-50 text-gray-600',
        )}
        style={{ paddingLeft: depth * 16 + 12 }}
        onClick={handleClick}
      >
        <span className="inline-block w-4 text-center mr-1 text-xs text-gray-400">
          {isFolder ? (isExpanded ? '\u25BE' : '\u25B8') : '\u2022'}
        </span>
        {node.name}
      </button>
      {isFolder && isExpanded && node.children.map(child => (
        <FileTreeNode key={child.id} node={child} depth={depth + 1} />
      ))}
    </>
  )
}
