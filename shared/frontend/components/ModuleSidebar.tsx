/**
 * 统一模块 Sidebar 骨架组件
 *
 * 提供响应式侧边栏外壳（fixed 定位 + mobile overlay + translate 动画）。
 * 各模块通过 children 传入具体的导航内容。
 *
 * 使用方式：
 *   <ModuleSidebar mobileOpen={mobileOpen} onClose={onClose}>
 *     <NavItems />
 *     <RecentProjects />
 *   </ModuleSidebar>
 */
import type { ReactNode } from 'react'

export interface ModuleSidebarProps {
  mobileOpen: boolean
  onClose: () => void
  children: ReactNode
}

export default function ModuleSidebar({ mobileOpen, onClose, children }: ModuleSidebarProps) {
  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 bg-black/20 z-30 lg:hidden" onClick={onClose} />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-60 bg-surface border-r border-border flex flex-col transition-transform duration-200 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {children}
      </aside>
    </>
  )
}
