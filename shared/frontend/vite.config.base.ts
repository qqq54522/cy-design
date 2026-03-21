/**
 * Shared Vite config factory.
 */
import { resolve } from 'path'

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, type UserConfig } from 'vite'

export interface ViteConfigOptions {
  port: number
  proxyTarget: string
  sharedPath: string
  extraProxyRoutes?: Record<string, string>
  enableTest?: boolean
  extraConfig?: Partial<UserConfig>
}

export function createViteConfig(options: ViteConfigOptions) {
  const {
    port,
    proxyTarget,
    sharedPath,
    extraProxyRoutes = {},
    enableTest = true,
    extraConfig = {},
  } = options
  const apiTarget = process.env.API_TARGET || proxyTarget

  const proxyEntries: Record<string, object> = {
    '/api': { target: apiTarget, changeOrigin: true, ws: true },
  }

  for (const [route, target] of Object.entries(extraProxyRoutes)) {
    proxyEntries[route] = { target: target || apiTarget, changeOrigin: true }
  }

  return defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': resolve(process.cwd(), 'src'),
        '@shared': resolve(process.cwd(), sharedPath),
        '@lingqiao/shared': resolve(process.cwd(), sharedPath),
      },
    },
    server: {
      port,
      proxy: proxyEntries,
    },
    ...(enableTest
      ? {
          test: {
            globals: true,
            environment: 'jsdom',
            setupFiles: ['./src/test/setup.ts'],
            include: ['src/**/*.{test,spec}.{ts,tsx}'],
          },
        }
      : {}),
    ...extraConfig,
  })
}
