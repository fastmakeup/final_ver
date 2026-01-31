import FileTreeNode from '@/features/fileExplorer/components/FileTreeNode'

export default function FileTree({ files }) {
  if (!files?.length) return null

  return (
    <div className="py-2">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1 px-3">
        파일
      </h3>
      {files.map(node => (
        <FileTreeNode key={node.id} node={node} />
      ))}
    </div>
  )
}
