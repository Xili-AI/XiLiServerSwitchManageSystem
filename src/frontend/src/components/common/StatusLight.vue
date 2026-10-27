<template>
  <span class="status-pill" :class="{ pulse }">
    <span class="led" :class="tone" />
    <span v-if="label" class="status-text">{{ label }}</span>
  </span>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    tone?: 'online' | 'offline' | 'warn'
    label?: string
    pulse?: boolean
  }>(),
  { tone: 'warn', label: '', pulse: false },
)
</script>

<style scoped>
.status-pill {
  line-height: 1;
}

.status-text {
  font-family: var(--mono);
  letter-spacing: 0.06em;
  white-space: nowrap;
}

.pulse .led {
  animation: status-pulse 1.9s ease-in-out infinite;
}

@keyframes status-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.35;
  }
}
</style>
