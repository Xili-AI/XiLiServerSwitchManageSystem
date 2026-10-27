import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { servicesApi, type ServiceMutationResult } from '@/api/services'
import type { Service, ServicePayload, ServiceStats } from '@/types'
import { useAppStore } from './app'

const EMPTY_STATS: ServiceStats = {
  total: 0,
  enabled: 0,
  online: 0,
  offline: 0,
  unknown: 0,
  average_latency_ms: null,
}

export const useServicesStore = defineStore('services', () => {
  const services = ref<Service[]>([])
  const stats = ref<ServiceStats>({ ...EMPTY_STATS })
  const loading = ref(false)
  const initialized = ref(false)
  const lastLoadedAt = ref<number>(0)

  const total = computed(() => stats.value.total)
  const online = computed(() => stats.value.online)
  const offline = computed(() => stats.value.offline)
  const averageLatency = computed(() => stats.value.average_latency_ms)

  function replaceService(updated: Service): void {
    const index = services.value.findIndex((item) => item.id === updated.id)
    if (index >= 0) services.value[index] = updated
  }

  async function fetchAll(silent = false): Promise<void> {
    if (loading.value) return
    if (!silent) loading.value = true
    try {
      const data = await servicesApi.list()
      services.value = data.services
      stats.value = data.stats
      useAppStore().applySettings(data.settings)
      lastLoadedAt.value = Date.now()
    } finally {
      if (!silent) loading.value = false
      initialized.value = true
    }
  }

  async function create(payload: ServicePayload): Promise<ServiceMutationResult> {
    const result = await servicesApi.create(payload)
    await fetchAll(true)
    return result
  }

  async function update(id: string, payload: ServicePayload): Promise<ServiceMutationResult> {
    const result = await servicesApi.update(id, payload)
    replaceService(result.service)
    await fetchAll(true)
    return result
  }

  async function remove(id: string): Promise<void> {
    await servicesApi.remove(id)
    services.value = services.value.filter((item) => item.id !== id)
    await fetchAll(true)
  }

  async function check(id: string): Promise<Service | null> {
    const result = await servicesApi.check(id)
    replaceService(result.service)
    await fetchAll(true)
    return result.service
  }

  function getById(id: string): Service | null {
    return services.value.find((item) => item.id === id) || null
  }

  return {
    services,
    stats,
    loading,
    initialized,
    lastLoadedAt,
    total,
    online,
    offline,
    averageLatency,
    fetchAll,
    create,
    update,
    remove,
    check,
    getById,
  }
})
