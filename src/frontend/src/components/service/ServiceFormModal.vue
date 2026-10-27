<template>
  <n-modal
    :show="app.serviceFormOpen"
    :mask-closable="!submitting"
    :auto-focus="false"
    :style="{ width: 'min(720px, calc(100vw - 24px))' }"
    @update:show="handleShow"
  >
    <div class="pixel-panel form-modal">
      <header class="form-head">
        <div>
          <span class="hud-label">{{ editing ? 'EDIT SERVICE' : 'NEW SERVICE' }}</span>
          <h2>{{ editing ? '编辑服务' : '接入新服务' }}</h2>
        </div>
        <button class="icon-action" type="button" title="关闭" @click="close">
          <X />
        </button>
      </header>

      <form class="form-body" @submit.prevent="submit">
        <div class="form-grid">
          <div class="field">
            <label class="pixel-label" for="service-name">服务名称</label>
            <input
              id="service-name"
              v-model="form.name"
              class="pixel-input"
              :class="{ invalid: errors.name }"
              maxlength="80"
              placeholder="例如 Portainer"
              @input="onNameInput"
            />
            <span v-if="errors.name" class="pixel-error">{{ errors.name }}</span>
          </div>

          <div class="field">
            <label class="pixel-label" for="service-slug">服务标识</label>
            <input
              id="service-slug"
              v-model="form.slug"
              class="pixel-input"
              :class="{ invalid: errors.slug }"
              maxlength="32"
              placeholder="portainer"
              @input="onSlugInput"
            />
            <span class="pixel-hint">用于子域名和 /p/ 路径，只能小写字母、数字、中划线。</span>
            <span v-if="errors.slug" class="pixel-error">{{ errors.slug }}</span>
          </div>

          <div class="field full">
            <label class="pixel-label" for="service-entry-path">入口路径（可选）</label>
            <input
              id="service-entry-path"
              v-model="form.entry_path"
              class="pixel-input"
              placeholder="/dashboard"
              @input="clearError('entry_path')"
            />
            <span class="pixel-hint">
              某些应用的 UI 不在根路径，例如 Qdrant 的 Web UI 是 <code>/dashboard</code>。留空表示打开根路径。
            </span>
            <span v-if="errors.entry_path" class="pixel-error">{{ errors.entry_path }}</span>
          </div>

          <div class="field full">
            <label class="pixel-label" for="service-target">目标地址</label>
            <input
              id="service-target"
              v-model="form.target_url"
              class="pixel-input"
              :class="{ invalid: errors.target_url }"
              placeholder="http://host.docker.internal:8181"
              @input="clearError('target_url')"
            />
            <span class="pixel-hint">
              容器服务写容器名和端口；宿主机服务写 host.docker.internal；局域网写 IP。只填协议、主机和端口。
            </span>
            <span v-if="errors.target_url" class="pixel-error">{{ errors.target_url }}</span>
          </div>

          <div class="field full">
            <label class="pixel-label">访问模式</label>
            <div class="mode-grid">
              <button
                v-for="option in MODES"
                :key="option.value"
                class="mode-option"
                :class="{ active: form.mode === option.value }"
                type="button"
                @click="form.mode = option.value"
              >
                <span class="mode-title">{{ option.label }}</span>
                <span class="mode-desc">{{ option.desc }}</span>
              </button>
            </div>
            <label v-if="form.mode !== 'origin'" class="strip-row">
              <input v-model="form.strip_prefix" type="checkbox" />
              <span>
                <strong>网关剥离 /p/&lt;标识&gt; 前缀</strong>
                <small>
                  默认开启：网关剥离前缀，并自动处理应用的根绝对资源、重定向和 Cookie 路径。
                  若应用自身的 base path 就是 <code>/p/&lt;标识&gt;</code>（File Browser <code>-b</code>、
                  code-server <code>--server-base-path</code>），取消勾选，让应用收到完整路径。
                </small>
              </span>
            </label>
            <p v-if="form.mode === 'origin'" class="origin-hint">
              直连模式不生成 <code>/p/</code> 路由，卡片直接打开源站地址。局域网红可用；
              远程访问需要 wstunnel 客户端。客户端会为每个服务自动开一个
              <code>127.0.0.1:181xx</code> 本地入口，卡片上的「本地」按钮在根路径打开应用，
              适合把根路径写死在 JS 里的应用。
            </p>
          </div>

          <div class="field">
            <label class="pixel-label">服务图标</label>
            <div class="icon-grid">
              <button
                v-for="option in ICON_OPTIONS"
                :key="option.value"
                class="icon-option"
                :class="{ active: form.icon === option.value }"
                :title="option.label"
                type="button"
                @click="form.icon = option.value"
              >
                <component :is="resolveServiceIcon(option.value)" />
              </button>
            </div>
          </div>

          <div class="field">
            <label class="pixel-label">主题色</label>
            <div class="color-row">
              <input v-model="form.color" class="color-input" type="color" />
              <div class="swatches">
                <button
                  v-for="color in COLORS"
                  :key="color"
                  class="swatch"
                  :class="{ active: form.color.toLowerCase() === color }"
                  :style="{ background: color }"
                  type="button"
                  @click="form.color = color"
                />
              </div>
            </div>
            <label class="enable-row">
              <input v-model="form.is_enabled" type="checkbox" />
              启用该服务
            </label>
          </div>

          <div class="field full">
            <label class="pixel-label" for="service-desc">描述</label>
            <textarea
              id="service-desc"
              v-model="form.description"
              class="pixel-textarea"
              maxlength="200"
              placeholder="这个服务是做什么的"
            />
          </div>
        </div>

        <footer class="form-foot">
          <button class="pixel-btn ghost" type="button" :disabled="submitting" @click="close">取消</button>
          <PixelButton variant="primary" type="submit" :loading="submitting">
            {{ editing ? '保存修改' : '创建服务' }}
          </PixelButton>
        </footer>
      </form>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { NModal, useMessage } from 'naive-ui'
