import { useEffect, useState } from 'react'

import type { RecentLogsPayload, SettingsPayload } from '@/types/platform'

import StatusPill from '@/components/StatusPill'
import { fetchRecentLogs, fetchSettings } from '@/lib/api'

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsPayload | null>(null)
  const [logs, setLogs] = useState<RecentLogsPayload | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([fetchSettings(), fetchRecentLogs()])
      .then(([settingsPayload, logsPayload]) => {
        setSettings(settingsPayload)
        setLogs(logsPayload)
      })
      .catch((err) => setError(err instanceof Error ? err.message : '读取失败'))
  }, [])

  return (
    <div className="space-y-6">
      {error && (
        <section className="rounded-2xl border border-error/20 bg-error/5 px-5 py-4 text-sm text-error">
          {error}
        </section>
      )}

      <section className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-[24px] border border-border bg-surface-alt p-5">
          <p className="text-lg font-semibold text-text">运行入口</p>
          <div className="mt-4 space-y-3 text-sm">
            <SettingRow label="平台壳层" value={settings?.shell_url || 'http://localhost:5180'} />
            <SettingRow label="平台 API" value={settings?.platform_api_url || 'http://localhost:8100'} />
          </div>
        </div>

        <div className="rounded-[24px] border border-border bg-surface-alt p-5">
          <p className="text-lg font-semibold text-text">地基规则</p>
          <ul className="mt-4 space-y-3 text-sm leading-6 text-text-secondary">
            <li>统一入口固定为 `5180`，避免与业务前端相互冲突。</li>
            <li>内容营销保留 `8001/5174`，KV 调整为 `8002/5175`，表情包调整为 `8003/5176`。</li>
            <li>统一项目中心通过平台索引层汇总，不直接破坏原有数据结构。</li>
          </ul>
        </div>
      </section>

      <section className="rounded-[24px] border border-border bg-surface p-5">
        <p className="text-lg font-semibold text-text">模块配置中心</p>
        <div className="mt-4 space-y-3">
          {settings?.modules.map((module) => (
            <div key={module.key} className="rounded-2xl border border-border px-4 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-text">{module.name}</p>
                  <p className="mt-1 text-xs text-text-secondary">{module.description}</p>
                </div>
                <StatusPill status={module.status} />
              </div>
              <div className="mt-3 grid gap-2 text-xs text-text-secondary">
                <div>前端地址：{module.frontend_url}</div>
                <div>后端地址：{module.backend_url}</div>
                <div>健康检查：{module.health_url}</div>
                <div>数据目录：{module.data_dirs.join(' / ')}</div>
                <div>保留天数：{module.retention_days ?? '未配置'}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-[24px] border border-border bg-surface p-5">
        <p className="text-lg font-semibold text-text">平台日志</p>
        <div className="mt-4 overflow-hidden rounded-2xl bg-panel px-4 py-4 text-xs leading-6 text-white/80">
          {logs?.lines.length ? (
            logs.lines.map((line) => <div key={line}>{line}</div>)
          ) : (
            <div>日志文件还没有内容，启动平台后这里会显示最近 100 条请求记录。</div>
          )}
        </div>
      </section>
    </div>
  )
}

function SettingRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3">
      <span className="text-text-secondary">{label}</span>
      <span className="font-medium text-text">{value}</span>
    </div>
  )
}
