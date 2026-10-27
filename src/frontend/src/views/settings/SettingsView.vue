<template>
  <div class="settings-page">
    <header class="page-head">
      <div>
        <span class="hud-label">// GATEWAY CONFIGURATION</span>
        <h1>网关配置</h1>
        <p>调整公网入口、路由下发与健康检查。保存后网关会立即重新加载。</p>
      </div>
      <StatusLight
        :tone="app.gateway?.synced ? 'online' : 'warn'"
        :label="app.gateway?.synced ? 'ROUTING SYNCED' : 'ROUTING PENDING'"
      />
    </header>

    <div class="settings-grid">
      <form class="pixel-panel settings-card" @submit.prevent="save">
        <div class="panel-head">
          <div>
            <span class="hud-label">PUBLIC ENTRY</span>
            <h2>公网入口</h2>
          </div>
          <span class="pixel-tag">{{ form.public_scheme.toUpperCase() }}</span>
        </div>
        <div class="settings-body">
          <div class="field">
            <label class="pixel-label" for="base-domain">主域名 / BASE DOMAIN</label>
            <input
              id="base-domain"
              v-model="form.base_domain"
              class="pixel-input"
              placeholder="example.com 或 localhost"
            />
            <span class="pixel-hint">
              子域名入口为 &lt;服务标识&gt;.&lt;主域名&gt;。生产环境需要把 *.{{ form.base_domain || 'example.com' }} 解析到同一条隧道。
            </span>
          </div>

          <div class="field">
            <label class="pixel-label">公网协议</label>
            <div class="segmented">
              <button
                v-for="option in SCHEMES"
                :key="option"
                type="button"
                :class="{ active: form.public_scheme === option }"
                @click="form.public_scheme = option"
              >
                {{ option.toUpperCase() }}
              </button>
            </div>
          </div>

          <div class="field">
            <label class="pixel-label" for="public-port">公网端口 / PUBLIC PORT</label>
            <input
              id="public-port"
              v-model="form.public_port"
              class="pixel-input"
              inputmode="numeric"
              placeholder="443 或留空"
            />
            <span class="pixel-hint">留空时按协议使用 443 / 80；隧道使用非标准端口时填写该端口。</span>
          </div>

          <div class="field">
            <label class="pixel-label" for="health-interval">健康检查间隔 / SECONDS</label>
            <input
              id="health-interval"
              v-model.number="form.health_interval"
              class="pixel-input"
              inputmode="numeric"
              type="number"
              min="5"
              max="3600"
            />
            <span class="pixel-hint">后台线程会按此间隔探测所有启用服务，范围 5-3600 秒。</span>
          </div>

          <div class="field">
            <label class="pixel-label" for="site-name">站点名称</label>
            <input id="site-name" v-model="form.site_name" class="pixel-input" maxlength="60" />
          </div>

          <label class="switch-row">
            <input v-model="form.skip_tls_verify" type="checkbox" />
            <span class="switch-track"><span /></span>
            <span>
              <strong>跳过目标 TLS 校验</strong>
              <small>仅在内网服务使用自签名 HTTPS 证书时开启。</small>
            </span>
          </label>

          <div class="form-actions">
            <PixelButton variant="primary" type="submit" :loading="saving">
              <Save />
              保存设置
            </PixelButton>
            <span class="save-hint">保存后 Nginx 动态路由会在 1 秒内热加载。</span>
          </div>
        </div>
      </form>

      <div class="side-stack">
        <div class="pixel-panel status-card">
          <div class="panel-head">
            <div>
              <span class="hud-label">GATEWAY STATUS</span>
              <h2>网关状态</h2>
            </div>
          </div>
          <div class="status-body">
            <div class="status-line">
              <span>配置状态</span>
              <StatusLight
                :tone="app.gateway?.synced ? 'online' : 'warn'"
                :label="app.gateway?.synced ? 'SYNCED' : 'PENDING'"
              />
            </div>
            <div class="status-line">
              <span>启用路由</span>
              <strong>{{ app.gateway?.service_count ?? 0 }}</strong>
            </div>
            <div class="status-line">
              <span>最近同步</span>
              <strong>{{ formatRelative(app.gateway?.synced_at) }}</strong>
            </div>
            <div class="status-line column">
              <span>动态配置目录</span>
              <code class="path-code" :title="app.gateway?.hosts_file">{{ app.gateway?.hosts_file || '--' }}</code>
            </div>
            <PixelButton variant="ghost" block :loading="syncing" @click="syncGateway">
              <RefreshCw />
              立即同步路由
            </PixelButton>
          </div>
        </div>

        <div class="pixel-panel security-card">
          <div class="panel-head">
            <div>
              <span class="hud-label">SECURITY</span>
              <h2>账户安全</h2>
            </div>
          </div>
          <div class="security-body">
            <p>修改密码会立即撤销所有已签发的登录令牌，需要重新登录。</p>
            <PixelButton variant="ghost" block @click="router.push({ name: 'profile' })">
              <KeyRound />
              前往修改密码
            </PixelButton>
          </div>
        </div>

        <section class="pixel-panel config-card">
          <div class="panel-head">
            <div>
              <span class="hud-label">GENERATED ROUTING</span>
              <h2>配置预览</h2>
            </div>
            <FileCode2 class="head-icon" />
          </div>
          <div class="config-body">
            <p class="config-hint">生成当前下发给 Nginx 的 Host 与 Path 路由，在弹窗中查看和复制。</p>
            <div class="config-stats">
              <div class="config-stat"><span>HOSTS</span><strong>{{ hostCount }}</strong></div>
              <div class="config-stat"><span>PATHS</span><strong>{{ pathCount }}</strong></div>
            </div>
            <div class="config-actions">
              <PixelButton variant="primary" size="sm" :loading="loadingConfig" @click="openConfigModal">
                <FileCode2 />
                生成并查看
              </PixelButton>
              <PixelButton variant="ghost" size="sm" :disabled="!app.configPreview" @click="copyConfig">
                <Copy />
                复制
              </PixelButton>
            </div>
          </div>
        </section>
      </div>
    </div>

    <div v-if="configModalOpen" class="modal-backdrop" @click.self="configModalOpen = false">
      <div class="pixel-panel config-modal">
        <header class="modal-head">
          <div>
            <span class="hud-label">GENERATED ROUTING</span>
            <h2>配置预览</h2>
          </div>
          <div class="modal-actions">
            <div class="segmented small">
              <button type="button" :class="{ active: activeTab === 'hosts' }" @click="activeTab = 'hosts'">HOSTS</button>
              <button type="button" :class="{ active: activeTab === 'paths' }" @click="activeTab = 'paths'">PATHS</button>
            </div>
            <PixelButton variant="ghost" size="sm" :loading="loadingConfig" @click="loadConfig">
              <RefreshCw />
              重新生成
            </PixelButton>
            <PixelButton variant="ghost" size="sm" @click="copyConfig">
              <Copy />
              复制
            </PixelButton>
            <button class="icon-action" type="button" title="关闭" @click="configModalOpen = false">
              <X />
            </button>
          </div>
        </header>
        <div class="config-modal-body">
          <pre v-if="activeConfig" class="code-block">{{ activeConfig }}</pre>
          <div v-else class="config-empty">还没有生成配置。</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { Copy, FileCode2, KeyRound, RefreshCw, Save, X } from 'lucide-vue-next'
