<template>
  <section
    class="pixel-panel"
    :class="{ hoverable, inset }"
    :style="{ '--panel-accent': accent }"
  >
    <slot />
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    accent?: string
    hoverable?: boolean
    inset?: boolean
  }>(),
  { accent: '#5fd3f3', hoverable: false, inset: false },
)
</script>
