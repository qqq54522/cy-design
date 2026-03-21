/**
 * Shared package entry.
 */

export { createApiClient, ApiError } from './api/index'
export type { ApiClient, ApiClientOptions } from './api/index'

export {
  ConfirmDialog,
  ModuleLayout,
  ModuleSidebar,
  PlatformBridge,
  Spinner,
} from './components/index'

export { useDebounce, useLocalStorage } from './hooks/index'

export * from './utils/index'

export type {
  ApiErrorInfo,
  ApiResponse,
  BaseEntity,
  PaginatedResponse,
  PaginationParams,
  Status,
} from './types/index'

export { API_CONFIG, DEFAULT_PAGE_SIZE, POLL_INTERVAL, ROUTES } from './constants/index'
