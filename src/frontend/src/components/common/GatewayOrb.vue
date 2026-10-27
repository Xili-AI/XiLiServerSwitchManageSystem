<template>
  <div class="orb-wrap">
    <div class="orb-aura" />
    <div class="orb-stars" />
    <div class="orb-ticks" />
    <span class="orb-plus p1">+</span>
    <span class="orb-plus p2">+</span>
    <span class="orb-plus p3">+</span>

    <div class="orb-grid" />
    <div class="orb-crosshair" />
    <div class="orb-ring ring-outer" />
    <div class="orb-ring ring-mid" />
    <div class="orb-ring ring-inner" />
    <div class="orb-sweep" />

    <div class="orb-legend">
      <span><i class="online" />{{ onlineCount }}</span>
      <span><i class="offline" />{{ offlineCount }}</span>
    </div>

    <div class="orb-core">
      <div class="orb-core-glow" />
      <img class="orb-bot" src="@/assets/brand/robot.png" alt="XILI-AI robot" />
    </div>

    <div
      v-for="(node, index) in nodes"
      :key="node.id"
      class="orb-node"
      :style="nodeStyle(index)"
    >
      <span class="node-dot" :class="statusClass(node)">
        <span v-if="node.is_online === true" class="node-pulse" />
      </span>
      <span class="node-name">{{ node.name }}</span>
    </div>

    <div v-if="!nodes.length" class="orb-empty hud-label">NO SERVICES ROUTED</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Service } from '@/types'

const props = defineProps<{
  services: Service[]
  synced: boolean
}>()

const enabled = computed(() => props.services.filter((service) => service.is_enabled))
const nodes = computed(() => enabled.value.slice(0, 6))
const onlineCount = computed(
  () => enabled.value.filter((service) => service.is_online === true).length,
)
const offlineCount = computed(
  () => enabled.value.filter((service) => service.is_online === false).length,
)

function statusClass(node: Service): string {
  if (node.is_online === true) return 'online'
  if (node.is_online === false) return 'offline'
  return 'warn'
}

const SCAN_PERIOD = 7.5

function nodeStyle(index: number): Record<string, string> {
  const count = nodes.value.length || 1
  const angle = -90 + (360 / count) * index
  const normalized = ((angle % 360) + 360) % 360
  const delay = (normalized / 360) * SCAN_PERIOD
  return {
    '--angle': `${angle}deg`,
    '--radius': '124px',
    '--delay': `${delay.toFixed(2)}s`,
  }
}
</script>

<style scoped>
.orb-wrap {
  position: relative;
  width: 340px;
  height: 340px;
  flex: 0 0 auto;
}

.orb-aura {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 430px;
  height: 430px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(95, 211, 243, 0.1) 0%,
    rgba(58, 110, 216, 0.06) 38%,
    transparent 68%
  );
  animation: orb-aura 6.4s ease-in-out infinite;
  pointer-events: none;
}

@keyframes orb-aura {
  0%,
  100% {
    opacity: 0.45;
    transform: translate(-50%, -50%) scale(0.94);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.06);
  }
}

.orb-stars {
  position: absolute;
  inset: -30px;
  pointer-events: none;
  background-image:
    radial-gradient(1.5px 1.5px at 18% 24%, rgba(190, 248, 255, 0.8), transparent 60%),
    radial-gradient(1px 1px at 72% 18%, rgba(95, 211, 243, 0.7), transparent 60%),
    radial-gradient(1.5px 1.5px at 86% 62%, rgba(124, 92, 255, 0.7), transparent 60%),
    radial-gradient(1px 1px at 32% 78%, rgba(190, 248, 255, 0.6), transparent 60%),
    radial-gradient(1px 1px at 58% 88%, rgba(95, 211, 243, 0.55), transparent 60%),
    radial-gradient(1.5px 1.5px at 48% 8%, rgba(95, 211, 243, 0.6), transparent 60%);
  animation: orb-drift 18s ease-in-out infinite alternate;
}

@keyframes orb-drift {
  from {
    transform: translate3d(-6px, 4px, 0);
  }
  to {
    transform: translate3d(8px, -6px, 0);
  }
}

