<template>
  <div class="dashboard">
    <section class="stats-grid">
      <StatCard
        label="服务总数"
        :value="services.stats.total"
        :icon="Boxes"
        accent="#5fd3f3"
        :hint="`${services.stats.enabled} 个已启用`"
        :meter="services.stats.total ? services.stats.enabled / services.stats.total : 0.08"
      />
      <StatCard
        label="在线服务"
        :value="services.stats.online"
        :icon="Activity"
        accent="#8bffb0"
        :hint="`${services.stats.offline} 个离线 · ${services.stats.unknown} 个待检测`"
        :meter="services.stats.enabled ? services.stats.online / services.stats.enabled : 0.08"
      />
      <StatCard
        label="平均延迟"
        :value="services.stats.average_latency_ms ?? 0"
        suffix="ms"
        :icon="Timer"
        accent="#ffcc66"
        hint="仅统计当前在线服务"
        :meter="0.58"
      />
      <StatCard
        label="网关状态"
        :value="app.gateway?.synced ? 'SYNCED' : 'PENDING'"
        :icon="Cable"
        :accent="app.gateway?.synced ? '#7c5cff' : '#ff5f7e'"
        :hint="app.gateway?.synced ? '路由表已下发' : '等待配置同步'"
        :meter="app.gateway?.synced ? 1 : 0.3"
      />
    </section>

    <section class="hero pixel-panel">
      <div class="hero-bg" aria-hidden="true">
        <svg class="hero-wave" viewBox="0 0 1200 360" preserveAspectRatio="none">
          <defs>
            <path
              id="heroWavePath"
              d="M0 280 H120 L140 280 L150 250 L160 310 L170 280 H300 L320 280 L330 245 L340 315 L350 280 H470 L490 280 L500 260 L510 300 L520 280 H650 L670 280 L680 230 L690 330 L700 280 H820 L840 280 L850 255 L860 305 L870 280 H1000 L1020 280 L1030 240 L1040 320 L1050 280 H1180 L1200 280"
            />
            <linearGradient id="heroWaveStroke" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stop-color="#5fd3f3" stop-opacity="0" />
              <stop offset="0.12" stop-color="#5fd3f3" stop-opacity="0.85" />
              <stop offset="0.55" stop-color="#7c5cff" stop-opacity="0.7" />
              <stop offset="0.9" stop-color="#5fd3f3" stop-opacity="0.85" />
              <stop offset="1" stop-color="#5fd3f3" stop-opacity="0" />
            </linearGradient>
            <radialGradient id="heroElectronGlow">
              <stop offset="0" stop-color="#eaffff" stop-opacity="0.95" />
              <stop offset="0.3" stop-color="#5fd3f3" stop-opacity="0.5" />
              <stop offset="1" stop-color="#5fd3f3" stop-opacity="0" />
            </radialGradient>
          </defs>

          <use href="#heroWavePath" class="wave-base" />
          <use href="#heroWavePath" class="wave-base wave-base-2" transform="translate(0 -130)" />
          <path class="wave-pulse" d="M0 280 H120 L140 280 L150 250 L160 310 L170 280 H300 L320 280 L330 245 L340 315 L350 280 H470 L490 280 L500 260 L510 300 L520 280 H650 L670 280 L680 230 L690 330 L700 280 H820 L840 280 L850 255 L860 305 L870 280 H1000 L1020 280 L1030 240 L1040 320 L1050 280 H1180 L1200 280" />

          <g class="wave-electron">
            <circle r="9" fill="url(#heroElectronGlow)" />
            <circle r="2" fill="#eaffff" />
            <animateMotion dur="8s" repeatCount="indefinite">
              <mpath href="#heroWavePath" xlink:href="#heroWavePath" />
            </animateMotion>
          </g>
          <g class="wave-electron">
            <circle r="8" fill="url(#heroElectronGlow)" />
            <circle r="1.8" fill="#eaffff" />
            <animateMotion dur="12s" begin="-4s" repeatCount="indefinite">
              <mpath href="#heroWavePath" xlink:href="#heroWavePath" />
            </animateMotion>
          </g>
          <g class="wave-electron">
            <circle r="7" fill="url(#heroElectronGlow)" />
            <circle r="1.6" fill="#eaffff" />
            <animateMotion dur="16s" begin="-9s" repeatCount="indefinite">
              <mpath href="#heroWavePath" xlink:href="#heroWavePath" />
            </animateMotion>
          </g>
        </svg>
      </div>

      <div class="hero-copy">
        <span class="hud-label">SYSTEM OVERVIEW // SINGLE TUNNEL</span>
        <h2>苏州矽励科技</h2>
        <p class="hero-desc">
          服务网关管理平台
        </p>

        <div class="hero-actions">
          <PixelButton v-if="auth.isAdmin" variant="primary" @click="app.openServiceForm()">
            <Plus />
            接入新服务
          </PixelButton>
          <PixelButton variant="ghost" @click="router.push({ name: 'services' })">
            <Boxes />
            服务管理
          </PixelButton>
          <PixelButton v-if="auth.isAdmin" variant="ghost" :loading="syncing" @click="syncGateway">
            <RefreshCw />
            同步网关
          </PixelButton>
        </div>

        <div class="hero-terminal terminal-window">
          <div class="terminal-bar">
            <span class="terminal-dot red" />
            <span class="terminal-dot amber" />
            <span class="terminal-dot green" />
            <span class="term-title">system.status</span>
          </div>
          <div class="terminal-body">
            <div class="terminal-line">
              <span class="term-key">gateway</span>
              <span :class="app.gateway?.synced ? 'term-ok' : 'term-warn'">
                {{ app.gateway?.synced ? 'SYNCED' : 'PENDING' }}
              </span>
              <span class="term-sep">/</span>
              <span class="term-key">tunnel</span>
              <span class="term-val">single</span>
            </div>
            <div class="terminal-line">
              <span class="term-key">domain</span>
              <span class="term-val">{{ domainLabel }}</span>
              <span class="term-sep">/</span>
              <span class="term-key">services</span>
              <span class="term-val">{{ services.stats.enabled }} enabled</span>
            </div>
            <div class="terminal-line">
              <span class="term-key">health</span>
              <span class="term-val">{{ services.stats.online }} online</span>
              <span class="term-sep">·</span>
              <span class="term-val">{{ services.stats.offline }} offline</span>
              <span class="terminal-caret" />
            </div>
          </div>
        </div>
      </div>

      <div class="hero-visual">
        <GatewayOrb :services="services.services" :synced="Boolean(app.gateway?.synced)" />
        <div class="hero-chip">
          <span class="led" :class="app.gateway?.synced ? 'online' : 'warn'" />
          {{ app.gateway?.service_count ?? 0 }} ROUTES ACTIVE
        </div>
      </div>
    </section>

    <section class="section-head">
      <div>
        <span class="hud-label">SERVICE MATRIX</span>
        <h2>服务网关</h2>
      </div>
      <button class="text-link" type="button" @click="router.push({ name: 'services' })">
        查看全部
        <ArrowRight />
      </button>
    </section>

    <section v-if="services.services.length" class="service-grid">
      <ServiceCard
        v-for="service in recentServices"
        :key="service.id"
        :service="service"
        :settings="app.settings"
        @edit="app.openServiceForm($event)"
        @delete="confirmDelete"
        @embed="app.openEmbed($event)"
        @check="checkService"
      />
    </section>
    <EmptyState
      v-else
      title="还没有接入服务"
      :description="auth.isAdmin ? '把内网服务的地址登记进来，网关会立即生成可通过同一条隧道访问的入口。' : '请联系管理员为你授权可访问的服务。'"
      :action-label="auth.isAdmin ? '接入第一个服务' : ''"
      @action="app.openServiceForm()"
    />

    <section class="lower-grid">
      <div class="pixel-panel activity-panel">
        <div class="panel-head">
          <div>
            <span class="hud-label">AUDIT STREAM</span>
            <h3>最近活动</h3>
          </div>
          <span class="pixel-tag">{{ app.recentLogs.length }} EVENTS</span>
        </div>
        <div class="activity-list">
          <div v-for="log in app.recentLogs" :key="log.id" class="activity-row">
            <span class="activity-dot" :class="`tone-${actionTone(log.action)}`" />
            <div class="activity-main">
              <strong>{{ actionLabel(log.action) }}</strong>
              <span>{{ log.detail || log.resource_type || 'system' }}</span>
            </div>
            <span class="activity-user">{{ log.username || 'system' }}</span>
            <span class="activity-time">{{ formatRelative(log.created_at) }}</span>
          </div>
          <div v-if="!app.recentLogs.length" class="activity-empty">
            暂无操作记录。完成一次登录或服务变更后，审计流会出现在这里。
          </div>
        </div>
      </div>

      <div class="pixel-panel quick-panel">
        <div class="panel-head">
          <div>
            <span class="hud-label">QUICK ACTIONS</span>
            <h3>快捷指令</h3>
          </div>
        </div>
        <div class="quick-list">
          <button v-if="auth.isAdmin" class="quick-item" type="button" @click="app.openServiceForm()">
            <span class="quick-icon"><Plus /></span>
            <span><strong>接入服务</strong><small>登记一个新的内网地址</small></span>
            <ArrowRight />
          </button>
          <button v-if="auth.isAdmin" class="quick-item" type="button" @click="router.push({ name: 'settings' })">
            <span class="quick-icon"><Settings2 /></span>
            <span><strong>网关设置</strong><small>主域名、协议与健康检查</small></span>
            <ArrowRight />
          </button>
          <button v-if="auth.isAdmin" class="quick-item" type="button" @click="syncGateway">
            <span class="quick-icon"><RefreshCw /></span>
            <span><strong>强制同步</strong><small>重新生成 Nginx 路由表</small></span>
            <ArrowRight />
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDialog, useMessage } from 'naive-ui'
import {
  Activity,
  ArrowRight,
  Boxes,
  Cable,
  Plus,
  RefreshCw,
  Settings2,
  Timer,
} from 'lucide-vue-next'
import StatCard from '@/components/common/StatCard.vue'
import GatewayOrb from '@/components/common/GatewayOrb.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ServiceCard from '@/components/service/ServiceCard.vue'
import PixelButton from '@/components/cyber/PixelButton.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useServicesStore } from '@/stores/services'
import type { Service } from '@/types'
import { actionLabel, actionTone, formatRelative } from '@/utils/format'

