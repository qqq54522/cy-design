import { useState, useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import Sidebar from './Sidebar'

import { useModuleByRoute } from '@/lib/bootstrap'

const PAGE_META: Record<string, { title: string; desc: string }> = {
  '/': { title: '工作台', desc: '统一管理所有创意工具与商品资产。' },
  '/projects': { title: '资产中心', desc: '汇总三个模块的项目与资产数据。' },
  '/settings': { title: '设置', desc: '平台全局配置与偏好设置。' },
}

export default function AppShell() {
  const location = useLocation()
  const [subPath, setSubPath] = useState('')
  const activeModule = useModuleByRoute(location.pathname)

  useEffect(() => {
    if (activeModule) {
      setSubPath(activeModule.default_path)
    } else {
      setSubPath('')
    }
  }, [location.pathname, activeModule])

  if (activeModule) {
    return (
      <div className="flex h-screen overflow-hidden">
        <Sidebar activeModule={activeModule} subPath={subPath} onNavigate={setSubPath} />
        <main className="min-w-0 flex-1">
          <Outlet context={{ subPath, setSubPath }} />
        </main>
      </div>
    )
  }

  const meta = PAGE_META[location.pathname] || { title: '灵桥 Creative Hub', desc: '' }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar activeModule={null} subPath="" onNavigate={() => {}} />
      <main className="min-w-0 flex-1 overflow-y-auto bg-surface">
        <div className="mx-auto max-w-[1260px] px-10 py-8">
          <header className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-[28px] font-semibold tracking-tight text-text">{meta.title}</h1>
              <p className="mt-1 text-sm text-text-secondary">{meta.desc}</p>
            </div>
            <div className="flex items-center gap-3">
              <button className="inline-flex items-center gap-2 rounded-full border border-border px-4 py-2 text-sm text-text-secondary transition hover:bg-surface-alt">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                搜索项目
              </button>
              <button className="inline-flex items-center gap-2 rounded-full bg-panel px-4 py-2 text-sm font-medium text-white transition hover:bg-panel-soft">
                + 新建任务
              </button>
            </div>
          </header>
          <Outlet context={{ subPath, setSubPath }} />
        </div>
      </main>
    </div>
  )
}
