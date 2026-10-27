<template>
  <header class="app-header">
    <div class="header-left">
      <button class="mobile-menu" type="button" title="打开导航" @click="app.openMobileNav()">
        <Menu />
      </button>
      <div class="header-title">
        <span class="hud-label">XILI-AI // COMMAND DECK</span>
        <h1>
          <span class="crumb-root">控制台</span>
          <span class="crumb-sep">/</span>
          <span class="crumb-current">{{ title }}</span>
        </h1>
      </div>
    </div>

    <div class="header-right">
      <div class="sys-clock">
        <span class="led online" />
        <span class="clock-value">{{ clock }}</span>
        <span class="clock-zone">CST</span>
      </div>

      <StatusLight
        class="gateway-light"
        :tone="app.gateway?.synced ? 'online' : 'warn'"
        :label="app.gateway?.synced ? 'GATEWAY SYNCED' : 'GATEWAY PENDING'"
      />

      <PixelButton variant="primary" size="sm" class="add-btn" @click="app.openServiceForm()">
        <Plus />
        添加服务
      </PixelButton>

      <n-dropdown trigger="click" :options="userOptions" @select="handleSelect">
        <button class="user-chip" type="button">
          <span class="avatar">{{ initial }}</span>
          <span class="user-name">{{ auth.displayName }}</span>
          <ChevronDown class="chevron" />
        </button>
      </n-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NDropdown } from 'naive-ui'
import { ChevronDown, Menu, Plus } from 'lucide-vue-next'
import StatusLight from '@/components/common/StatusLight.vue'
import PixelButton from '@/components/cyber/PixelButton.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { formatClock } from '@/utils/format'

const app = useAppStore()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const title = computed(() => route.meta.title || '控制台')
const initial = computed(() => (auth.displayName || 'X').slice(0, 1).toUpperCase())
const clock = ref(formatClock())
let timer = 0

const userOptions = [
  { label: '个人资料', key: 'profile' },
  { label: '退出登录', key: 'logout' },
]

function handleSelect(key: string): void {
  if (key === 'profile') {
    router.push({ name: 'profile' })
    return
  }
  if (key === 'logout') {
    auth.logout().finally(() => {
      router.push({ name: 'login' })
    })
  }
}

onMounted(() => {
  timer = window.setInterval(() => {
    clock.value = formatClock()
  }, 1000)
})

onBeforeUnmount(() => {
  window.clearInterval(timer)
})
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 25;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: var(--header-height);
  padding: 10px 28px;
  border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(5, 9, 20, 0.98), rgba(5, 9, 20, 0.86));
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.header-title {
  min-width: 0;
}

.header-title h1 {
  margin: 1px 0 0;
  overflow: hidden;
  color: #f0f7ff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.crumb-root {
  color: var(--text-muted);
  font-weight: 500;
}

.crumb-sep {
  margin: 0 7px;
  color: #2f4d7f;
}

.crumb-current {
  color: #f0f7ff;
}

.header-title .hud-label {
  font-size: 11px;
}

.sys-clock {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 10px;
  border: 1px solid var(--line);
  border-radius: 4px;
  background: rgba(3, 8, 18, 0.6);
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 14px;
  letter-spacing: 0.08em;
}

.clock-value {
  color: var(--text-dim);
  font-variant-numeric: tabular-nums;
}

.clock-zone {
  color: var(--text-muted);
  font-size: 12px;
}

.gateway-light {
  flex: 0 0 auto;
}

.add-btn :deep(svg) {
  width: 15px;
  height: 15px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 38px;
  padding: 3px 9px 3px 4px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: rgba(3, 8, 18, 0.6);
  color: var(--text);
  transition: 0.16s ease;
}

.user-chip:hover {
  border-color: var(--line-strong);
  background: rgba(18, 36, 72, 0.5);
}

.avatar {
  display: grid;
  place-items: center;
  width: 29px;
  height: 29px;
  border: 1px solid rgba(95, 211, 243, 0.4);
  border-radius: 5px;
  background: linear-gradient(135deg, rgba(58, 110, 216, 0.65), rgba(95, 211, 243, 0.16));
  color: #fff;
  font-family: var(--pixel);
  font-size: 8px;
}

.user-name {
  max-width: 110px;
  overflow: hidden;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chevron {
  width: 13px;
  height: 13px;
  color: var(--text-muted);
}

.mobile-menu {
  display: none;
  place-items: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: rgba(3, 8, 18, 0.6);
  color: var(--text-dim);
}

.mobile-menu svg {
  width: 18px;
  height: 18px;
}

@media (max-width: 1180px) {
  .sys-clock,
  .gateway-light {
    display: none;
  }
}

@media (max-width: 900px) {
  .app-header {
    padding: 10px 16px;
  }

  .mobile-menu {
    display: grid;
  }

  .header-title h1 {
    font-size: 19px;
  }

  .user-name,
  .chevron {
    display: none;
  }

  .user-chip {
    padding: 3px;
    border-color: transparent;
    background: transparent;
  }

  .add-btn {
    padding: 0 10px;
  }
}
</style>
