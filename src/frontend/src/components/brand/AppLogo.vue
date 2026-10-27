<template>
  <router-link to="/" class="app-logo" :class="[`size-${size}`, { compact }]" aria-label="矽励科技服务网关管理系统 首页">
    <img
      class="logo-image"
      :src="compact ? robot : logo"
      :alt="compact ? 'XILI-AI' : 'XILI-AI wordmark'"
    />
    <span v-if="!compact" class="logo-product">
      <span class="logo-name">XILI GATEWAY</span>
      <span class="logo-sub">SINGLE TUNNEL GATEWAY</span>
    </span>
  </router-link>
</template>

<script setup lang="ts">
import logo from '@/assets/brand/logo.png'
import robot from '@/assets/brand/robot.png'

withDefaults(
  defineProps<{
    compact?: boolean
    size?: 'sm' | 'md' | 'lg'
  }>(),
  { compact: false, size: 'md' },
)
</script>

<style scoped>
.app-logo {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  color: inherit;
  text-decoration: none;
}

.logo-image {
  display: block;
  width: auto;
  height: 22px;
  image-rendering: pixelated;
  filter: drop-shadow(0 0 14px rgba(95, 211, 243, 0.18));
}

.size-sm .logo-image {
  height: 18px;
}

.size-lg .logo-image {
  height: 30px;
}

.compact .logo-image {
  width: 46px;
  height: 46px;
  object-fit: contain;
}

.logo-product {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.logo-name {
  font-family: var(--pixel);
  font-size: 10px;
  letter-spacing: 0.14em;
  color: #eaf4ff;
  text-shadow: 0 0 18px rgba(95, 211, 243, 0.35);
  white-space: nowrap;
}

.logo-sub {
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.14em;
  color: var(--text-muted);
  white-space: nowrap;
}
</style>
