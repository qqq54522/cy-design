/**
 * 统一 HTTP 请求客户端
 *
 * 使用方式：
 *   import { createApiClient } from '@lingqiao/shared/api'
 *   const api = createApiClient({ baseUrl: '/api' })
 *   const data = await api.get<Project[]>('/projects')
 */

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code: string = 'UNKNOWN',
    public details?: Record<string, unknown>,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export interface ApiClientOptions {
  baseUrl?: string
  timeout?: number
  defaultHeaders?: Record<string, string>
}

export interface ApiClient {
  request<T>(path: string, options?: RequestInit): Promise<T>
  get<T>(path: string, options?: RequestInit): Promise<T>
  post<T>(path: string, body?: unknown, options?: RequestInit): Promise<T>
  put<T>(path: string, body?: unknown, options?: RequestInit): Promise<T>
  del<T>(path: string, options?: RequestInit): Promise<T>
}

async function parseErrorBody(res: Response): Promise<ApiError> {
  try {
    const body = await res.json()
    const errObj = body.error || body
    return new ApiError(
      res.status,
      errObj.message || errObj.detail || '请求失败',
      errObj.code || 'UNKNOWN',
      errObj.details,
    )
  } catch {
    return new ApiError(res.status, res.statusText || '请求失败', 'NETWORK_ERROR')
  }
}

export function createApiClient(options: ApiClientOptions = {}): ApiClient {
  const { baseUrl = '', defaultHeaders = {} } = options

  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const { headers: extraHeaders, ...rest } = init ?? {}

    const mergedHeaders: Record<string, string> = {
      ...defaultHeaders,
      ...(extraHeaders as Record<string, string>),
    }
    if (!mergedHeaders['Content-Type'] && rest.body && typeof rest.body === 'string') {
      mergedHeaders['Content-Type'] = 'application/json'
    }

    const res = await fetch(`${baseUrl}${path}`, { ...rest, headers: mergedHeaders })

    if (!res.ok) {
      throw await parseErrorBody(res)
    }

    const contentType = res.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      return res.json()
    }
    return res.text() as unknown as T
  }

  function get<T>(path: string, init?: RequestInit): Promise<T> {
    return request<T>(path, { ...init, method: 'GET' })
  }

  function post<T>(path: string, body?: unknown, init?: RequestInit): Promise<T> {
    return request<T>(path, {
      ...init,
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
      headers: { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string>) },
    })
  }

  function put<T>(path: string, body?: unknown, init?: RequestInit): Promise<T> {
    return request<T>(path, {
      ...init,
      method: 'PUT',
      body: body !== undefined ? JSON.stringify(body) : undefined,
      headers: { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string>) },
    })
  }

  function del<T>(path: string, init?: RequestInit): Promise<T> {
    return request<T>(path, { ...init, method: 'DELETE' })
  }

  return { request, get, post, put, del }
}
