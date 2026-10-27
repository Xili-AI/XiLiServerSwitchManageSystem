export type ServiceMode = 'auto' | 'subdomain' | 'path' | 'origin'
export type ViewMode = 'grid' | 'table'

export interface Service {
  id: string
  name: string
  slug: string
  target_url: string
  entry_path: string
  strip_prefix: boolean
  description: string
  color: string
  icon: string
  mode: ServiceMode
  is_enabled: boolean
  sort_order: number
  is_online: boolean | null
  last_checked_at: string | null
  latency_ms: number | null
  last_error: string | null
  created_at: string
  updated_at: string
  public_url: string | null
  path_url: string
  local_port: number | null
}

export interface ServicePayload {
  name: string
  slug: string
  target_url: string
  entry_path: string
  strip_prefix: boolean
  description: string
  color: string
  icon: string
  mode: ServiceMode
  is_enabled: boolean
}

export interface ServiceStats {
  total: number
  enabled: number
  online: number
  offline: number
  unknown: number
  average_latency_ms: number | null
}

export interface GatewayStatus {
  synced: boolean
  synced_at: string | null
  hosts_file: string
  paths_file: string
  service_count: number
}

export interface GatewaySyncResult {
  synced: boolean
  service_count?: number
  synced_at?: string | null
  hosts_file?: string
  paths_file?: string
  message?: string
}

export interface Settings {
  base_domain: string
  public_scheme: 'http' | 'https'
  public_port: string
  health_interval: number
  skip_tls_verify: boolean
  site_name: string
}

export interface User {
  id: number
  username: string
  display_name: string
  email: string | null
  is_admin: boolean
  is_active: boolean
  service_ids: string[]
  last_login_at: string | null
  created_at: string
  updated_at: string
}

export interface UserPayload {
  username: string
  display_name: string
  email: string
  password?: string
  is_admin: boolean
  is_active: boolean
  service_ids: string[]
}

export interface AuditLog {
  id: number
  user_id: number | null
  username: string | null
  action: string
  resource_type: string | null
  resource_id: string | null
  detail: string | null
  ip_address: string | null
  created_at: string
}

export interface ServiceListData {
  services: Service[]
  stats: ServiceStats
  settings: Settings
}

export interface SystemInfo {
  services: Service[]
  stats: ServiceStats
  settings: Settings
  gateway: GatewayStatus
  recent_logs: AuditLog[]
}

export interface LoginResult {
  token: string
  user: User
}

export interface PublicInfo {
  site_name: string
  version: string
  base_domain: string
  public_scheme: string
  public_port: string
}

export interface HealthInfo {
  status: string
  version: string
  site_name: string
  time: string
}

export interface ApiEnvelope<T> {
  code: number
  message: string
  data?: T
}
