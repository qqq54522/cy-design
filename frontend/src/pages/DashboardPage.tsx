import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'

import type { DashboardSummary, ModuleInfo, ServiceStatus } from '@/types/platform'

import ServiceControlButton from '@/components/ServiceControlButton'
import StatusPill from '@/components/StatusPill'
import {
  fetchModules,
  fetchServiceStatus,
  fetchSummary,
  startAllServices,
  startModule,
  stopAllServices,
  stopModule,
} from '@/lib/api'

const POLL_INTERVAL = 5000

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [modules, setModules] = useState<ModuleInfo[]>([])
  const [services, setServices] = useState<ServiceStatus[]>([])
  const [error, setError] = useState<string | null>(null)
  const [globalLoading, setGlobalLoading] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval>>()

  const refresh = useCallback(async () => {
    try {
      const [summaryData, modulesData, servicesData] = await Promise.all([
        fetchSummary(),
        fetchModules(),
        fetchServiceStatus(),
      ])
      setSummary(summaryData)
      setModules(modulesData)
      setServices(servicesData)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : '平台服务未启动')
    }
  }, [])

  useEffect(() => {
    refresh()
    pollRef.current = setInterval(refresh, POLL_INTERVAL)
    return () => clearInterval(pollRef.current)
  }, [refresh])

  const svcMap = Object.fromEntries(services.map((s) => [s.key, s]))
  const anyRunning = services.some((s) => s.backend_running || s.frontend_running)

  const handleStartAll = async () => {
    setGlobalLoading(true)
    try {
      await startAllServices()
      await refresh()
    } finally {
      setGlobalLoading(false)
    }
  }

  const handleStopAll = async () => {
    setGlobalLoading(true)
    try {
      await stopAllServices()
      await refresh()
    } finally {
      setGlobalLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Toolbar */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleStartAll}
          disabled={globalLoading}
          className="inline-flex items-center gap-2 rounded-full bg-panel px-5 py-2.5 text-sm font-medium text-white transition hover:bg-panel-soft disabled:opacity-50"
        >
          {globalLoading ? (
            <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
          ) : (
            <svg width="12" height="12" viewBox="0 0 10 10" fill="currentColor"><polygon points="1,0 10,5 1,10" /></svg>
          )}
          一键启动全部
        </button>
        {anyRunning && (
          <button
            onClick={handleStopAll}
            disabled={globalLoading}
            className="inline-flex items-center gap-2 rounded-full border border-error/30 bg-error/5 px-5 py-2.5 text-sm font-medium text-error transition hover:bg-error/10 disabled:opacity-50"
          >
            <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><rect x="1" y="1" width="8" height="8" rx="1" /></svg>
            全部停止
          </button>
        )}
      </div>

      {/* Hero + Quick Launch */}
      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.7fr)_340px]">
        <div className="rounded-[24px] border border-border bg-surface p-5 shadow-sm">
          <div className="rounded-[18px] bg-gradient-to-r from-[#020617] to-[#1d4ed8] p-5 text-white">
            <p className="text-[11px] uppercase tracking-[0.2em] text-white/65">Creative Platform</p>
            <h2 className="mt-3 text-[28px] font-semibold">一站式创意生产平台</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-white/75">
              先把三个成熟项目纳入一个统一入口中，再通过平台项目中心、服务编排和配置中心逐步抽公共能力。
            </p>
            <div className="mt-5 flex gap-3">
              <Link className="rounded-full bg-white px-4 py-2 text-sm font-medium text-panel no-underline" to="/projects">
                打开项目中心
              </Link>
              <Link className="rounded-full bg-white/10 px-4 py-2 text-sm font-medium text-white no-underline" to="/settings">
                平台设置
              </Link>
            </div>
          </div>
        </div>

        <div className="rounded-[24px] border border-border bg-surface p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold text-text">快速启动</p>
              <p className="mt-1 text-sm text-text-secondary">管理各模块的前后端服务。</p>
            </div>
          </div>
          <div className="mt-4 space-y-3">
            {modules.map((module) => {
              const svc = svcMap[module.key]
              const running = svc ? svc.backend_running || svc.frontend_running : false
              return (
                <div key={module.key} className="flex items-center justify-between rounded-2xl border border-border px-4 py-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-text">{module.name}</p>
                      <StatusPill status={module.status} />
                    </div>
                    {svc && (
                      <p className="mt-0.5 text-[11px] text-text-tertiary">
                        后端{svc.backend_running ? ' ✓' : ' ✗'}
                        {' · '}
                        前端{svc.frontend_running ? ' ✓' : ' ✗'}
                      </p>
                    )}
                  </div>
                  <ServiceControlButton
                    running={running}
                    onStart={() => startModule(module.key).then(refresh)}
                    onStop={() => stopModule(module.key).then(refresh)}
                  />
                </div>
              )
            })}
            {modules.length === 0 && <p className="text-sm text-text-secondary">正在读取模块状态...</p>}
          </div>
        </div>
      </section>

      {error && (
        <section className="rounded-2xl border border-error/20 bg-error/5 px-5 py-4 text-sm text-error">
          平台 API 尚未启动：{error}
        </section>
      )}

      {/* Stats */}
      <section className="grid gap-4 md:grid-cols-4">
        <StatCard label="总项目数" value={summary?.total_projects ?? 0} />
        <StatCard label="在线服务" value={summary?.running_services ?? 0} />
        <StatCard label="内容项目" value={summary?.module_counts.content ?? 0} />
        <StatCard label="KV 项目" value={summary?.module_counts.kv ?? 0} />
      </section>

      {/* Module Cards — 整卡点击跳转，控制功能留给快速启动区 */}
      <section className="grid gap-4 xl:grid-cols-3">
        {modules.map((module) => (
          <Link
            key={module.key}
            to={module.route}
            className="rounded-[22px] bg-panel px-5 py-5 text-white no-underline shadow-sm transition hover:-translate-y-0.5"
          >
            <div className="flex items-center justify-between">
              <p className="text-lg font-semibold">{module.name}</p>
              <StatusPill status={module.status} />
            </div>
            <p className="mt-3 text-sm leading-6 text-white/72">{module.description}</p>
          </Link>
        ))}
      </section>

      {/* Recent Projects */}
      <section className="rounded-[24px] border border-border bg-surface p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-lg font-semibold text-text">最近项目</p>
            <p className="mt-1 text-sm text-text-secondary">这里已经开始按统一索引汇总三个模块的历史数据。</p>
          </div>
          <Link to="/projects" className="text-sm text-primary no-underline">
            查看全部
          </Link>
        </div>
        <div className="space-y-3">
          {summary?.recent_projects.map((project) => (
            <a
              key={`${project.module}-${project.id}`}
              href={project.detail_url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-between rounded-2xl border border-border px-4 py-3 text-text no-underline"
            >
              <div>
                <p className="text-sm font-medium">{project.title}</p>
                <p className="mt-1 text-xs text-text-secondary">
                  {project.module_name}
                  {project.subtitle ? ` · ${project.subtitle}` : ''}
                </p>
              </div>
              <span className="text-xs text-text-secondary">{project.status}</span>
            </a>
          ))}
          {!summary?.recent_projects.length && <p className="text-sm text-text-secondary">暂无项目记录。</p>}
        </div>
      </section>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-border bg-surface px-5 py-4 shadow-sm">
      <p className="text-xs uppercase tracking-[0.18em] text-text-tertiary">{label}</p>
      <p className="mt-2 text-[30px] font-semibold text-text">{value}</p>
    </div>
  )
}