const app = useAppStore()
const auth = useAuthStore()
const services = useServicesStore()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const syncing = ref(false)

const recentServices = computed(() => services.services.slice(0, 6))
const domainLabel = computed(() => {
  const base = app.settings?.base_domain || 'localhost'
  const port = app.settings?.public_port
  return port ? `${base}:${port}` : base
})

async function syncGateway(): Promise<void> {
  if (syncing.value) return
  syncing.value = true
  try {
    const result = await app.syncGateway()
    message.success(result.synced ? '网关路由表已同步' : '同步未完成，请检查网关日志')
    await services.fetchAll(true)
  } catch (error) {
    message.error(error instanceof Error ? error.message : '同步失败')
  } finally {
    syncing.value = false
  }
}

async function checkService(service: Service): Promise<void> {
  try {
    const updated = await services.check(service.id)
    message.success(updated?.is_online ? `${service.name} 在线` : `${service.name} 离线`)
  } catch (error) {
    message.error(error instanceof Error ? error.message : '检测失败')
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

onMounted(() => {
  if (!services.initialized) services.fetchAll().catch(() => {})
  if (!app.settings) app.loadSettings().catch(() => {})
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(330px, 0.75fr);
  align-items: center;
  gap: 20px;
  min-height: 350px;
  padding: 30px 30px 24px;
  overflow: hidden;
}


.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
  -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 8%, #000 92%, transparent 100%);
  mask-image: linear-gradient(90deg, transparent 0, #000 8%, #000 92%, transparent 100%);
}

.hero-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(95, 211, 243, 0.16) 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: 0.24;
  -webkit-mask-image: radial-gradient(circle at 70% 45%, #000 0 30%, transparent 78%);
  mask-image: radial-gradient(circle at 70% 45%, #000 0 30%, transparent 78%);
}

.hero-wave {
  display: block;
  width: 100%;
  height: 100%;
}

.wave-base {
  fill: none;
  stroke: rgba(95, 211, 243, 0.14);
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}

.wave-base-2 {
  stroke: rgba(124, 92, 255, 0.1);
}

.wave-pulse {
  fill: none;
  stroke: url(#heroWaveStroke);
  stroke-width: 1.6;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
  stroke-dasharray: 90 1200;
  animation: hero-wave-dash 7s linear infinite;
}

@keyframes hero-wave-dash {
  to {
    stroke-dashoffset: -1290;
  }
}

.wave-electron {
  filter: drop-shadow(0 0 5px rgba(95, 211, 243, 0.7));
}

.hero-copy {
  position: relative;
  z-index: 2;
  max-width: 700px;
}

.hero-copy h2 {
  margin: 8px 0 0;
  color: #f2f8ff;
  font-size: clamp(26px, 2.6vw, 36px);
  line-height: 1.2;
  letter-spacing: 0.02em;
}

.hero-desc {
  max-width: 580px;
  margin: 10px 0 18px;
  color: var(--text-dim);
  font-size: 13.5px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.hero-actions :deep(svg) {
  width: 15px;
  height: 15px;
}

.hero-terminal {
  max-width: 560px;
  margin-top: 18px;
}

.term-title {
  margin-left: 4px;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.1em;
}

.terminal-line {
  font-size: 16px;
}

.term-key {
  display: inline-block;
  min-width: 70px;
  margin-right: 7px;
  color: var(--xl-cyan);
}

.term-val {
  color: var(--text);
}

.term-ok {
  color: var(--xl-lime);
}

.term-warn {
  color: var(--xl-amber);
}

.term-sep {
  margin: 0 8px;
  color: var(--text-muted);
}

.hero-visual {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-top: -4px;
  padding: 5px 10px;
  border: 1px solid var(--line);
  border-radius: 4px;
  background: rgba(3, 8, 18, 0.7);
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 13px;
  letter-spacing: 0.08em;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-top: 4px;
}

.section-head h2 {
  margin: 2px 0 0;
  color: #f0f7ff;
  font-size: 20px;
}

.text-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  color: var(--xl-cyan);
  font-family: var(--mono);
  font-size: 15px;
  letter-spacing: 0.06em;
}

.text-link svg {
  width: 15px;
  height: 15px;
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

.lower-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
  gap: 14px;
}

.activity-panel,
.quick-panel {
  overflow: hidden;
}

.activity-list {
  display: flex;
  flex-direction: column;
  padding: 6px 0;
}

.activity-row {
  display: grid;
  grid-template-columns: 10px minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 11px;
  padding: 10px 20px;
  border-bottom: 1px solid rgba(95, 211, 243, 0.06);
}

.activity-row:last-child {
  border-bottom: 0;
}

.activity-dot {
  width: 7px;
  height: 7px;
  border-radius: 1px;
  background: var(--xl-cyan);
  box-shadow: 0 0 9px currentColor;
}

.tone-lime {
  color: var(--xl-lime);
  background: var(--xl-lime);
}

.tone-amber {
  color: var(--xl-amber);
  background: var(--xl-amber);
}

.tone-red {
  color: var(--xl-red);
  background: var(--xl-red);
}

.tone-violet {
  color: var(--xl-violet);
  background: var(--xl-violet);
}

.tone-cyan {
  color: var(--xl-cyan);
  background: var(--xl-cyan);
}

.activity-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.activity-main strong {
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
}

.activity-main span {
  overflow: hidden;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-user {
  color: var(--text-dim);
  font-family: var(--mono);
  font-size: 12px;
}

.activity-time {
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  white-space: nowrap;
}

.activity-empty {
  padding: 34px 20px;
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
}

.quick-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
}

.quick-item {
  display: flex;
  align-items: center;
  gap: 11px;
  width: 100%;
  padding: 11px 10px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: var(--text-dim);
  text-align: left;
  transition: 0.16s ease;
}

.quick-item:hover {
  border-color: var(--line);
  background: rgba(18, 36, 72, 0.4);
}

.quick-icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  border: 1px solid var(--line);
  border-radius: 5px;
  background: rgba(4, 10, 22, 0.7);
  color: var(--xl-cyan);
}

.quick-icon svg {
  width: 16px;
  height: 16px;
}

.quick-item > span:nth-child(2) {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.quick-item strong {
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
}

.quick-item small {
  color: var(--text-muted);
  font-size: 11.5px;
}

.quick-item > svg {
  width: 14px;
  height: 14px;
  color: var(--text-muted);
}

@media (max-width: 1180px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    margin-top: -18px;
  }

  .lower-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .hero-bg {
    opacity: 0.55;
  }

  .wave-base-2 {
    display: none;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .hero {
    padding: 22px 20px 18px;
  }

  .hero-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .hero-actions :deep(.pixel-btn:first-child) {
    grid-column: 1 / -1;
  }

  .hero-terminal {
    display: none;
  }

  .activity-row {
    grid-template-columns: 10px minmax(0, 1fr) auto;
  }

  .activity-user {
    display: none;
  }

  .service-grid {
    grid-template-columns: 1fr;
  }
}
</style>