import PixelButton from '@/components/cyber/PixelButton.vue'
import StatusLight from '@/components/common/StatusLight.vue'
import { useAppStore } from '@/stores/app'
import { useServicesStore } from '@/stores/services'
import type { Settings } from '@/types'
import { formatRelative } from '@/utils/format'
import { copyText } from '@/utils/url'

const app = useAppStore()
const services = useServicesStore()
const message = useMessage()
const router = useRouter()

const SCHEMES: Array<'http' | 'https'> = ['http', 'https']
const saving = ref(false)
const syncing = ref(false)
const loadingConfig = ref(false)
const activeTab = ref<'hosts' | 'paths'>('hosts')
const configModalOpen = ref(false)

const form = reactive<Settings>({
  base_domain: 'localhost',
  public_scheme: 'http',
  public_port: '8080',
  health_interval: 20,
  skip_tls_verify: false,
  site_name: '矽励科技服务网关管理系统',
})

const activeConfig = computed(() => {
  if (!app.configPreview) return ''
  return activeTab.value === 'hosts' ? app.configPreview.hosts : app.configPreview.paths
})

const hostCount = computed(() => {
  const text = app.configPreview?.hosts || ''
  return (text.match(/server_name\b/g) || []).length
})

const pathCount = computed(() => {
  const text = app.configPreview?.paths || ''
  return (text.match(/^\s*location\s/gm) || []).length
})

