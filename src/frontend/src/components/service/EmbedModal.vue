<template>
  <n-modal
    :show="Boolean(app.embedService)"
    :auto-focus="false"
    :style="{ width: 'min(1240px, calc(100vw - 20px))' }"
    @update:show="handleShow"
  >
    <div class="pixel-panel embed-shell">
      <header class="embed-head">
        <div class="embed-title">
          <span class="hud-label">EMBEDDED SESSION</span>
          <strong>{{ app.embedService?.name || '服务' }}</strong>
          <span class="embed-url">{{ embedUrl }}</span>
        </div>
        <div class="embed-actions">
          <a class="pixel-btn ghost sm" :href="embedUrl" target="_blank" rel="noopener noreferrer">
            <ExternalLink />
            新标签打开
          </a>
          <button class="icon-action" type="button" title="关闭" @click="close">
            <X />
          </button>
        </div>
      </header>

      <div class="embed-body">
        <div v-if="loading" class="embed-loading">
          <span class="embed-loader" />
          正在建立服务会话...
        </div>
        <iframe
          :key="app.embedService?.id || 'empty'"
          :src="embedUrl"
          class="embed-frame"
          title="服务预览"
          referrerpolicy="no-referrer"
          allow="clipboard-read; clipboard-write; fullscreen"
          @load="loading = false"
        />
      </div>

      <footer class="embed-foot">
        如果页面空白或提示拒绝连接，说明该服务禁止被嵌入，请点击「新标签打开」。
      </footer>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { NModal } from 'naive-ui'
import { ExternalLink, X } from 'lucide-vue-next'
import { useAppStore } from '@/stores/app'
import { buildServiceUrl } from '@/utils/url'

const app = useAppStore()
const loading = ref(true)

const embedUrl = computed(() => {
  if (!app.embedService) return 'about:blank'
  return buildServiceUrl(app.embedService, app.settings)
})

watch(
  () => app.embedService,
  (service) => {
    if (service) loading.value = true
  },
)

function close(): void {
  app.closeEmbed()
}

function handleShow(value: boolean): void {
  if (!value) close()
}
</script>

<style scoped>
.embed-shell {
  display: flex;
  flex-direction: column;
  height: min(840px, calc(100vh - 28px));
  overflow: hidden;
  box-shadow: 0 10px 0 rgba(3, 6, 13, 0.9), 0 40px 90px rgba(0, 0, 0, 0.55);
}

.embed-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, #0d1d3d, rgba(10, 23, 48, 0.96));
}

.embed-title {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 1px;
}

.embed-title strong {
  overflow: hidden;
  color: #f0f7ff;
  font-size: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.embed-url {
  overflow: hidden;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.embed-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}

.embed-actions svg {
  width: 14px;
  height: 14px;
}

.embed-body {
  position: relative;
  flex: 1;
  background: #fff;
}

.embed-frame {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}

.embed-loading {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  background: #071022;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 15px;
  letter-spacing: 0.06em;
}

.embed-loader {
  width: 44px;
  height: 44px;
  border: 2px dashed rgba(95, 211, 243, 0.35);
  border-top-color: var(--xl-cyan);
  border-radius: 50%;
  animation: spin 1.1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.embed-foot {
  padding: 8px 16px;
  border-top: 1px solid var(--line);
  color: var(--text-muted);
  font-size: 11.5px;
}
</style>
