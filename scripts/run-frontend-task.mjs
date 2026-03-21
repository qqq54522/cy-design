import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import process from 'node:process'

const task = process.argv[2]

if (!task) {
  console.error('Usage: node scripts/run-frontend-task.mjs <task>')
  process.exit(1)
}

const repoRoot = path.resolve(import.meta.dirname, '..')
const packageDirs = [
  'frontend',
  'shared/frontend',
  'KV生成/frontend',
  '素材抓取/content-marketing/frontend',
  '表情包/frontend',
]

for (const relativeDir of packageDirs) {
  const packageDir = path.join(repoRoot, relativeDir)

  if (!existsSync(packageDir)) {
    console.warn(`Skip missing package: ${relativeDir}`)
    continue
  }

  console.log(`
==> ${relativeDir} :: ${task}`)

  const result = spawnSync('pnpm', ['run', task], {
    cwd: packageDir,
    stdio: 'inherit',
    shell: process.platform === 'win32',
  })

  if (result.error) {
    console.error(result.error)
    process.exit(1)
  }

  if (result.status !== 0) {
    process.exit(result.status ?? 1)
  }
}
