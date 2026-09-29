export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

// FastAPI wraps error text as {"detail": "..."}; surface that message directly.
async function readError(res: Response): Promise<string> {
  const raw = await res.text()
  try {
    const body = JSON.parse(raw)
    if (body && typeof body.detail === 'string') return body.detail
    if (body && Array.isArray(body.detail) && body.detail.length) {
      return body.detail.map((d: any) => d.msg).join('；')
    }
  } catch {
    /* fall through to raw text */
  }
  return raw || res.statusText
}

export async function api<T = any>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch('/api' + path, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    ...init,
  })
  if (!res.ok) throw new ApiError(await readError(res), res.status)
  if (res.status === 204) return undefined as T
  return res.json()
}