import { X } from 'lucide-vue-next'
import PixelButton from '@/components/cyber/PixelButton.vue'
import { useAppStore } from '@/stores/app'
import { useServicesStore } from '@/stores/services'
import type { ServiceMode, ServicePayload } from '@/types'
import { ICON_OPTIONS, resolveServiceIcon } from '@/utils/icons'
import { isValidHexColor, isValidSlug, slugify, validateTarget } from '@/utils/validators'

const app = useAppStore()
const services = useServicesStore()
const message = useMessage()

const MODES: Array<{ value: ServiceMode; label: string; desc: string }> = [
  { value: 'auto', label: '智能', desc: '公网自动使用子域名，本地自动使用 *.localhost' },
  { value: 'subdomain', label: '子域名', desc: '兼容性最好，需要 *.<主域名> 泛解析' },
  { value: 'path', label: '路径', desc: '不需要泛域名，部分单页应用可能不兼容' },
  { value: 'origin', label: '直连', desc: '不走网关，卡片直接打开源站；适合写死根路径的应用' },
]

const COLORS = ['#5fd3f3', '#3a6ed8', '#7c5cff', '#ff4fd8', '#8bffb0', '#ffcc66', '#ff5f7e', '#22c55e']

const editing = computed(() => Boolean(app.editingService))
const submitting = ref(false)
const slugTouched = ref(false)

const form = reactive<ServicePayload>({
  name: '',
  slug: '',
  target_url: '',
  entry_path: '',
  strip_prefix: true,
  description: '',
  color: COLORS[0],
  icon: 'server',
  mode: 'auto',
  is_enabled: true,
})

const errors = reactive({
  name: '',
  slug: '',
  target_url: '',
  entry_path: '',
})

function clearErrors(): void {
  errors.name = ''
  errors.slug = ''
  errors.target_url = ''
  errors.entry_path = ''
}

function clearError(key: keyof typeof errors): void {
  errors[key] = ''
}

function resetForm(): void {
  const service = app.editingService
  clearErrors()
  slugTouched.value = false
  if (service) {
    form.name = service.name
    form.slug = service.slug
    form.target_url = service.target_url
    form.entry_path = service.entry_path
    form.strip_prefix = service.strip_prefix
    form.description = service.description
    form.color = service.color
    form.icon = service.icon
    form.mode = service.mode
    form.is_enabled = service.is_enabled
    return
  }
  form.name = ''
  form.slug = ''
  form.target_url = ''
  form.entry_path = ''
  form.strip_prefix = true
  form.description = ''
  form.color = COLORS[0]
  form.icon = 'server'
  form.mode = 'auto'
  form.is_enabled = true
}

function onNameInput(): void {
  if (editing.value || slugTouched.value) return
  form.slug = slugify(form.name)
}

function onSlugInput(): void {
  slugTouched.value = true
  form.slug = form.slug.toLowerCase().replace(/[^a-z0-9-]/g, '')
  clearError('slug')
}

