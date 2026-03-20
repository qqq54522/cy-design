import { useEffect } from 'react'

interface ConfirmDialogProps {
  open: boolean
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmDialog({
  open, title = '确认', message, confirmText = '确定',
  cancelText = '取消', danger = false, onConfirm, onCancel,
}: ConfirmDialogProps) {
  useEffect(() => {
    if (!open) return
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onCancel() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, onCancel])

  if (!open) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onCancel}
    >
      <div
        className="bg-surface rounded-lg border border-border p-5 w-full max-w-sm space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-[15px] font-semibold">{title}</h3>
        <p className="text-[13px] text-text-secondary leading-relaxed">{message}</p>
        <div className="flex gap-2 justify-end pt-1">
          <button
            onClick={onCancel}
            className="px-4 py-1.5 text-[13px] text-text-secondary hover:text-text rounded-md hover:bg-surface-alt transition"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-1.5 text-[13px] text-white rounded-md transition ${
              danger ? 'bg-error hover:bg-error/80' : 'bg-primary hover:bg-primary-hover'
            }`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}
