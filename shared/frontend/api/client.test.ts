import { afterEach, describe, expect, it, vi } from 'vitest'

import { createApiClient } from './client'

function createJsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
}

describe('createApiClient', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  it('returns parsed JSON for successful requests', async () => {
    const fetchMock = vi.fn().mockResolvedValue(createJsonResponse({ items: [1, 2, 3] }))
    vi.stubGlobal('fetch', fetchMock)

    const client = createApiClient({ baseUrl: '/api' })

    await expect(client.get<{ items: number[] }>('/projects')).resolves.toEqual({
      items: [1, 2, 3],
    })
    expect(fetchMock).toHaveBeenCalledWith('/api/projects', { headers: {}, method: 'GET' })
  })

  it('normalizes structured error payloads into ApiError', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      createJsonResponse(
        {
          error: {
            code: 'PROJECT_NOT_FOUND',
            message: 'Project not found',
            details: { projectId: 'p_123' },
          },
        },
        { status: 404, statusText: 'Not Found' },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const client = createApiClient({ baseUrl: '/api' })

    await expect(client.get('/projects/p_123')).rejects.toMatchObject({
      name: 'ApiError',
      status: 404,
      code: 'PROJECT_NOT_FOUND',
      message: 'Project not found',
      details: { projectId: 'p_123' },
    })
  })
})
