export interface ModuleNavItem {
  path: string
  label: string
}

export interface ModuleFrontendInfo {
  port: number
  origin: string
  cwd: string
  start_command: string
}

export interface ModuleBackendInfo {
  port: number
  origin: string
  cwd: string
  health_path: string
  start_command: string
  uvicorn_module: string
}

export interface ModuleEmbedInfo {
  enabled: boolean
}

export interface ModuleInfo {
  key: 'content' | 'kv' | 'emoji' | string
  name: string
  description: string
  route: string
  default_path: string
  nav: ModuleNavItem[]
  frontend_url: string
  backend_url: string
  health_url: string
  status: 'online' | 'offline' | 'degraded' | 'unknown'
  frontend?: ModuleFrontendInfo | null
  backend?: ModuleBackendInfo | null
  embed?: ModuleEmbedInfo | null
  data_dirs: string[]
  retention_days?: number | null
}

export interface ProjectIndexItem {
  id: string
  module: string
  module_name: string
  title: string
  subtitle?: string | null
  status: string
  created_at?: string | null
  updated_at?: string | null
  detail_url: string
  source_path: string
  metrics: Record<string, number>
}

export interface DashboardSummary {
  total_projects: number
  module_counts: Record<string, number>
  running_services: number
  recent_projects: ProjectIndexItem[]
}

export interface SettingsPayload {
  shell_url: string
  platform_api_url: string
  modules: ModuleInfo[]
}

export interface RecentLogsPayload {
  lines: string[]
}

export interface ServiceStatus {
  key: string
  backend_running: boolean
  frontend_running: boolean
  backend_pid: number | null
  frontend_pid: number | null
}