function applySettings(value: Settings): void {
  form.base_domain = value.base_domain
  form.public_scheme = value.public_scheme
  form.public_port = value.public_port
  form.health_interval = value.health_interval
  form.skip_tls_verify = value.skip_tls_verify
  form.site_name = value.site_name
}

function validate(): boolean {
  if (form.public_port && (!/^\d+$/.test(form.public_port) || Number(form.public_port) < 1 || Number(form.public_port) > 65535)) {
    message.error('公网端口必须是 1-65535 的数字，或留空')
    return false
  }
  if (form.health_interval < 5 || form.health_interval > 3600) {
    message.error('健康检查间隔必须在 5-3600 秒之间')
    return false
  }
  if (!form.site_name.trim()) {
    message.error('站点名称不能为空')
    return false
  }
  return true
}

async function save(): Promise<void> {
  if (saving.value || !validate()) return
  saving.value = true
  try {
    const gateway = await app.saveSettings({ ...form })
    await services.fetchAll(true)
    await app.loadInfo()
    if (gateway.synced) {
      message.success('设置已保存，网关路由已重新加载')
    } else {
      message.warning(gateway.message || '设置已保存，但网关同步失败，请手动同步')
    }
  } catch (error) {
    message.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    saving.value = false
  }
}

async function syncGateway(): Promise<void> {
  if (syncing.value) return
  syncing.value = true
  try {
    const result = await app.syncGateway()
    message.success(result.synced ? '路由表已重新下发' : '同步未完成，请检查后端日志')
    if (app.configPreview) await loadConfig()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '同步失败')
  } finally {
    syncing.value = false
  }
}

async function loadConfig(): Promise<void> {
  if (loadingConfig.value) return
  loadingConfig.value = true
  try {
    await app.loadGatewayConfig()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '读取配置失败')
  } finally {
    loadingConfig.value = false
  }
}

async function openConfigModal(): Promise<void> {
  await loadConfig()
  if (app.configPreview) configModalOpen.value = true
}

async function copyConfig(): Promise<void> {
  if (!activeConfig.value) return
  const done = await copyText(activeConfig.value)
  message[done ? 'success' : 'error'](done ? '配置已复制' : '复制失败')
}

watch(
  () => app.settings,
  (value) => {
    if (value) applySettings(value)
  },
  { deep: true },
)

onMounted(async () => {
  try {
    const value = app.settings || (await app.loadSettings())
    applySettings(value)
    if (!app.gateway) await app.loadInfo()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载设置失败')
  }
})
</script>

<style scoped>
.settings-page {
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
}

.page-head p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

.settings-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(310px, 0.75fr);
  gap: 14px;
  align-items: stretch;
}

.settings-card {
  overflow: hidden;
}

.panel-head h2 {
  margin: 2px 0 0;
  font-size: 18px;
}

.settings-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 20px;
}

.field {
  display: flex;
  flex-direction: column;
}

.segmented {
  display: inline-flex;
  width: fit-content;
  padding: 3px;
  border: 1px solid var(--line);
  border-radius: 5px;
  background: rgba(3, 8, 18, 0.6);
}

