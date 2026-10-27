<template>
  <div class="error-page">
    <div class="pixel-panel error-card">
      <img class="error-bot" src="@/assets/brand/robot.png" alt="XILI-AI" />
      <GlitchText text="ACCESS DENIED" tag="h1" class="error-title" />
      <span class="hud-label">403 // CLEARANCE REQUIRED</span>
      <p>当前操作员没有访问该区域的权限。请联系管理员提升权限，或返回控制台。</p>
      <PixelButton variant="primary" @click="router.push({ name: 'dashboard' })">
        返回控制台
      </PixelButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import GlitchText from '@/components/cyber/GlitchText.vue'
import PixelButton from '@/components/cyber/PixelButton.vue'

const router = useRouter()
</script>

<style scoped>
.error-page {
  display: grid;
  place-items: center;
  min-height: calc(100vh - var(--header-height) - 80px);
}

.error-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: min(560px, 100%);
  padding: 36px 32px;
  text-align: center;
}

.error-bot {
  width: 94px;
  height: 94px;
  object-fit: contain;
  image-rendering: pixelated;
  opacity: 0.9;
  animation: float-soft 5s ease-in-out infinite;
}

.error-title {
  margin: 4px 0 0;
  font-family: var(--pixel);
  font-size: clamp(20px, 3vw, 30px);
  color: #fff;
}

.error-card p {
  max-width: 400px;
  margin: 0 0 10px;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.8;
}
</style>
