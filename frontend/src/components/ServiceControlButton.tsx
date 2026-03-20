import { useState } from 'react'

type ServiceControlButtonProps = {
  running: boolean
  onStart: () => Promise<void>
  onStop: () => Promise<void>
  size?: 'sm' | 'md'
}

export default function ServiceControlButton({ running, onStart, onStop, size = 'sm' }: ServiceControlButtonProps) {
  const [loading, setLoading] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    try {
      if (running) {
        await onStop()
      } else {
        await onStart()
      }
    } finally {
      setLoading(false)
    }
  }

  const sizeClass = size === 'md'
    ? 'px-4 py-2 text-sm'
    : 'px-3 py-1.5 text-xs'

  if (loading) {
    return (
      <button disabled className={`inline-flex items-center gap-1.5 rounded-full bg-text-tertiary/15 font-medium text-text-secondary ${sizeClass}`}>
        <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-text-secondary border-t-transparent" />
        处理中
      </button>
    )
  }

  if (running) {
    return (
      <button
        onClick={handleClick}
        className={`inline-flex items-center gap-1.5 rounded-full bg-error/10 font-medium text-error transition hover:bg-error/20 ${sizeClass}`}
      >
        <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><rect x="1" y="1" width="8" height="8" rx="1" /></svg>
        停止
      </button>
    )
  }

  return (
    <button
      onClick={handleClick}
      className={`inline-flex items-center gap-1.5 rounded-full bg-success/10 font-medium text-success transition hover:bg-success/20 ${sizeClass}`}
    >
      <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><polygon points="2,0 10,5 2,10" /></svg>
      启动
    </button>
  )
}
