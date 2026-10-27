<template>
  <aside class="sidebar" :class="{ collapsed: app.sidebarCollapsed, 'mobile-open': app.mobileNavOpen }">
    <div class="sidebar-head">
      <AppLogo :compact="app.sidebarCollapsed" />
      <button class="collapse-btn" type="button" title="折叠侧栏" @click="app.toggleSidebar">
        <ChevronRight :class="{ flipped: !app.sidebarCollapsed }" />
      </button>
    </div>

    <div class="side-section">
      <span class="hud-label">指挥中心</span>
    </div>

    <nav class="side-nav">
      <RouterLink
        v-for="item in mainNav"
        :key="item.name"
        :to="{ name: item.name }"
        class="nav-link"
        :class="{ active: route.name === item.name }"
        @click="app.closeMobileNav()"
      >
        <component :is="item.icon" />
        <span class="nav-label">{{ item.label }}</span>
        <span class="nav-code">{{ item.code }}</span>
      </RouterLink>
    </nav>

    <div class="side-section">
      <span class="hud-label">系统</span>
    </div>

    <nav class="side-nav">
      <RouterLink
        v-for="item in systemNav"
        :key="item.name"
        :to="{ name: item.name }"
        class="nav-link"
        :class="{ active: route.name === item.name }"
        @click="app.closeMobileNav()"
      >
        <component :is="item.icon" />
        <span class="nav-label">{{ item.label }}</span>
        <span class="nav-code">{{ item.code }}</span>
      </RouterLink>
    </nav>

    <div class="side-spacer" />

    <div class="side-status">
      <div class="status-line">
        <span class="led" :class="app.gateway?.synced ? 'online' : 'warn'" />
        <span class="status-key">GATEWAY</span>
        <span class="status-value">{{ app.gateway?.synced ? 'SYNCED' : 'PENDING' }}</span>
      </div>
      <div class="status-line">
        <span class="status-key">DOMAIN</span>
        <span class="status-value" :title="domain">{{ domain }}</span>
      </div>
      <div class="status-line">
        <span class="status-key">VERSION</span>
        <span class="status-value">v{{ version }}</span>
      </div>
    </div>

    <div class="side-user">
      <div class="avatar">{{ initial }}</div>
      <div class="user-meta">
        <strong>{{ auth.displayName }}</strong>
        <span>@{{ auth.user?.username }}</span>
      </div>
      <button class="logout-btn" type="button" title="退出登录" @click="logout">
        <LogOut />
      </button>
    </div>
  </aside>

  <div v-if="app.mobileNavOpen" class="sidebar-backdrop" @click="app.closeMobileNav()" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import {
  Boxes,
  ChevronRight,
  LayoutDashboard,
  LogOut,
  Settings2,
  UserRound,
  Users,
} from 'lucide-vue-next'
import AppLogo from '@/components/brand/AppLogo.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const app = useAppStore()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const mainNav = [
  { name: 'dashboard', label: '仪表盘', code: '01', icon: LayoutDashboard },
  { name: 'services', label: '服务管理', code: '02', icon: Boxes },
]

const systemNav = computed(() => {
  const items = []
  if (auth.isAdmin) {
    items.push({ name: 'users', label: '用户管理', code: '03', icon: Users })
    items.push({ name: 'settings', label: '系统设置', code: '04', icon: Settings2 })
  }
  items.push({ name: 'profile', label: '个人资料', code: '05', icon: UserRound })
  return items
})

const initial = computed(() => (auth.displayName || 'X').slice(0, 1).toUpperCase())
const domain = computed(() => {
  const base = app.settings?.base_domain || 'localhost'
  const port = app.settings?.public_port
  return port ? `${base}:${port}` : base
})
const version = computed(() => app.publicInfo?.version || '1.0.0')

async function logout(): Promise<void> {
  await auth.logout()
  await router.push({ name: 'login' })
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 40;
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width);
  padding: 20px 15px 16px;
  border-right: 1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(8, 18, 38, 0.98) 0%, rgba(4, 9, 20, 0.99) 100%);
  box-shadow: 16px 0 58px rgba(0, 0, 0, 0.3);
  transition: width 0.22s ease, transform 0.22s ease;
}

.sidebar::after {
  content: '';
  position: absolute;
  top: 0;
  right: -1px;
  width: 1px;
  height: 140px;
  background: linear-gradient(180deg, var(--xl-cyan), transparent);
  opacity: 0.5;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed);
  padding-left: 12px;
  padding-right: 12px;
}

