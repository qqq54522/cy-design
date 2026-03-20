import { Link, Navigate, Route, Routes } from 'react-router-dom'

import AppShell from '@/components/AppShell'
import DashboardPage from '@/pages/DashboardPage'
import ModulePage from '@/pages/ModulePage'
import ProjectsPage from '@/pages/ProjectsPage'
import SettingsPage from '@/pages/SettingsPage'

function NotFound() {
  return (
    <div className="flex min-h-[420px] flex-col items-center justify-center gap-3 rounded-[24px] border border-border bg-surface-alt">
      <p className="text-3xl">404</p>
      <p className="text-sm text-text-secondary">页面不存在，返回工作台继续操作。</p>
      <Link to="/" className="rounded-full bg-panel px-4 py-2 text-sm font-medium text-white no-underline">
        回到工作台
      </Link>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/content" element={<ModulePage />} />
        <Route path="/kv" element={<ModulePage />} />
        <Route path="/emoji" element={<ModulePage />} />
        <Route path="/dashboard" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
