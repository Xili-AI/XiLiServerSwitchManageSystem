<template>
  <div class="stat-card pixel-panel hoverable" :style="{ '--stat-accent': accent }">
    <div class="stat-head">
      <span class="hud-label">{{ label }}</span>
      <span class="stat-icon">
        <component :is="icon" />
      </span>
    </div>
    <div class="stat-value">
      <span>{{ displayValue }}</span>
      <small v-if="suffix">{{ suffix }}</small>
    </div>
    <div class="stat-hint">{{ hint }}</div>
    <div class="stat-meter">
      <span :style="{ width: meterWidth }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, type Component } from 'vue'
import gsap from 'gsap'

const props = withDefaults(
  defineProps<{
    label: string
    value: number | string
    suffix?: string
    icon: Component
    accent?: string
    hint?: string
    meter?: number
  }>(),
  {
    suffix: '',
    accent: '#5fd3f3',
    hint: '',
    meter: 0.68,
  },
)

const animated = ref(0)
const isNumeric = computed(() => typeof props.value === 'number')

const displayValue = computed(() => {
  if (!isNumeric.value) return props.value
  return new Intl.NumberFormat('zh-CN').format(Math.round(animated.value))
})

const meterWidth = computed(() => `${Math.min(100, Math.max(4, props.meter * 100))}%`)

function animateTo(value: number): void {
  const state = { value: animated.value }
  gsap.to(state, {
    value,
    duration: 0.8,
    ease: 'power2.out',
    onUpdate: () => {
      animated.value = state.value
    },
  })
}

onMounted(() => {
  if (isNumeric.value) animateTo(Number(props.value))
})

watch(
  () => props.value,
  (value) => {
    if (typeof value === 'number') animateTo(value)
  },
)
</script>

<style scoped>
.stat-card {
  position: relative;
  padding: 16px 18px 15px;
  overflow: hidden;
}

.stat-card::before {
  border-color: var(--stat-accent);
}

.stat-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border: 1px solid color-mix(in srgb, var(--stat-accent) 42%, transparent);
  border-radius: 6px;
  background: color-mix(in srgb, var(--stat-accent) 10%, transparent);
  color: var(--stat-accent);
}

.stat-icon :deep(svg) {
  width: 17px;
  height: 17px;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-top: 10px;
  font-family: var(--mono);
  font-size: 43px;
  line-height: 1;
  color: #f2f8ff;
  text-shadow: 0 0 24px color-mix(in srgb, var(--stat-accent) 25%, transparent);
}

.stat-value small {
  font-size: 17px;
  color: var(--text-muted);
  text-shadow: none;
}

.stat-hint {
  margin-top: 5px;
  color: var(--text-muted);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-meter {
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 8px;
  height: 2px;
  background: rgba(95, 211, 243, 0.08);
}

.stat-meter span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--stat-accent), transparent);
  box-shadow: 0 0 10px color-mix(in srgb, var(--stat-accent) 55%, transparent);
  transition: width 0.6s ease;
}
</style>
