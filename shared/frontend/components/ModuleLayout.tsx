/**
 * 统一模块 Layout 组件
 *
 * 提供 embed 模式检测、侧边栏 + 主内容区布局、移动端响应式 header。
 * 各模块通过 props 传入 sidebar 和可选的全局覆盖层组件。
 *
 * 使用方式：
 *   <ModuleLayout
 *     title="HotContent"
 *     sidebar={<Sidebar mobileOpen={mobileOpen} onClose={closeMobile} />}
 *     overlay={<ToastContainer />}
 *   />
 */
import { useState, type ReactNode } from 'react'
import { Outlet } from 'react-router-dom'

const isEmbed = new URLSearchParams(window.location.search).get('embed') === 'true'

export interface ModuleLayoutProps {
  title?: string
  sidebar: (props: { mobileOpen: boolean; onClose: () => void }) => ReactNode
  overlay?: ReactNode
}

export default function ModuleLayout({ title, sidebar, overlay }: ModuleLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false)

  if (isEmbed) {
    return (
      <div className="h-screen overflow-y-auto bg-surface">
        <Outlet />
        {overlay}
      </div>
    )
  }

  return (
    <div className="h-screen flex overflow-hidden bg-surface">
      {sidebar({ mobileOpen, onClose: () => setMobileOpen(false) })}

      <div className="flex-1 flex flex-col min-w-0 lg:ml-60">
        <header className="lg:hidden h-12 border-b border-border flex items-center px-4 shrink-0 bg-surface">
          <button
            onClick={() => setMobileOpen(true)}
            className="w-7 h-7 flex flex-col items-center justify-center gap-[5px]"
            aria-label="菜单"
          >
            <span className="block w-4 h-[1.5px] bg-text-secondary rounded-full" />
            <span className="block w-4 h-[1.5px] bg-text-secondary rounded-full" />
            <span className="block w-4 h-[1.5px] bg-text-secondary rounded-full" />
          </button>
          {title && <span className="text-sm font-medium ml-3 text-text">{title}</span>}
        </header>

        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>

      {overlay}
    </div>
  )
}
