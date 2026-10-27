<template>
  <div class="empty-state pixel-panel inset">
    <div class="empty-grid" />
    <img class="empty-bot" src="@/assets/brand/robot.png" alt="XILI-AI" />
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <PixelButton v-if="actionLabel" variant="primary" @click="$emit('action')">
      <Plus />
      {{ actionLabel }}
    </PixelButton>
  </div>
</template>

<script setup lang="ts">
import { Plus } from 'lucide-vue-next'
import PixelButton from '@/components/cyber/PixelButton.vue'

withDefaults(
  defineProps<{
    title: string
    description: string
    actionLabel?: string
  }>(),
  { actionLabel: '' },
)

defineEmits<{ (event: 'action'): void }>()
</script>

<style scoped>
.empty-state {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 330px;
  padding: 32px 24px;
  overflow: hidden;
  text-align: center;
}

.empty-grid {
  position: absolute;
  inset: 0;
  background-image:
    repeating-linear-gradient(0deg, rgba(95, 211, 243, 0.06) 0 1px, transparent 1px 34px),
    repeating-linear-gradient(90deg, rgba(95, 211, 243, 0.06) 0 1px, transparent 1px 34px);
  mask-image: radial-gradient(circle at 50% 40%, #000, transparent 72%);
  pointer-events: none;
}

.empty-bot {
  position: relative;
  width: 96px;
  height: 96px;
  object-fit: contain;
  image-rendering: pixelated;
  opacity: 0.9;
  animation: float-soft 5.5s ease-in-out infinite;
  filter: drop-shadow(0 0 20px rgba(95, 211, 243, 0.22));
}

.empty-state h3 {
  position: relative;
  margin: 6px 0 0;
  color: #eaf4ff;
  font-size: 18px;
}

.empty-state p {
  position: relative;
  max-width: 520px;
  margin: 0 0 12px;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.7;
}
</style>
