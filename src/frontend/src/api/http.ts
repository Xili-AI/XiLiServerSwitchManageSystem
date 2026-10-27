import axios, { type AxiosError, type AxiosRequestConfig } from 'axios'
import type { ApiEnvelope } from '@/types'
import { clearSessionStorage, getToken } from '@/utils/storage'

export class ApiError extends Error {
  code: number
  status: number

  constructor(message: string, code = 0, status = 0) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

const http = axios.create({
  baseURL: '/api',
  timeout: 25000,
  headers: { Accept: 'application/json' },
})

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiEnvelope<unknown>>) => {
    const status = error.response?.status || 0
    const isLoginRequest = String(error.config?.url || '').includes('/auth/login')
    if (status === 401 && !isLoginRequest) {
      clearSessionStorage()
      if (!window.location.pathname.startsWith('/login')) {
        const redirect = encodeURIComponent(window.location.pathname + window.location.search)
        window.location.assign(`/login?redirect=${redirect}`)
      }
    }
    return Promise.reject(toApiError(error))
  },
)

function toApiError(error: AxiosError<ApiEnvelope<unknown>>): ApiError {
  const status = error.response?.status || 0
  const payload = error.response?.data
  const message =
    payload?.message ||
    (status ? `请求失败（HTTP ${status}）` : '无法连接到后端服务，请确认服务已启动')
  return new ApiError(message, payload?.code || status, status)
}

export async function request<T>(config: AxiosRequestConfig): Promise<T> {
  const response = await http.request<ApiEnvelope<T>>(config)
  const envelope = response.data
  if (!envelope) return undefined as T
  if (envelope.code !== 200 && envelope.code !== 201) {
    throw new ApiError(envelope.message || '业务处理失败', envelope.code, response.status)
  }
  return envelope.data as T
}

export default http
