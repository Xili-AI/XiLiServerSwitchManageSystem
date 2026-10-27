<template>
  <component :is="tag" class="glitch" :data-text="text">{{ text }}</component>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    text: string
    tag?: string
  }>(),
  { tag: 'span' },
)
</script>
