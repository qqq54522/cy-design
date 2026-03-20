import { NavLink, useNavigate } from 'react-router-dom'

import type { ModuleInfo } from '@/types/platform'

import { useBootstrap } from '@/lib/bootstrap'

const STATIC_NAV = [{ to: '/', label: '工作台', end: true }]

const BOTTOM_NAV = [
  { to: '/projects', label: '资产中心' },
  { to: '/settings', label: '设置' },
]

type SidebarProps = {
  activeModule: ModuleInfo | null
  subPath: string
  onNavigate: (path: string) => void
}

export default function Sidebar({ activeModule, subPath, onNavigate }: SidebarProps) {
  const navigate = useNavigate()
  const { modules } = useBootstrap()

  if (activeModule) {
    const currentPath = subPath || activeModule.default_path
    return (
      <aside className="flex h-full w-[220px] shrink-0 flex-col bg-panel px-4 py-6 text-white">
        <button
          onClick={() => navigate('/')}
          className="mb-4 flex items-center gap-2 px-3 text-sm text-white/50 transition hover:text-white"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          返回
        </button>

        <div className="mb-6 px-3">
          <p className="text-lg font-semibold tracking-tight">{activeModule.name}</p>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto">
          {activeModule.nav.map((item) => (
            <button
              key={item.path}
              onClick={() => onNavigate(item.path)}
              className={`block w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                currentPath === item.path
                  ? 'bg-white/10 font-medium text-white'
                  : 'text-white/60 hover:bg-white/6 hover:text-white'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
    )
  }

  return (
    <aside className="flex h-full w-[220px] shrink-0 flex-col bg-panel px-4 py-6 text-white">
      <div className="mb-6 px-3">
        <p className="text-lg font-semibold tracking-tight">Creative Hub</p>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto">
        {STATIC_NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm transition ${
                isActive ? 'bg-white/10 font-medium text-white' : 'text-white/60 hover:bg-white/6 hover:text-white'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}

        {modules.map((m) => (
          <NavLink
            key={m.route}
            to={m.route}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm transition ${
                isActive ? 'bg-white/10 font-medium text-white' : 'text-white/60 hover:bg-white/6 hover:text-white'
              }`
            }
          >
            {m.name}
          </NavLink>
        ))}

        <div className="my-4 border-t border-white/10" />

        {BOTTOM_NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm transition ${
                isActive ? 'bg-white/10 font-medium text-white' : 'text-white/60 hover:bg-white/6 hover:text-white'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-4 rounded-2xl bg-white/10 px-4 py-4">
        <p className="text-sm font-semibold">编作专业版</p>
        <p className="mt-1.5 text-xs leading-5 text-white/55">AI 全套下载工程成本，开始打造你的创作产线。</p>
        <button className="mt-3 w-full rounded-full bg-white px-4 py-2 text-xs font-medium text-panel transition hover:bg-white/90">
          立即升级
        </button>
      </div>
    </aside>
  )
}
