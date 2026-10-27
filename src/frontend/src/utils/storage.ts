import type { User } from '@/types'

const TOKEN_KEY = 'xili_serverswitchmanagesystem_token'
const USER_KEY = 'xili_serverswitchmanagesystem_user'
const SIDEBAR_KEY = 'xili_serverswitchmanagesystem_sidebar_collapsed'
const VIEW_KEY = 'xili_serverswitchmanagesystem_service_view'

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token: string): void {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

export function setStoredUser(user: User | null): void {
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
  else localStorage.removeItem(USER_KEY)
}

export function clearSessionStorage(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getSidebarCollapsed(): boolean {
  return localStorage.getItem(SIDEBAR_KEY) === '1'
}

export function setSidebarCollapsed(value: boolean): void {
  localStorage.setItem(SIDEBAR_KEY, value ? '1' : '0')
}

export function getServiceView(): 'grid' | 'table' {
  return localStorage.getItem(VIEW_KEY) === 'table' ? 'table' : 'grid'
}

export function setServiceView(value: 'grid' | 'table'): void {
  localStorage.setItem(VIEW_KEY, value)
}
