<template>
  <article
    class="service-card pixel-panel hoverable"
    :class="{ disabled: !service.is_enabled }"
    :style="{ '--card-accent': service.color }"
  >
    <span class="accent-line" />
    <header class="service-head">
      <div class="icon-tile" :style="{ '--tile-accent': service.color }">
        <component :is="iconComponent" />
      </div>
      <div class="service-title">
        <h3 :title="service.name">{{ service.name }}</h3>
        <span class="service-slug">/{{ service.slug }}</span>
      </div>
      <StatusLight
        class="service-status"
        :tone="tone"
        :label="statusText"
        :pulse="service.is_enabled && service.is_online === null"
      />
    </header>

    <p class="service-desc">{{ service.description || '暂无描述' }}</p>

    <div class="service-meta">
      <div class="meta-line">
        <span class="hud-label">TARGET</span>
        <code class="code-chip" :title="service.target_url">{{ service.target_url }}</code>
      </div>
      <div class="meta-line">
        <span class="hud-label">ENTRY</span>
        <code class="code-chip entry" :title="url">{{ url }}</code>
        <button class="copy-btn" type="button" title="复制入口地址" @click="copyEntry">
          <Check v-if="copied" />
          <Copy v-else />
        </button>
      </div>
    </div>

    <div class="service-tags">
      <span class="pixel-tag">{{ mode }}</span>
      <span v-if="service.latency_ms !== null && service.is_online" class="pixel-tag lime">
        {{ formatLatency(service.latency_ms) }}
      </span>
      <span v-if="!service.is_enabled" class="pixel-tag red">已停用</span>
      <span v-if="service.last_error && service.is_online === false" class="pixel-tag amber" :title="service.last_error">
        连接异常
      </span>
    </div>

    <footer class="service-actions">
      <div class="primary-actions">
        <a
          class="pixel-btn primary sm"
          :href="url"
          :target="isOrigin ? '_blank' : '_self'"
          :rel="isOrigin ? 'noreferrer' : undefined"
        >
          <ExternalLink />
          打开
        </a>
        <a
          v-if="service.local_port"
          class="pixel-btn ghost sm"
          :href="`http://127.0.0.1:${service.local_port}/`"
          target="_blank"
          rel="noreferrer"
          title="本机入口：应用在根路径打开，需要 tunnel-client 正在运行"
        >
          <ExternalLink />
          本地
        </a>
        <PixelButton v-if="auth.isAdmin" size="sm" variant="ghost" @click="$emit('embed', service)">
          <PanelTop />
          嵌入
        </PixelButton>
      </div>
      <div v-if="auth.isAdmin" class="icon-actions">
        <button class="icon-action" type="button" title="立即检测" @click="$emit('check', service)">
          <RefreshCw />
        </button>
        <button class="icon-action" type="button" title="编辑" @click="$emit('edit', service)">
          <Pencil />
        </button>
        <button class="icon-action danger" type="button" title="删除" @click="$emit('delete', service)">
          <Trash2 />
        </button>
      </div>
    </footer>
  </article>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  Check,
  Copy,
  ExternalLink,
  PanelTop,
  Pencil,
  RefreshCw,
  Trash2,
} from 'lucide-vue-next'
import type { Service, Settings } from '@/types'
import { resolveServiceIcon } from '@/utils/icons'
import { buildServiceUrl, copyText, modeLabel, statusLabel, statusTone } from '@/utils/url'
import { formatLatency } from '@/utils/format'
import StatusLight from '@/components/common/StatusLight.vue'
import PixelButton from '@/components/cyber/PixelButton.vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  service: Service
  settings: Settings | null
}>()

defineEmits<{
  (event: 'edit', service: Service): void
  (event: 'delete', service: Service): void
  (event: 'embed', service: Service): void
  (event: 'check', service: Service): void
}>()

const copied = ref(false)
const iconComponent = computed(() => resolveServiceIcon(props.service.icon))
const auth = useAuthStore()
const url = computed(() => buildServiceUrl(props.service, props.settings))
const mode = computed(() => modeLabel(props.service))
const isOrigin = computed(() => props.service.mode === 'origin')
const statusText = computed(() => statusLabel(props.service))
const tone = computed(() => statusTone(props.service))

async function copyEntry(): Promise<void> {
  const done = await copyText(url.value)
  if (!done) return
  copied.value = true
  window.setTimeout(() => {
    copied.value = false
  }, 1600)
}
</script>

<style scoped>
.service-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 13px;
  min-height: 288px;
  padding: 19px 19px 16px;
  overflow: hidden;
}

.service-card::before {
  border-color: var(--card-accent);
}

.service-card.disabled {
  opacity: 0.58;
}

.accent-line {
  position: absolute;
  inset: 0 0 auto 0;
  height: 2px;
  background: linear-gradient(90deg, var(--card-accent), transparent 78%);
  opacity: 0.9;
}

.service-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.service-title {
  min-width: 0;
  flex: 1;
  padding-top: 2px;
}

.service-title h3 {
  margin: 0;
  overflow: hidden;
  color: #f0f7ff;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.service-slug {
  display: block;
  margin-top: 2px;
  overflow: hidden;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 13px;
  letter-spacing: 0.06em;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.service-status {
  flex: 0 0 auto;
  margin-top: 2px;
}

.service-desc {
  min-height: 38px;
  margin: 0;
  overflow: hidden;
  color: var(--text-dim);
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.service-meta {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.meta-line {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.meta-line .hud-label {
  flex: 0 0 48px;
  font-size: 12px;
}

.code-chip {
  min-width: 0;
  flex: 1;
}

.code-chip.entry {
  color: var(--xl-cyan);
}

.copy-btn {
  display: grid;
  place-items: center;
  width: 25px;
  height: 25px;
  flex: 0 0 auto;
  border: 1px solid var(--line);
  border-radius: 4px;
  background: rgba(4, 10, 22, 0.72);
  color: var(--text-muted);
  transition: 0.16s ease;
}

.copy-btn:hover {
  color: var(--xl-cyan);
  border-color: var(--line-strong);
}

.copy-btn :deep(svg) {
  width: 12px;
  height: 12px;
}

.service-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.service-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid rgba(95, 211, 243, 0.08);
}

.primary-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.icon-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
}

.service-actions :deep(svg) {
  width: 15px;
  height: 15px;
}
</style>
