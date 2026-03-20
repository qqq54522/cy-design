type StatusPillProps = {
  status: string
}

const STATUS_CLASS: Record<string, string> = {
  online: 'bg-success/10 text-success',
  offline: 'bg-error/10 text-error',
  degraded: 'bg-warning/10 text-warning',
  unknown: 'bg-text-tertiary/15 text-text-secondary',
}

export default function StatusPill({ status }: StatusPillProps) {
  const normalized = status.toLowerCase()
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_CLASS[normalized] || STATUS_CLASS.unknown}`}
    >
      {status}
    </span>
  )
}
