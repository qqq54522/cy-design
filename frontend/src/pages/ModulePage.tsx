import { useLocation, useOutletContext } from 'react-router-dom'

import ModuleFrame from '@/components/ModuleFrame'
import { useModuleByRoute } from '@/lib/bootstrap'

export default function ModulePage() {
  const location = useLocation()
  const { subPath, setSubPath } = useOutletContext<{ subPath: string; setSubPath: (p: string) => void }>()
  const mod = useModuleByRoute(location.pathname)

  if (!mod) {
    return (
      <div className="flex h-full items-center justify-center text-text-secondary">
        模块未找到
      </div>
    )
  }

  return <ModuleFrame module={mod} subPath={subPath} onSubPathChange={setSubPath} />
}
