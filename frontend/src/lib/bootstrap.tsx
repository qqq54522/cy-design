/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

import { fetchSettings } from './api'

import type { ModuleInfo } from '@/types/platform'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface BootstrapData {
  modules: ModuleInfo[]
  loading: boolean
  error: string | null
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const BootstrapContext = createContext<BootstrapData>({
  modules: [],
  loading: true,
  error: null,
})

// ---------------------------------------------------------------------------
// Provider — wrap this around <App /> in main.tsx
// ---------------------------------------------------------------------------

export function BootstrapProvider({ children }: { children: ReactNode }) {
  const [modules, setModules] = useState<ModuleInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    fetchSettings()
      .then((data) => {
        if (!cancelled) {
          setModules(data.modules)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : '加载平台配置失败')
          setLoading(false)
        }
      })
    return () => { cancelled = true }
  }, [])

  return (
    <BootstrapContext.Provider value={{ modules, loading, error }}>
      {children}
    </BootstrapContext.Provider>
  )
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

export function useBootstrap(): BootstrapData {
  return useContext(BootstrapContext)
}

export function useModuleByRoute(pathname: string): ModuleInfo | null {
  const { modules } = useBootstrap()
  return modules.find((m) => m.route === pathname) ?? null
}

export function useModuleByKey(key: string): ModuleInfo | null {
  const { modules } = useBootstrap()
  return modules.find((m) => m.key === key) ?? null
}
