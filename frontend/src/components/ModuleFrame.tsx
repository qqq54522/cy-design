import { useRef, useCallback, useEffect } from 'react'

import type { ModuleInfo } from '@/types/platform'

import { postToModule, onModuleMessage, type ModuleMessage } from '@/lib/bridge'

type Props = {
  module: ModuleInfo
  subPath: string
  onSubPathChange?: (path: string) => void
}

export default function ModuleFrame({ module, subPath, onSubPathChange }: Props) {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const path = subPath || module.default_path
  const url = `${module.frontend_url}${path}?embed=true`

  const handleIframeLoad = useCallback(() => {
    const iframe = iframeRef.current
    if (!iframe) return
    postToModule(iframe, {
      type: 'host:init',
      moduleKey: module.key,
      shellOrigin: window.location.origin,
      initialPath: path,
      embed: module.embed?.enabled ?? true,
    })
  }, [module.key, module.embed?.enabled, path])

  useEffect(() => {
    return onModuleMessage((msg: ModuleMessage) => {
      if (msg.type === 'module:route-change' && onSubPathChange) {
        onSubPathChange(msg.path)
      }
    })
  }, [onSubPathChange])

  return (
    <iframe
      ref={iframeRef}
      key={module.key}
      title={module.name}
      src={url}
      onLoad={handleIframeLoad}
      className="h-full w-full border-0 bg-white"
    />
  )
}