.segmented button {
  height: 31px;
  padding: 0 17px;
  border: 0;
  border-radius: 3px;
  background: transparent;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 14px;
  letter-spacing: 0.08em;
}

.segmented button.active {
  background: rgba(58, 110, 216, 0.32);
  color: var(--xl-cyan);
}

.segmented.small button {
  height: 26px;
  padding: 0 10px;
  font-size: 12px;
}

.switch-row {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  padding: 13px 14px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: rgba(4, 10, 22, 0.5);
  cursor: pointer;
}

.switch-row input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.switch-track {
  position: relative;
  width: 38px;
  height: 20px;
  flex: 0 0 auto;
  margin-top: 2px;
  border: 1px solid #1b3766;
  border-radius: 3px;
  background: #040a16;
  transition: 0.16s ease;
}

.switch-track span {
  position: absolute;
  left: 2px;
  top: 2px;
  width: 14px;
  height: 14px;
  background: #2f4d7f;
  transition: 0.16s ease;
}

.switch-row input:checked + .switch-track {
  border-color: var(--xl-cyan);
  background: rgba(95, 211, 243, 0.12);
}

.switch-row input:checked + .switch-track span {
  left: 20px;
  background: var(--xl-cyan);
  box-shadow: 0 0 10px rgba(95, 211, 243, 0.7);
}

.switch-row > span:last-child {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.switch-row strong {
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
}

.switch-row small {
  color: var(--text-muted);
  font-size: 11.5px;
  line-height: 1.5;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 13px;
  flex-wrap: wrap;
  padding-top: 2px;
}

.save-hint {
  color: var(--text-muted);
  font-size: 12px;
}

.side-stack {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 100%;
}

.status-body,
.security-body {
  padding: 16px 18px 18px;
}

.status-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 9px 0;
  border-bottom: 1px solid rgba(95, 211, 243, 0.07);
  color: var(--text-muted);
  font-size: 13px;
}

.status-line strong {
  color: var(--text);
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 400;
}

.status-line.column {
  align-items: flex-start;
  flex-direction: column;
  gap: 4px;
}

.path-code {
  display: block;
  max-width: 100%;
  overflow: hidden;
  color: var(--text-dim);
  font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-body :deep(.pixel-btn) {
  margin-top: 14px;
}

.security-body p {
  margin: 0 0 14px;
  color: var(--text-muted);
  font-size: 12.5px;
  line-height: 1.7;
}

.config-card {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 210px;
  overflow: hidden;
}

.config-body {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 18px 18px;
}

.config-hint {
  margin: 0;
  color: var(--text-muted);
  font-size: 12.5px;
  line-height: 1.65;
}

.config-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.config-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(4, 10, 22, 0.5);
}

.config-stat span {
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.16em;
}

.config-stat strong {
  color: var(--xl-cyan);
  font-family: var(--mono);
  font-size: 24px;
  font-weight: 500;
}

.config-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.config-actions :deep(svg) {
  width: 14px;
  height: 14px;
}

.head-icon {
  width: 18px;
  height: 18px;
  color: var(--xl-cyan);
  opacity: 0.85;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(2, 6, 14, 0.76);
  backdrop-filter: blur(4px);
}

.config-modal {
  display: flex;
  flex-direction: column;
  width: min(1020px, 100%);
  max-height: 88vh;
  overflow: hidden;
  padding: 0;
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding: 16px 20px 14px;
  border-bottom: 1px solid var(--line);
}

.modal-head h2 {
  margin: 2px 0 0;
  font-size: 18px;
}

.modal-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.config-modal-body {
  flex: 1 1 auto;
  min-height: 320px;
  overflow: auto;
  scrollbar-gutter: stable;
}

.config-modal-body .code-block {
  margin: 0;
  border: 0;
  border-radius: 0;
  max-height: none;
  overflow: visible;
}

.config-empty {
  padding: 42px 20px;
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
}

@media (max-width: 1080px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }

  .side-stack {
    min-height: 0;
  }
}
</style>
