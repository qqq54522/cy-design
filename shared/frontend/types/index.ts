/**
 * 鍏变韩绫诲瀷瀹氫箟
 */

// ============================================
// API 鍝嶅簲鏍煎紡
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
// 鍒嗛〉鐩稿叧
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
// 閫氱敤绫诲瀷
// ============================================

export type Status = 'idle' | 'loading' | 'success' | 'error'

export interface BaseEntity {
  id: string
  createdAt: string
  updatedAt: string
}
