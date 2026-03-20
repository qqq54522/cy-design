import pathlib

content = """import type { DashboardSummary, ModuleInfo, ProjectIndexItem, RecentLogsPayload, ServiceStatus, SettingsPayload } from '@/types/platform'
import { ApiError } from '@lingqiao/shared/api'

export { ApiError }

type ApiErrorPayload = {
  detail?: string
  code?: string
  error?: {
    message?: string
    code?: string
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init)
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as ApiErrorPayload
    const message = payload.error?.message || payload.detail || '\u8bf7\u6c42\u5931\u8d25'
    const code = payload.error?.code || payload.code || 'UNKNOWN'
    throw new ApiError(response.status, message, code)
  }
  return response.json() as Promise<T>
}

export async function fetchModules(): Promise<ModuleInfo[]> {
  const response = await request<{ data: ModuleInfo[] }>('/api/platform/modules')
  return response.data
}

export async function fetchProjects(): Promise<ProjectIndexItem[]> {
  const response = await request<{ data: { projects: ProjectIndexItem[] } }>('/api/platform/projects')
  return response.data.projects
}

export async function fetchSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>('/api/platform/summary')
}

export async function fetchSettings(): Promise<SettingsPayload> {
  return request<SettingsPayload>('/api/platform/settings')
}

export async function fetchRecentLogs(): Promise<RecentLogsPayload> {
  const response = await request<{ data: RecentLogsPayload }>('/api/platform/logs/recent')
  return response.data
}

export async function fetchServiceStatus(): Promise<ServiceStatus[]> {
  return request<ServiceStatus[]>('/api/platform/services/status')
}

export async function startAllServices(): Promise<void> {
  await request('/api/platform/services/start-all', { method: 'POST' })
}

export async function stopAllServices(): Promise<void> {
  await request('/api/platform/services/stop-all', { method: 'POST' })
}

export async function startModule(key: string): Promise<void> {
  await request(`/api/platform/services/${key}/start`, { method: 'POST' })
}

export async function stopModule(key: string): Promise<void> {
  await request(`/api/platform/services/${key}/stop`, { method: 'POST' })
}
"""

pathlib.Path("frontend/src/lib/api.ts").write_text(content, encoding="utf-8")
print("File written successfully")