function validate(): boolean {
  clearErrors()
  let valid = true
  if (!form.name.trim()) {
    errors.name = '请填写服务名称'
    valid = false
  }
  if (!isValidSlug(form.slug)) {
    errors.slug = '标识只能包含小写字母、数字和中划线（1-32 位）'
    valid = false
  }
  const targetError = validateTarget(form.target_url)
  if (targetError) {
    errors.target_url = targetError
    valid = false
  }
  const entryPath = form.entry_path.trim()
  if (entryPath && (!entryPath.startsWith('/') || entryPath.startsWith('//') || /[?#\s]/.test(entryPath))) {
    errors.entry_path = '入口路径必须以单个 / 开头，且不能包含查询参数、锚点或空格'
    valid = false
  }
  if (!isValidHexColor(form.color)) {
    form.color = COLORS[0]
  }
  return valid
}

async function submit(): Promise<void> {
  if (!validate() || submitting.value) return
  submitting.value = true
  const payload: ServicePayload = {
    name: form.name.trim(),
    slug: form.slug.trim(),
    target_url: form.target_url.trim(),
    entry_path: form.entry_path.trim(),
    strip_prefix: form.strip_prefix,
    description: form.description.trim(),
    color: form.color,
    icon: form.icon,
    mode: form.mode,
    is_enabled: form.is_enabled,
  }
  try {
    const result = editing.value && app.editingService
      ? await services.update(app.editingService.id, payload)
      : await services.create(payload)
    message.success(editing.value ? '服务已更新，路由已生效' : '服务已创建，路由已生效')
    if (!result.gateway.synced) {
      message.warning(result.gateway.message || '网关配置同步失败，请到系统设置手动同步')
    }
    app.closeServiceForm()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    submitting.value = false
  }
}

function close(): void {
  if (submitting.value) return
  app.closeServiceForm()
}

function handleShow(value: boolean): void {
  if (!value) close()
}

watch(
  () => app.serviceFormOpen,
  (open) => {
    if (open) resetForm()
  },
)
</script>

<style scoped>
.form-modal {
  max-height: min(860px, calc(100vh - 30px));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 0 rgba(3, 6, 13, 0.9), 0 40px 90px rgba(0, 0, 0, 0.55);
}

.form-head {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 19px 22px 15px;
  border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, #0d1d3d 0%, rgba(10, 23, 48, 0.96) 100%);
}

.form-head h2 {
  margin: 3px 0 0;
  color: #f0f7ff;
  font-size: 20px;
}

.form-body {
  padding: 20px 22px 0;
  min-height: 0;
  overflow-y: auto;
  scrollbar-gutter: stable;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 17px;
}

.field {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.field.full {
  grid-column: 1 / -1;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.mode-option {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-height: 82px;
  padding: 11px 12px;
  border: 2px solid #1b3766;
  border-radius: 6px;
  background: rgba(4, 10, 22, 0.72);
  color: var(--text-dim);
  text-align: left;
  transition: 0.16s ease;
}

.mode-option:hover {
  border-color: #2f60c4;
}

.mode-option.active {
  border-color: var(--xl-cyan);
  background: linear-gradient(180deg, rgba(58, 110, 216, 0.24), rgba(4, 10, 22, 0.8));
  box-shadow: inset 0 0 20px rgba(95, 211, 243, 0.06);
}

.mode-title {
  color: #eaf4ff;
  font-family: var(--mono);
  font-size: 17px;
  letter-spacing: 0.06em;
}

.mode-desc {
  color: var(--text-muted);
  font-size: 11.5px;
  line-height: 1.45;
}

.strip-row {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin-top: 11px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: rgba(4, 10, 22, 0.55);
  color: var(--text-dim);
  font-size: 12px;
  line-height: 1.55;
  cursor: pointer;
}

.strip-row input {
  width: 16px;
  height: 16px;
  margin-top: 2px;
  flex: 0 0 auto;
  accent-color: var(--xl-cyan);
}

.strip-row > span {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.strip-row strong {
  color: var(--text);
  font-size: 12.5px;
}

.strip-row small {
  color: var(--text-muted);
  font-size: 11.5px;
}

.strip-row code {
  color: var(--xl-cyan);
  font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 11px;
}

.origin-hint {
  margin: 10px 0 0;
  padding: 9px 11px;
  border: 1px dashed var(--line);
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 11.5px;
  line-height: 1.55;
}

.origin-hint code {
  color: var(--xl-cyan);
  font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 11px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 6px;
}

.icon-option {
  display: grid;
  place-items: center;
  height: 38px;
  border: 1px solid var(--line);
  border-radius: 5px;
  background: rgba(4, 10, 22, 0.72);
  color: var(--text-muted);
  transition: 0.16s ease;
}

.icon-option:hover {
  color: var(--text);
  border-color: var(--line-strong);
}

.icon-option.active {
  color: var(--xl-cyan);
  border-color: var(--xl-cyan);
  background: rgba(95, 211, 243, 0.1);
  box-shadow: 0 0 18px rgba(95, 211, 243, 0.08);
}

.icon-option svg {
  width: 17px;
  height: 17px;
}

.color-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-input {
  width: 44px;
  height: 40px;
  padding: 3px;
  border: 1px solid var(--line);
  border-radius: 5px;
  background: rgba(4, 10, 22, 0.8);
}

.swatches {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.swatch {
  width: 21px;
  height: 21px;
  border: 2px solid transparent;
  border-radius: 3px;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.5);
}

.swatch.active {
  border-color: #fff;
  box-shadow: 0 0 12px currentColor;
}

.enable-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  color: var(--text-dim);
  font-size: 13px;
  cursor: pointer;
}

.enable-row input {
  width: 16px;
  height: 16px;
  accent-color: var(--xl-cyan);
}

.form-foot {
  position: sticky;
  bottom: 0;
  display: flex;
  justify-content: flex-end;
  gap: 9px;
  margin-top: 20px;
  padding: 15px 0 18px;
  border-top: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(10, 23, 48, 0.9), #0a1730 45%);
}

@media (max-width: 680px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .mode-grid {
    grid-template-columns: 1fr;
  }

  .icon-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}
</style>
