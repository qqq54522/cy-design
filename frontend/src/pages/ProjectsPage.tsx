import { useEffect, useMemo, useState } from 'react'

import type { ProjectIndexItem } from '@/types/platform'

import { fetchProjects } from '@/lib/api'

const FILTERS = [
  { key: 'all', label: '全部' },
  { key: 'content', label: '内容营销' },
  { key: 'kv', label: 'KV 生成' },
  { key: 'emoji', label: '表情包' },
] as const

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectIndexItem[]>([])
  const [filter, setFilter] = useState<(typeof FILTERS)[number]['key']>('all')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchProjects()
      .then(setProjects)
      .catch((err) => setError(err instanceof Error ? err.message : '读取失败'))
  }, [])

  const filteredProjects = useMemo(() => {
    if (filter === 'all') return projects
    return projects.filter((project) => project.module === filter)
  }, [filter, projects])

  return (
    <div className="space-y-5">
      <section className="flex flex-wrap gap-2">
        {FILTERS.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setFilter(item.key)}
            className={`rounded-full px-4 py-2 text-sm transition ${
              filter === item.key ? 'bg-panel text-white' : 'bg-surface-alt text-text-secondary'
            }`}
          >
            {item.label}
          </button>
        ))}
      </section>

      {error && (
        <section className="rounded-2xl border border-error/20 bg-error/5 px-5 py-4 text-sm text-error">
          {error}
        </section>
      )}

      <section className="overflow-hidden rounded-[24px] border border-border">
        <div className="grid grid-cols-[1.6fr_0.9fr_0.8fr_0.8fr] bg-surface-alt px-5 py-3 text-xs uppercase tracking-[0.18em] text-text-tertiary">
          <span>项目</span>
          <span>模块</span>
          <span>状态</span>
          <span>动作</span>
        </div>
        <div className="divide-y divide-border bg-surface">
          {filteredProjects.map((project) => (
            <div key={`${project.module}-${project.id}`} className="grid grid-cols-[1.6fr_0.9fr_0.8fr_0.8fr] px-5 py-4">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-text">{project.title}</p>
                <p className="mt-1 truncate text-xs text-text-secondary">
                  {project.subtitle || project.source_path}
                </p>
              </div>
              <div className="text-sm text-text-secondary">{project.module_name}</div>
              <div className="text-sm text-text-secondary">{project.status}</div>
              <div>
                <a
                  href={project.detail_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm font-medium text-primary no-underline"
                >
                  打开
                </a>
              </div>
            </div>
          ))}
          {filteredProjects.length === 0 && (
            <div className="px-5 py-12 text-center text-sm text-text-secondary">还没有可以汇总的平台项目。</div>
          )}
        </div>
      </section>
    </div>
  )
}
