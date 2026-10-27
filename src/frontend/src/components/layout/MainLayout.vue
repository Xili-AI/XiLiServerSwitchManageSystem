<template>
  <div class="app-shell" :class="{ collapsed: app.sidebarCollapsed }">
    <CyberBackground variant="app" />
    <ScanlineOverlay subtle />
    <AppSidebar />
    <div class="app-main">
      <AppHeader />
      <main class="app-content">
        <div v-if="lanIpAccess" class="lan-notice">
          <span class="led warn" />
          <span>
            当前通过局域网 IP 访问：服务使用 <code>/p/&lt;标识&gt;/</code> 路径模式。
            Portainer / File Browser 等单页应用请使用隧道公网子域名访问，路径模式会出现 MIME / CSP 错误。
          </span>
        </div>
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <ServiceFormModal />
    <EmbedModal />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useIntervalFn } from '@vueuse/core'
import CyberBackground from '@/components/cyber/CyberBackground.vue'
import ScanlineOverlay from '@/components/cyber/ScanlineOverlay.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ServiceFormModal from '@/components/service/ServiceFormModal.vue'
import EmbedModal from '@/components/service/EmbedModal.vue'
import { useAppStore } from '@/stores/app'
import { useServicesStore } from '@/stores/services'

const app = useAppStore()
const services = useServicesStore()

const lanIpAccess = computed(() => {
  const host = window.location.hostname
  return /^\d{1,3}(\.\d{1,3}){3}$/.test(host) && !host.startsWith('127.')
})

async function refresh(): Promise<void> {
  try {
    await Promise.all([app.loadInfo(), services.fetchAll(true)])
  } catch {
    // The HTTP interceptor handles auth expiry; transient errors keep the UI alive.
  }
}

onMounted(async () => {
  await Promise.allSettled([app.loadInfo(), app.loadPublicInfo(), services.fetchAll()])
})

useIntervalFn(() => {
  if (document.visibilityState === 'visible') refresh()
}, 30000)
</script>

<style scoped>
.app-shell {
  position: relative;
  min-height: 100vh;
}

.app-main {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  margin-left: var(--sidebar-width);
  transition: margin-left 0.22s ease;
}

.app-shell.collapsed .app-main {
  margin-left: var(--sidebar-collapsed);
}

.app-content {
  position: relative;
  z-index: 1;
  padding: 24px 28px 56px;
}

.lan-notice {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin-bottom: 16px;
  padding: 10px 13px;
  border: 1px solid rgba(255, 204, 102, 0.35);
  border-radius: 6px;
  background: rgba(255, 204, 102, 0.06);
  color: #e8cf9b;
  font-size: 12.5px;
  line-height: 1.6;
}

.lan-notice .led {
  margin-top: 5px;
  flex: 0 0 auto;
}

.lan-notice code {
  color: var(--xl-cyan);
  font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 11.5px;
}

@media (max-width: 900px) {
  .app-main,
  .app-shell.collapsed .app-main {
    margin-left: 0;
  }

  .app-content {
    padding: 18px 16px 42px;
  }
}
</style>
