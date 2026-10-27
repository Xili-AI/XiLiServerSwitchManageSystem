<template>
  <div class="services-page">
    <header class="page-head">
      <div>
        <span class="hud-label">// SERVICE REGISTRY</span>
        <h1>服务注册表</h1>
        <p>登记内网服务，网关会实时生成同一条隧道下的访问入口。</p>
      </div>
      <div class="head-actions">
        <div class="search-box">
          <Search />
          <input v-model="query" type="search" placeholder="搜索名称、标识或目标地址" autocomplete="off" />
          <button v-if="query" class="search-clear" type="button" @click="query = ''">
            <X />
          </button>
        </div>
        <div class="view-toggle">
          <button
            class="view-btn"
            :class="{ active: viewMode === 'grid' }"
            type="button"
            title="卡片视图"
            @click="setView('grid')"
          >
            <LayoutGrid />
          </button>
          <button
            class="view-btn"
            :class="{ active: viewMode === 'table' }"
            type="button"
            title="表格视图"
            @click="setView('table')"
          >
            <Rows3 />
          </button>
        </div>
        <PixelButton v-if="auth.isAdmin" variant="primary" @click="app.openServiceForm()">
          <Plus />
          添加服务
        </PixelButton>
      </div>
    </header>

    <div class="toolbar">
      <div class="filter-chips">
        <button
          v-for="filter in FILTERS"
          :key="filter.value"
          class="filter-chip"
          :class="{ active: activeFilter === filter.value }"
          type="button"
          @click="activeFilter = filter.value"
        >
          {{ filter.label }}
          <span>{{ counts[filter.value] }}</span>
        </button>
      </div>
      <span class="result-count">{{ filteredServices.length }} / {{ services.services.length }} SERVICES</span>
    </div>

    <template v-if="filteredServices.length">
      <div v-if="viewMode === 'grid'" class="service-grid">
        <ServiceCard
          v-for="service in filteredServices"
          :key="service.id"
          :service="service"
          :settings="app.settings"
          @edit="app.openServiceForm($event)"
          @delete="confirmDelete"
          @embed="app.openEmbed($event)"
          @check="checkService"
        />
      </div>

      <div v-else class="pixel-panel table-wrap">
        <table class="table-cyber">
          <thead>
            <tr>
              <th>服务</th>
              <th>状态</th>
              <th>目标</th>
              <th>入口</th>
              <th>延迟</th>
              <th>更新</th>
              <th class="actions-head">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="service in filteredServices" :key="service.id">
              <td>
                <div class="service-cell">
                  <span class="mini-icon" :style="{ '--tile-accent': service.color }">
                    <component :is="resolveServiceIcon(service.icon)" />
                  </span>
                  <span class="service-cell-text">
                    <strong>{{ service.name }}</strong>
                    <small>/{{ service.slug }}</small>
                  </span>
                </div>
              </td>
              <td>
                <StatusLight :tone="statusTone(service)" :label="statusLabel(service)" />
              </td>
              <td><code class="code-chip" :title="service.target_url">{{ service.target_url }}</code></td>
              <td>
                <div class="entry-cell">
                  <code class="code-chip" :title="entryUrl(service)">{{ entryUrl(service) }}</code>
                  <button class="icon-action" type="button" title="复制入口" @click="copyEntry(service)">
                    <Check v-if="copiedId === service.id" />
                    <Copy v-else />
                  </button>
                </div>
              </td>
              <td class="mono-cell">{{ formatLatency(service.latency_ms) }}</td>
              <td class="mono-cell">{{ formatRelative(service.updated_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="icon-action" type="button" title="打开" @click="openService(service)">
                    <ExternalLink />
                  </button>
                  <template v-if="auth.isAdmin">
                    <button class="icon-action" type="button" title="立即检测" @click="checkService(service)">
                      <RefreshCw :class="{ spinning: checkingId === service.id }" />
                    </button>
                    <button class="icon-action" type="button" title="编辑" @click="app.openServiceForm(service)">
                      <Pencil />
                    </button>
                    <button class="icon-action danger" type="button" title="删除" @click="confirmDelete(service)">
                      <Trash2 />
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <EmptyState
      v-else
      :title="services.services.length ? '没有匹配的服务' : '服务列表为空'"
      :description="services.services.length ? '换个关键词或筛选条件试试。' : (auth.isAdmin ? '把内网地址登记进来，即可通过同一条隧道访问。' : '请联系管理员为你授权服务。')"
      :action-label="services.services.length || !auth.isAdmin ? '' : '接入第一个服务'"
      @action="app.openServiceForm()"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import {
  Check,
  Copy,
  ExternalLink,
  LayoutGrid,
  Pencil,
  Plus,
  RefreshCw,
  Rows3,
  Search,
  Trash2,
  X,
} from 'lucide-vue-next'
import ServiceCard from '@/components/service/ServiceCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusLight from '@/components/common/StatusLight.vue'
import PixelButton from '@/components/cyber/PixelButton.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useServicesStore } from '@/stores/services'
import type { Service } from '@/types'
import { formatLatency, formatRelative } from '@/utils/format'
import { resolveServiceIcon } from '@/utils/icons'
import { buildServiceUrl, copyText, statusLabel, statusTone } from '@/utils/url'
import { getServiceView, setServiceView } from '@/utils/storage'

const app = useAppStore()
const auth = useAuthStore()
const services = useServicesStore()
const message = useMessage()
const dialog = useDialog()

const FILTERS = [
  { value: 'all', label: '全部' },
  { value: 'online', label: '在线' },
  { value: 'offline', label: '离线' },
  { value: 'disabled', label: '已停用' },
] as const

type FilterValue = (typeof FILTERS)[number]['value']

const query = ref('')
const activeFilter = ref<FilterValue>('all')
const viewMode = ref<'grid' | 'table'>(getServiceView())
const copiedId = ref('')
const checkingId = ref('')

const counts = computed<Record<FilterValue, number>>(() => ({
  all: services.services.length,
  online: services.services.filter((service) => service.is_enabled && service.is_online === true).length,
  offline: services.services.filter((service) => service.is_enabled && service.is_online === false).length,
  disabled: services.services.filter((service) => !service.is_enabled).length,
}))

const filteredServices = computed(() => {
  const keyword = query.value.trim().toLowerCase()
  return services.services.filter((service) => {
    const matchesFilter =
      activeFilter.value === 'all' ||
      (activeFilter.value === 'online' && service.is_enabled && service.is_online === true) ||
      (activeFilter.value === 'offline' && service.is_enabled && service.is_online === false) ||
      (activeFilter.value === 'disabled' && !service.is_enabled)
    if (!matchesFilter) return false
    if (!keyword) return true
    return (
      service.name.toLowerCase().includes(keyword) ||
      service.slug.toLowerCase().includes(keyword) ||
      service.target_url.toLowerCase().includes(keyword) ||
      service.description.toLowerCase().includes(keyword)
    )
  })
})

function setView(value: 'grid' | 'table'): void {
  viewMode.value = value
  setServiceView(value)
}

function entryUrl(service: Service): string {
  return buildServiceUrl(service, app.settings)
}

function openService(service: Service): void {
  window.location.assign(entryUrl(service))
}

async function copyEntry(service: Service): Promise<void> {
  const done = await copyText(entryUrl(service))
  if (!done) {
    message.error('复制失败，请手动选择地址')
    return
  }
  copiedId.value = service.id
  message.success('入口地址已复制')
  window.setTimeout(() => {
    copiedId.value = ''
  }, 1600)
}

async function checkService(service: Service): Promise<void> {
  checkingId.value = service.id
  try {
    const updated = await services.check(service.id)
    message.success(updated?.is_online ? `${service.name} 在线` : `${service.name} 离线`)
  } catch (error) {
    message.error(error instanceof Error ? error.message : '检测失败')
  } finally {
    checkingId.value = ''
  }
}

function confirmDelete(service: Service): void {
  dialog.warning({
    title: '删除服务',
    content: `确定删除「${service.name}」？只会移除面板记录，不会停止或删除对应容器。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await services.remove(service.id)
        message.success('服务已删除，路由已更新')
      } catch (error) {
        message.error(error instanceof Error ? error.message : '删除失败')
      }
    },
  })
}

watch(
  () => services.services.length,
  () => {
    if (!services.services.length) activeFilter.value = 'all'
  },
)

onMounted(() => {
  if (!services.initialized) services.fetchAll().catch(() => {})
})
</script>

<style scoped>
.services-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.page-head h1 {
  margin: 3px 0 0;
  color: #f2f8ff;
  font-size: 26px;
  letter-spacing: 0.02em;
}

.page-head p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

.head-actions {
  display: flex;
  align-items: center;
  gap: 9px;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: min(330px, 42vw);
  height: 40px;
  padding: 0 12px;
  border: 2px solid #1b3766;
  border-radius: 6px;
  background: rgba(4, 10, 22, 0.8);
  transition: 0.16s ease;
}

.search-box:focus-within {
  border-color: var(--xl-cyan);
  box-shadow: 0 0 0 3px rgba(95, 211, 243, 0.08);
}

.search-box > svg {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
  color: var(--text-muted);
}

.search-box input {
  min-width: 0;
  flex: 1;
  padding: 0 9px;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text);
  font-size: 13px;
}

.search-box input::placeholder {
  color: #4f6a99;
}

.search-clear {
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border: 0;
  border-radius: 3px;
  background: transparent;
  color: var(--text-muted);
}

.search-clear svg {
  width: 13px;
  height: 13px;
}

.view-toggle {
  display: flex;
  padding: 3px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: rgba(3, 8, 18, 0.6);
}

.view-btn {
  display: grid;
  place-items: center;
  width: 31px;
  height: 31px;
  border: 0;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted);
}

.view-btn.active {
  background: rgba(58, 110, 216, 0.28);
  color: var(--xl-cyan);
}

.view-btn svg {
  width: 15px;
  height: 15px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 32px;
  padding: 0 11px;
  border: 1px solid var(--line);
  border-radius: 5px;
  background: rgba(4, 10, 22, 0.6);
  color: var(--text-dim);
  font-family: var(--mono);
  font-size: 14px;
  letter-spacing: 0.04em;
  transition: 0.16s ease;
}

.filter-chip span {
  padding: 0 5px;
  border-radius: 3px;
  background: rgba(95, 211, 243, 0.08);
  color: var(--text-muted);
  font-size: 12px;
}

.filter-chip:hover,
.filter-chip.active {
  border-color: var(--line-strong);
  color: #fff;
}

.filter-chip.active {
  background: rgba(58, 110, 216, 0.24);
  box-shadow: inset 0 0 18px rgba(95, 211, 243, 0.05);
}

.result-count {
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 13px;
  letter-spacing: 0.08em;
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

.table-wrap {
  overflow: hidden;
}

.table-cyber {
  min-width: 980px;
}

.service-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 170px;
}

.mini-icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  border: 1px solid color-mix(in srgb, var(--tile-accent) 42%, transparent);
  border-radius: 5px;
  background: color-mix(in srgb, var(--tile-accent) 10%, transparent);
  color: var(--tile-accent);
}

.mini-icon svg {
  width: 16px;
  height: 16px;
}

.service-cell-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.service-cell-text strong {
  overflow: hidden;
  color: var(--text);
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.service-cell-text small {
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
}

.entry-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 290px;
}

.entry-cell .code-chip {
  flex: 1;
  color: var(--xl-cyan);
}

.mono-cell {
  color: var(--text-dim);
  font-family: var(--mono);
  font-size: 13px;
  white-space: nowrap;
}

.row-actions {
  display: flex;
  gap: 5px;
}

.row-actions :deep(svg) {
  width: 14px;
  height: 14px;
}

.spinning {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.actions-head {
  text-align: right;
}

@media (max-width: 1000px) {
  .page-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .head-actions {
    width: 100%;
  }

  .search-box {
    flex: 1;
    width: auto;
  }

  .table-wrap {
    overflow-x: auto;
  }
}

@media (max-width: 640px) {
  .head-actions {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .search-box {
    grid-column: 1 / -1;
    width: 100%;
  }

  .view-toggle {
    justify-self: start;
  }

  .service-grid {
    grid-template-columns: 1fr;
  }
}
</style>