.orb-ticks {
  position: absolute;
  inset: 20px;
  border-radius: 50%;
  opacity: 0.55;
  background: repeating-conic-gradient(
    from 0deg,
    rgba(95, 211, 243, 0.32) 0deg 0.7deg,
    transparent 0.7deg 6deg
  );
  -webkit-mask-image: radial-gradient(circle, transparent 0 97%, #000 97.6% 100%);
  mask-image: radial-gradient(circle, transparent 0 97%, #000 97.6% 100%);
  animation: ring-spin 40s linear infinite;
  pointer-events: none;
}

.orb-plus {
  position: absolute;
  color: rgba(95, 211, 243, 0.5);
  font-family: var(--mono);
  font-size: 12px;
  pointer-events: none;
  animation: orb-float 6s ease-in-out infinite;
}

.orb-plus.p1 {
  top: 8%;
  left: 14%;
  animation-delay: -1s;
}

.orb-plus.p2 {
  top: 26%;
  right: 6%;
  animation-delay: -3s;
}

.orb-plus.p3 {
  bottom: 10%;
  left: 24%;
  animation-delay: -4.5s;
}

@keyframes orb-float {
  0%,
  100% {
    opacity: 0.2;
    transform: translateY(0);
  }
  50% {
    opacity: 0.9;
    transform: translateY(-6px);
  }
}

.orb-grid {
  position: absolute;
  inset: 20px;
  overflow: hidden;
  border-radius: 50%;
  background-image:
    repeating-linear-gradient(0deg, rgba(95, 211, 243, 0.06) 0 1px, transparent 1px 34px),
    repeating-linear-gradient(90deg, rgba(95, 211, 243, 0.06) 0 1px, transparent 1px 34px);
  -webkit-mask-image: radial-gradient(circle, #000 0 68%, transparent 72%);
  mask-image: radial-gradient(circle, #000 0 68%, transparent 72%);
}

.orb-crosshair {
  position: absolute;
  inset: 20px;
  overflow: hidden;
  border-radius: 50%;
  opacity: 0.55;
  background:
    linear-gradient(90deg, transparent calc(50% - 0.5px), rgba(95, 211, 243, 0.22) 50%, transparent calc(50% + 0.5px)),
    linear-gradient(0deg, transparent calc(50% - 0.5px), rgba(95, 211, 243, 0.22) 50%, transparent calc(50% + 0.5px));
  pointer-events: none;
}

.orb-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}


.ring-outer {
  width: 300px;
  height: 300px;
  border: 1px solid rgba(95, 211, 243, 0.14);
  box-shadow: 0 0 40px rgba(95, 211, 243, 0.05), inset 0 0 40px rgba(95, 211, 243, 0.03);
}

.ring-mid {
  width: 236px;
  height: 236px;
  border: 1px dashed rgba(124, 92, 255, 0.26);
}

.ring-inner {
  width: 176px;
  height: 176px;
  border: 1px solid rgba(95, 211, 243, 0.2);
}


/* Soft radar beam: starts at zero alpha so there is no hard white leading edge. */
.orb-sweep {
  position: absolute;
  inset: 20px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    rgba(95, 211, 243, 0) 0deg,
    rgba(95, 211, 243, 0.14) 26deg,
    rgba(95, 211, 243, 0.05) 68deg,
    rgba(95, 211, 243, 0) 108deg,
    rgba(95, 211, 243, 0) 360deg
  );
  -webkit-mask-image: radial-gradient(circle, transparent 0 30%, #000 32% 92%, transparent 98% 100%);
  mask-image: radial-gradient(circle, transparent 0 30%, #000 32% 92%, transparent 98% 100%);
  animation: ring-spin 7.5s linear infinite;
  pointer-events: none;
}

.orb-core {
  position: absolute;
  left: 50%;
  top: 50%;
  display: grid;
  place-items: center;
  width: 132px;
  height: 132px;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(95, 211, 243, 0.38);
  border-radius: 50%;
  background: radial-gradient(circle at 50% 40%, #102651, #050b17 70%);
  box-shadow: 0 0 40px rgba(95, 211, 243, 0.16), inset 0 0 36px rgba(95, 211, 243, 0.08);
}

.orb-core-glow {
  position: absolute;
  inset: -18px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(95, 211, 243, 0.12), transparent 68%);
  animation: pulse-glow 3.6s ease-in-out infinite;
}

.orb-bot {
  position: relative;
  z-index: 1;
  width: 102px;
  height: 102px;
  object-fit: contain;
  image-rendering: pixelated;
  filter: drop-shadow(0 0 16px rgba(95, 211, 243, 0.35));
  animation: float-soft 5s ease-in-out infinite;
}

.orb-node {
  position: absolute;
  left: 50%;
  top: 50%;
  display: flex;
  opacity: 0;
  animation: node-scan 7.5s linear infinite;
  animation-delay: var(--delay, 0s);
  align-items: center;
  gap: 6px;
  transform: translate(-50%, -50%) rotate(var(--angle)) translateX(var(--radius))
    rotate(calc(-1 * var(--angle)));
  padding: 4px 7px;
  border: 1px solid rgba(95, 211, 243, 0.16);
  border-radius: 4px;
  background: rgba(5, 12, 26, 0.86);
  box-shadow: 0 4px 0 rgba(3, 6, 13, 0.7);
  white-space: nowrap;
}

@keyframes node-scan {
  0% {
    opacity: 0;
    filter: brightness(2.2) blur(1px);
  }
  5% {
    opacity: 1;
    filter: brightness(1.6);
  }
  10% {
    opacity: 1;
    filter: brightness(1);
  }
  20% {
    opacity: 1;
  }
  30% {
    opacity: 0;
  }
  100% {
    opacity: 0;
  }
}

.node-dot {
  position: relative;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-muted);
}

.node-dot.online {
  color: rgba(139, 255, 176, 0.8);
  background: var(--xl-lime);
  box-shadow: 0 0 8px rgba(139, 255, 176, 0.8);
}

.node-dot.offline {
  color: rgba(255, 95, 126, 0.75);
  background: var(--xl-red);
  box-shadow: 0 0 8px rgba(255, 95, 126, 0.7);
}

.node-dot.warn {
  background: var(--xl-amber);
  box-shadow: 0 0 8px rgba(255, 204, 102, 0.7);
}

.node-pulse {
  position: absolute;
  inset: -4px;
  border: 1px solid currentColor;
  border-radius: 50%;
  animation: node-ping 2.6s ease-out infinite;
}

@keyframes node-ping {
  0% {
    opacity: 0.7;
    transform: scale(0.6);
  }
  80%,
  100% {
    opacity: 0;
    transform: scale(1.9);
  }
}

.node-name {
  max-width: 76px;
  overflow: hidden;
  color: var(--text-dim);
  font-family: var(--mono);
  font-size: 13px;
  text-overflow: ellipsis;
}

.orb-legend {
  position: absolute;
  top: 6px;
  right: 2px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.08em;
}

.orb-legend i {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-right: 5px;
  border-radius: 50%;
}

.orb-legend i.online {
  background: var(--xl-lime);
  box-shadow: 0 0 8px rgba(139, 255, 176, 0.8);
}

.orb-legend i.offline {
  background: var(--xl-red);
  box-shadow: 0 0 8px rgba(255, 95, 126, 0.8);
}

.orb-empty {
  position: absolute;
  left: 50%;
  top: 78%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 12px;
}

@media (max-width: 1100px) {
  .orb-wrap {
    transform: scale(0.86);
    margin: -18px 0;
  }
}

@media (max-width: 760px) {
  .orb-wrap {
    transform: scale(0.68);
    margin: -48px 0;
  }

  .node-name {
    display: none;
  }

  .orb-aura {
    width: 360px;
    height: 360px;
  }

  .orb-stars {
    opacity: 0.6;
  }

  .orb-ticks {
    opacity: 0.32;
  }
}

@media (prefers-reduced-motion: reduce) {
  .orb-sweep,
  .node-pulse,
  .orb-core-glow,
  .orb-bot,
  .orb-aura,
  .orb-stars,
  .orb-ticks,
  .orb-plus {
    animation: none !important;
  }

  .orb-node {
    opacity: 1;
    animation: none;
  }
}
</style>
