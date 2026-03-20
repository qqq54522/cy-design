// ---------------------------------------------------------------------------
// Host ↔ Module postMessage bridge protocol
// ---------------------------------------------------------------------------

// Host -> Module
export type HostInitMessage = {
  type: 'host:init'
  moduleKey: string
  shellOrigin: string
  initialPath: string
  embed: boolean
}

export type HostNavigateMessage = {
  type: 'host:navigate'
  path: string
}

export type HostPingMessage = {
  type: 'host:ping'
}

export type HostMessage = HostInitMessage | HostNavigateMessage | HostPingMessage

// Module -> Host
export type ModuleReadyMessage = {
  type: 'module:ready'
}

export type ModuleRouteChangeMessage = {
  type: 'module:route-change'
  path: string
  title?: string
  canGoBack?: boolean
}

export type ModuleTitleChangeMessage = {
  type: 'module:title-change'
  title: string
}

export type ModuleMessage = ModuleReadyMessage | ModuleRouteChangeMessage | ModuleTitleChangeMessage

// All bridge messages
export type BridgeMessage = HostMessage | ModuleMessage

function isBridgeMessage(data: unknown): data is BridgeMessage {
  return (
    typeof data === 'object' &&
    data !== null &&
    'type' in data &&
    typeof (data as { type: unknown }).type === 'string' &&
    ((data as { type: string }).type.startsWith('host:') ||
      (data as { type: string }).type.startsWith('module:'))
  )
}

export function postToModule(iframe: HTMLIFrameElement, msg: HostMessage) {
  iframe.contentWindow?.postMessage(msg, '*')
}

export function onModuleMessage(
  callback: (msg: ModuleMessage, origin: string) => void,
): () => void {
  const handler = (event: MessageEvent) => {
    if (isBridgeMessage(event.data) && event.data.type.startsWith('module:')) {
      callback(event.data as ModuleMessage, event.origin)
    }
  }
  window.addEventListener('message', handler)
  return () => window.removeEventListener('message', handler)
}
