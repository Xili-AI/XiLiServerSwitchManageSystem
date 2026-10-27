import type {
  AuditLog,
  GatewayStatus,
  GatewaySyncResult,
  HealthInfo,
  PublicInfo,
  Settings,
  SystemInfo,
} from '@/types'
import { request } from './http'

export const systemApi = {
  health() {
    return request<HealthInfo>({ url: '/health' })
  },
  publicInfo() {
    return request<PublicInfo>({ url: '/public/info' })
  },
  info() {
    return request<SystemInfo>({ url: '/system/info' })
  },
  settings() {
    return request<Settings>({ url: '/system/settings' })
  },
  saveSettings(payload: Partial<Settings>) {
    return request<{ settings: Settings; gateway: GatewaySyncResult }>({
      url: '/system/settings',
      method: 'put',
      data: payload,
    })
  },
  syncGateway() {
    return request<GatewaySyncResult>({ url: '/system/gateway/sync', method: 'post' })
  },
  gatewayConfig() {
    return request<{ hosts: string; paths: string }>({ url: '/system/gateway/config' })
  },
  gatewayStatus() {
    return request<GatewayStatus>({ url: '/system/info' })
  },
  auditLogs(limit = 20) {
    return request<{ logs: AuditLog[] }>({
      url: `/system/audit-logs?limit=${encodeURIComponent(String(limit))}`,
    })
  },
}
