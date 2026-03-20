/**
 * 共享常量定义
 */

// ============================================
// API 配置
// ============================================

export const API_CONFIG = {
  platform: {
    baseUrl: import.meta.env.VITE_PLATFORM_API_BASE || 'http://localhost:8100',
  },
  modules: {
    content: {
      baseUrl: import.meta.env.VITE_CONTENT_API_BASE || 'http://localhost:8001',
    },
    kv: {
      baseUrl: import.meta.env.VITE_KV_API_BASE || 'http://localhost:8002',
    },
    emoji: {
      baseUrl: import.meta.env.VITE_EMOJI_API_BASE || 'http://localhost:8003',
    },
  },
} as const

// ============================================
// 路由常量
// ============================================

export const ROUTES = {
  hub: {
    home: '/',
    projects: '/projects',
    settings: '/settings',
  },
  modules: {
    content: '/content',
    kv: '/kv',
    emoji: '/emoji',
  },
} as const

// ============================================
// 其他常量
// ============================================

export const POLL_INTERVAL = 5000 // 轮询间隔（毫秒）

export const DEFAULT_PAGE_SIZE = 20
