/**
 * 共享类型定义
 */

// ============================================
// API 响应格式
// ============================================

export interface ApiResponse<T> {
  data: T
  error?: ApiErrorInfo
}

export interface ApiErrorInfo {
  code: string
  message: string
  details?: Record<string, unknown>
}

// ============================================
// 分页相关
// ============================================

export interface PaginationParams {
  page: number
  pageSize: number
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
}

// ============================================
// 通用类型
// ============================================

export type Status = 'idle' | 'loading' | 'success' | 'error'

export interface BaseEntity {
  id: string
  createdAt: string
  updatedAt: string
}
