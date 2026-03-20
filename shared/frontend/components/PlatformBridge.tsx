import { useEffect, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

type HostInitMessage = {
  type: 'host:init'
  moduleKey: string
  shellOrigin: string
  initialPath: string
  embed: boolean
}

type HostNavigateMessage = {
  type: 'host:navigate'
  path: string
}

type HostMessage = HostInitMessage | HostNavigateMessage | { type: 'host:ping' }

function isHostMessage(data: unknown): data is HostMessage {
  return (
    typeof data === 'object' &&
    data !== null &&
    'type' in data &&
    typeof (data as { type: unknown }).type === 'string' &&
    (data as { type: string }).type.startsWith('host:')
  )
}

export default function PlatformBridge() {
  const location = useLocation()
  const navigate = useNavigate()
  const shellOrigin = useRef<string | null>(null)

  useEffect(() => {
    const handler = (event: MessageEvent) => {
      if (!isHostMessage(event.data)) return

      const msg = event.data

      if (msg.type === 'host:init') {
        shellOrigin.current = msg.shellOrigin
        window.parent.postMessage({ type: 'module:ready' }, msg.shellOrigin)
      }

      if (msg.type === 'host:navigate') {
        navigate(msg.path)
      }

      if (msg.type === 'host:ping') {
        const origin = shellOrigin.current
        if (origin) {
          window.parent.postMessage({ type: 'module:ready' }, origin)
        }
      }
    }

    window.addEventListener('message', handler)
    return () => window.removeEventListener('message', handler)
  }, [navigate])

  useEffect(() => {
    if (window.parent === window) return
    const origin = shellOrigin.current
    if (!origin) return

    window.parent.postMessage(
      {
        type: 'module:route-change',
        path: location.pathname,
        title: document.title,
        canGoBack: location.key !== 'default',
      },
      origin,
    )
  }, [location.pathname, location.key])

  return null
}