.sidebar-head {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 48px;
  /* Reserve room for the absolutely positioned toggle so it can never sit on
     top of the brand text. */
  padding: 0 34px 16px 4px;
  border-bottom: 1px solid var(--line);
}

.sidebar-head :deep(.app-logo) {
  flex: 1 1 auto;
  min-width: 0;
  gap: 10px;
  overflow: hidden;
}

/* Sidebar shows only the XILI-AI wordmark; the product text lives elsewhere. */
.sidebar-head :deep(.logo-product) {
  display: none;
}

.collapse-btn {
  position: absolute;
  top: 8px;
  right: 4px;
  z-index: 2;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  border: 1px solid var(--line);
  border-radius: 5px;
  background: rgba(4, 10, 22, 0.7);
  color: var(--text-muted);
  transition: 0.16s ease;
}

.collapse-btn:hover {
  color: var(--xl-cyan);
  border-color: var(--line-strong);
}

.collapse-btn svg {
  width: 14px;
  height: 14px;
  transition: transform 0.22s ease;
}

.collapse-btn svg.flipped {
  transform: rotate(180deg);
}

.side-section {
  padding: 16px 10px 7px;
}

.side-section .hud-label {
  font-size: 12px;
}

.side-nav {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.nav-code {
  margin-left: auto;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 13px;
  letter-spacing: 0.08em;
}

.side-spacer {
  flex: 1;
  min-height: 18px;
}

.side-status {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 11px 12px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: rgba(3, 8, 18, 0.55);
}

.status-line {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.06em;
}

.status-key {
  color: var(--text-muted);
}

.status-value {
  margin-left: auto;
  max-width: 120px;
  overflow: hidden;
  color: var(--text-dim);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.side-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  padding: 12px 6px 0;
  border-top: 1px solid var(--line);
}

.avatar {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  flex: 0 0 auto;
  border: 1px solid rgba(95, 211, 243, 0.45);
  border-radius: 7px;
  background: linear-gradient(135deg, rgba(58, 110, 216, 0.6), rgba(95, 211, 243, 0.18));
  color: #fff;
  font-family: var(--pixel);
  font-size: 10px;
  box-shadow: 0 4px 0 #03060d;
}

.user-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.user-meta strong {
  overflow: hidden;
  color: var(--text);
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-meta span {
  overflow: hidden;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  border: 1px solid transparent;
  border-radius: 5px;
  background: transparent;
  color: var(--text-muted);
  transition: 0.16s ease;
}

.logout-btn:hover {
  color: #ffb3c0;
  border-color: rgba(255, 95, 126, 0.3);
  background: rgba(255, 95, 126, 0.06);
}

.logout-btn svg {
  width: 15px;
  height: 15px;
}

.sidebar-backdrop {
  display: none;
}

.collapsed .nav-label,
.collapsed .nav-code,
.collapsed .side-section .hud-label,
.collapsed .side-status,
.collapsed .user-meta,
.collapsed .logout-btn {
  display: none;
}

/* Keep the toggle visible: stack it under the compact mark and let it sit in
   the normal flow so it cannot overlap anything. */
.collapsed .sidebar-head {
  flex-direction: column;
  justify-content: center;
  padding: 4px 0 12px;
  gap: 8px;
}

.collapsed .collapse-btn {
  position: static;
}

.collapsed .side-section {
  padding: 12px 0 4px;
}

.collapsed .nav-link {
  justify-content: center;
  padding: 12px 0;
}

.collapsed .side-user {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}

@media (max-width: 900px) {
  .sidebar {
    width: var(--sidebar-width) !important;
    transform: translateX(-104%);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 35;
    background: rgba(2, 5, 12, 0.64);
  }

  .collapse-btn {
    display: none;
  }

  .collapsed .nav-label,
  .collapsed .nav-code,
  .collapsed .side-section .hud-label,
  .collapsed .side-status,
  .collapsed .user-meta,
  .collapsed .logout-btn {
    display: initial;
  }

  .collapsed .side-status,
  .collapsed .user-meta {
    display: flex;
  }

  .sidebar-head {
    padding-right: 4px;
  }

  .collapsed .sidebar-head {
    flex-direction: row;
    justify-content: space-between;
    padding: 0 4px 16px;
  }

  .collapsed .nav-link {
    justify-content: flex-start;
    padding: 10px 12px;
  }

  .collapsed .side-user {
    justify-content: flex-start;
    padding-left: 10px;
    padding-right: 6px;
  }
}
</style>
