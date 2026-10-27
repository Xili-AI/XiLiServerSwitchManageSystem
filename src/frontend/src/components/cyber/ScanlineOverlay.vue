<template>
  <div class="scanline-wrap" aria-hidden="true">
    <div class="scanlines" :style="{ opacity: subtle ? 0.3 : 0.55 }" />
    <div class="crt-vignette" :style="{ opacity: subtle ? 0.6 : 1 }" />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ subtle?: boolean }>(), { subtle: false })
</script>

<style scoped>
.scanline-wrap {
  position: fixed;
  inset: 0;
  z-index: 59;
  pointer-events: none;
}
</style>
