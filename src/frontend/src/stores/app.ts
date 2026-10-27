import { ref } from 'vue'
import { defineStore } from 'pinia'
import { systemApi } from '@/api/system'
import type {
  AuditLog,
  GatewayStatus,
  GatewaySyncResult,
  HealthInfo,
  PublicInfo,
  Service,
  Settings,
} from '@/types'
import {
  getSidebarCollapsed,
  setSidebarCollapsed as persistSidebar,
} from '@/utils/storage'

export const useAppStore = defineStore('app', () => {
  const settings = ref<Settings | null>(null)
  const gateway = ref<GatewayStatus | null>(null)
  const recentLogs = ref<AuditLog[]>([])
  const publicInfo = ref<PublicInfo | null>(null)
  const health = ref<HealthInfo | null>(null)
  const configPreview = ref<{ hosts: string; paths: string } | null>(null)

  const sidebarCollapsed = ref(getSidebarCollapsed())
  const mobileNavOpen = ref(false)
  const serviceFormOpen = ref(false)
  const editingService = ref<Service | null>(null)
  const embedService = ref<Service | null>(null)

  function applySettings(value: Settings): void {
    settings.value = value
  }

  async function loadSettings(): Promise<Settings> {
    const value = await systemApi.settings()
    settings.value = value
    return value
  }

  async function loadInfo(): Promise<void> {
    const info = await systemApi.info()
    settings.value = info.settings
    gateway.value = info.gateway
    recentLogs.value = info.recent_logs
  }

  async function loadPublicInfo(): Promise<void> {
    publicInfo.value = await systemApi.publicInfo()
  }

  async function loadHealth(): Promise<void> {
    health.value = await systemApi.health()
  }

  async function saveSettings(payload: Partial<Settings>): Promise<GatewaySyncResult> {
    const result = await systemApi.saveSettings(payload)
    settings.value = result.settings
    return result.gateway
  }

  async function syncGateway(): Promise<GatewaySyncResult> {
    const result = await systemApi.syncGateway()
    await loadInfo()
    return result
  }

  async function loadGatewayConfig(): Promise<void> {
    configPreview.value = await systemApi.gatewayConfig()
  }

  function toggleSidebar(): void {
    sidebarCollapsed.value = !sidebarCollapsed.value
    persistSidebar(sidebarCollapsed.value)
  }

  function openMobileNav(): void {
    mobileNavOpen.value = true
  }

  function closeMobileNav(): void {
    mobileNavOpen.value = false
  }

  function openServiceForm(service: Service | null = null): void {
    editingService.value = service
    serviceFormOpen.value = true
  }

  function closeServiceForm(): void {
    serviceFormOpen.value = false
    editingService.value = null
  }

  function openEmbed(service: Service): void {
    embedService.value = service
  }

  function closeEmbed(): void {
    embedService.value = null
  }

  return {
    settings,
    gateway,
    recentLogs,
    publicInfo,
    health,
    configPreview,
    sidebarCollapsed,
    mobileNavOpen,
    serviceFormOpen,
    editingService,
    embedService,
    applySettings,
    loadSettings,
    loadInfo,
    loadPublicInfo,
    loadHealth,
    saveSettings,
    syncGateway,
    loadGatewayConfig,
    toggleSidebar,
    openMobileNav,
    closeMobileNav,
    openServiceForm,
    closeServiceForm,
    openEmbed,
    closeEmbed,
  }
})
