<template>
  <button
    class="pixel-btn"
    :class="[variant, size, { block, icon: iconOnly }]"
    :type="type"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="btn-loader" aria-hidden="true">
      <i /><i /><i />
    </span>
    <slot v-else />
  </button>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'default' | 'primary' | 'ghost' | 'danger'
    size?: 'sm' | 'md' | 'lg'
    type?: 'button' | 'submit' | 'reset'
    loading?: boolean
    disabled?: boolean
    block?: boolean
    iconOnly?: boolean
  }>(),
  {
    variant: 'default',
    size: 'md',
    type: 'button',
    loading: false,
    disabled: false,
    block: false,
    iconOnly: false,
  },
)

defineEmits<{ (event: 'click', value: MouseEvent): void }>()
</script>

<style scoped>
.pixel-btn.block {
  width: 100%;
}

.btn-loader {
  display: inline-flex;
  align-items: flex-end;
  gap: 3px;
  height: 16px;
}

.btn-loader i {
  display: block;
  width: 5px;
  height: 5px;
  background: currentColor;
  animation: btn-bounce 0.9s ease-in-out infinite;
}

.btn-loader i:nth-child(2) {
  animation-delay: 0.12s;
}

.btn-loader i:nth-child(3) {
  animation-delay: 0.24s;
}

@keyframes btn-bounce {
  0%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  50% {
    transform: translateY(-6px);
    opacity: 1;
  }
}
</style>
