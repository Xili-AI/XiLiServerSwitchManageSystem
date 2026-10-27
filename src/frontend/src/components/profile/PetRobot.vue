<template>
  <div class="pet-console pixel-panel">
    <header class="pet-head">
      <span class="hud-label">XILI PET // {{ moodLabel }}</span>
      <span class="pet-state">
        <span class="led" :class="offline > 0 ? 'warn' : 'online'" />
        {{ offline > 0 ? 'ALERT' : 'STABLE' }}
      </span>
    </header>

    <div v-if="hasSearched" class="pet-services">
      <div v-for="service in services" :key="service.id" class="pet-service">
        <i :class="statusClass(service)" />
        <span>{{ service.name }}</span>
        <small>{{ statusText(service) }}</small>
      </div>
      <div v-if="!services.length" class="pet-service-empty">还没有接入服务</div>
    </div>

    <div class="pet-stage" @click="runSearch" @mousemove="track" @mouseleave="resetLook">
      <button
        v-if="!searching"
        class="pet-search"
        type="button"
        title="用放大镜搜索所有服务"
        @click.stop="runSearch"
      >
        <Search />
      </button>
      <div v-else class="pet-orbit" aria-hidden="true">
        <div class="pet-orbit-arm">
          <div class="pet-orbit-counter">
            <span class="pet-search is-flying"><Search /></span>
          </div>
        </div>
      </div>

      <div :key="bubble" class="pet-bubble">{{ bubble }}</div>
      <span v-if="searching" class="pet-scanline" />

      <div class="pet-move" :style="lookStyle">
        <div class="pet-body" :class="{ jump }">
          <img :src="robot" alt="XILI 小矽" draggable="false" />
        </div>
        <span class="pet-shadow" />
      </div>
    </div>

    <footer class="pet-meta">
      <div class="pet-name">
        <strong>小矽</strong>
        <small>{{ statusLine }}</small>
      </div>
      <div class="pet-counts">
        <span><i class="online" />{{ online }} 在线</span>
        <span><i class="offline" />{{ offline }} 离线</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Search } from 'lucide-vue-next'
import type { Service } from '@/types'
import robot from '@/assets/brand/robot.png'

const props = withDefaults(
  defineProps<{
    services?: Service[]
    online?: number
    offline?: number
  }>(),
  { services: () => [], online: 0, offline: 0 },
)

const searching = ref(false)
const hasSearched = ref(false)
const bubble = ref('')
const jump = ref(false)
const lookX = ref(0)
const lookY = ref(0)

let bubbleTimer: number | undefined
let jumpTimer: number | undefined
let searchTimer: number | undefined

const moodLabel = computed(() =>
  props.offline > 0 ? 'ALERT' : props.online > 0 ? 'HAPPY' : 'IDLE',
)

const statusLine = computed(() => {
  if (props.offline > 0) return `${props.offline} 个服务离线，正在盯着它们`
  if (props.online > 0) return `${props.online} 条路由在线，隧道稳定`
  return '待命中，点我用放大镜找服务'
})

const HINTS = [
  '点我一下，用放大镜搜服务。',
  '单隧道也能装下整个内网。',
  '密钥轮换后我会自动待机。',
  '需要我帮你巡检一下服务吗？',
  '放大镜一转，服务全出来。',
  '我盯着路由表呢，放心。',
  '有新服务接入记得告诉我。',
  '在线服务越多，我越精神。',
  '离线服务可以点立即检测。',
  '所有隧道都走同一条线，省事。',
  '网关同步好了，我这边收到。',
  '试试点我，看看谁在线。',
]

const hintPool = computed(() => {
  const pool = [...HINTS]
  if (props.online > 0) pool.push(`${props.online} 条路由在线，隧道稳定。`)
  if (props.offline > 0) pool.push(`有 ${props.offline} 个服务离线，要我看看吗？`)
  return pool
})

function nextHint(): void {
  const pool = hintPool.value
  if (!pool.length) return
  let next = pool[Math.floor(Math.random() * pool.length)] ?? ''
  for (let i = 0; i < 5 && next === bubble.value && pool.length > 1; i += 1) {
    next = pool[Math.floor(Math.random() * pool.length)] ?? ''
  }
  bubble.value = next
}

const lookStyle = computed(() => ({
  transform: `translate(${lookX.value}px, ${lookY.value}px)`,
}))

function statusText(service: Service): string {
  if (!service.is_enabled) return '已停用'
  if (service.is_online === true) return '在线'
  if (service.is_online === false) return '离线'
  return '未知'
}

function statusClass(service: Service): string {
  if (!service.is_enabled) return 'disabled'
  if (service.is_online === true) return 'online'
  if (service.is_online === false) return 'offline'
  return 'warn'
}

function pokeJump(): void {
  jump.value = false
  window.requestAnimationFrame(() => {
    jump.value = true
  })
  window.clearTimeout(jumpTimer)
  jumpTimer = window.setTimeout(() => {
    jump.value = false
  }, 660)
}

function runSearch(): void {
  if (searching.value) return
  searching.value = true
  hasSearched.value = false
  nextHint()
  pokeJump()

  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    searching.value = false
    hasSearched.value = true
  }, 1500)
}

function track(event: MouseEvent): void {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const dx = event.clientX - (rect.left + rect.width / 2)
  const dy = event.clientY - (rect.top + rect.height / 2)
  lookX.value = Math.max(-34, Math.min(34, dx / 10))
  lookY.value = Math.max(-20, Math.min(20, dy / 14))
}

function resetLook(): void {
  lookX.value = 0
  lookY.value = 0
}

onMounted(() => {
  nextHint()
  bubbleTimer = window.setInterval(() => {
    if (!searching.value) nextHint()
  }, 2000)
})

onUnmounted(() => {
  window.clearInterval(bubbleTimer)
  window.clearTimeout(jumpTimer)
  window.clearTimeout(searchTimer)
})
</script>

<style scoped>
.pet-console {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 520px;
  padding: 0;
  overflow: hidden;
}

.pet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
}

.pet-state {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.12em;
}

.pet-services {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  gap: 6px;
  max-height: 190px;
  overflow-y: auto;
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
  background: rgba(4, 10, 22, 0.4);
  scrollbar-gutter: stable;
  animation: pet-list-in 0.42s ease-out;
}

@keyframes pet-list-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pet-service {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border: 1px solid rgba(95, 211, 243, 0.12);
  border-radius: 5px;
  background: rgba(5, 12, 26, 0.72);
  font-family: var(--mono);
  font-size: 11.5px;
}

.pet-service i {
  flex: 0 0 auto;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.pet-service i.online {
  background: var(--xl-lime);
  box-shadow: 0 0 8px rgba(139, 255, 176, 0.8);
}

.pet-service i.offline {
  background: var(--xl-red);
  box-shadow: 0 0 8px rgba(255, 95, 126, 0.8);
}

.pet-service i.warn {
  background: var(--xl-amber);
}

.pet-service i.disabled {
  background: var(--text-muted);
}

.pet-service span {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  color: var(--text-dim);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pet-service small {
  flex: 0 0 auto;
  color: var(--text-muted);
  font-size: 10px;
}

.pet-service-empty {
  padding: 8px 4px;
  color: var(--text-muted);
  font-size: 12px;
  text-align: center;
}

.pet-stage {
  position: relative;
  display: flex;
  flex: 1 1 auto;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  overflow: hidden;
  cursor: pointer;
  background: radial-gradient(circle at 50% 56%, rgba(58, 110, 216, 0.14), transparent 62%);
}

.pet-stage::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    repeating-linear-gradient(0deg, rgba(95, 211, 243, 0.05) 0 1px, transparent 1px 34px),
    repeating-linear-gradient(90deg, rgba(95, 211, 243, 0.05) 0 1px, transparent 1px 34px);
  mask-image: radial-gradient(circle at 50% 50%, #000 0 58%, transparent 74%);
}

.pet-search {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 7;
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border: 1px solid rgba(95, 211, 243, 0.32);
  border-radius: 50%;
  background: rgba(5, 12, 26, 0.88);
  color: var(--xl-cyan);
  cursor: pointer;
  box-shadow: 0 0 16px rgba(95, 211, 243, 0.12);
  transition: 0.16s ease;
}

.pet-search:hover {
  border-color: var(--xl-cyan);
  box-shadow: 0 0 20px rgba(95, 211, 243, 0.3);
}

.pet-search svg {
  width: 18px;
  height: 18px;
}

.pet-orbit {
  position: absolute;
  inset: 0;
  z-index: 7;
  display: grid;
  place-items: center;
  pointer-events: none;
}

.pet-orbit-arm {
  position: relative;
  animation: pet-orbit-spin 1.5s linear;
}

.pet-orbit-counter {
  position: relative;
  animation: pet-orbit-counter 1.5s linear;
}

/* The glass keeps its upright orientation while the whole image orbits. */
.pet-search.is-flying {
  top: -132px;
  right: auto;
  left: -19px;
  pointer-events: none;
  animation: pet-orbit-wave 0.75s ease-in-out infinite;
}

@keyframes pet-orbit-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pet-orbit-counter {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(-360deg);
  }
}

@keyframes pet-orbit-wave {
  0%,
  100% {
    top: -114px;
  }
  50% {
    top: -146px;
  }
}

.pet-scanline {
  position: absolute;
  left: 50%;
  z-index: 4;
  width: 210px;
  height: 1px;
  transform: translateX(-50%);
  background: linear-gradient(90deg, transparent, rgba(95, 211, 243, 0.85), transparent);
  box-shadow: 0 0 12px rgba(95, 211, 243, 0.6);
  animation: pet-scan 1.1s ease-in-out infinite;
}

@keyframes pet-scan {
  0%,
  100% {
    top: 24%;
    opacity: 0.2;
  }
  50% {
    top: 74%;
    opacity: 1;
  }
}

.pet-bubble {
  position: absolute;
  top: 16px;
  left: 50%;
  z-index: 6;
  max-width: 210px;
  padding: 7px 10px;
  transform: translateX(-50%);
  border: 1px solid rgba(95, 211, 243, 0.28);
  border-radius: 6px;
  background: rgba(5, 12, 26, 0.94);
  color: var(--text-dim);
  font-family: var(--mono);
  font-size: 11.5px;
  line-height: 1.5;
  text-align: center;
  box-shadow: 0 4px 0 rgba(3, 6, 13, 0.7);
  animation: pet-bubble 0.36s ease-out;
}

.pet-bubble::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  width: 8px;
  height: 8px;
  transform: translateX(-50%) rotate(45deg);
  border-right: 1px solid rgba(95, 211, 243, 0.28);
  border-bottom: 1px solid rgba(95, 211, 243, 0.28);
  background: rgba(5, 12, 26, 0.94);
}

@keyframes pet-bubble {
  from {
    opacity: 0;
    transform: translate(-50%, 6px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0) scale(1);
  }
}

.pet-move {
  position: relative;
  z-index: 3;
  transition: transform 0.4s ease-out;
}

.pet-shadow {
  position: absolute;
  bottom: -12px;
  left: 50%;
  width: 120px;
  height: 18px;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(95, 211, 243, 0.22), transparent 70%);
  filter: blur(2px);
  animation: pet-shadow 4.2s ease-in-out infinite;
}

.pet-body {
  animation: pet-bob 4.2s ease-in-out infinite;
}

.pet-body.jump {
  animation: pet-jump 0.66s cubic-bezier(0.28, 0.84, 0.42, 1);
}

.pet-body img {
  display: block;
  width: 156px;
  height: 156px;
  object-fit: contain;
  image-rendering: pixelated;
  filter: drop-shadow(0 0 22px rgba(95, 211, 243, 0.35));
  user-select: none;
}

@keyframes pet-bob {
  0%,
  100% {
    transform: translateY(0) rotate(-1deg);
  }
  50% {
    transform: translateY(-10px) rotate(1deg);
  }
}

@keyframes pet-jump {
  0% {
    transform: translateY(0) scale(1);
  }
  35% {
    transform: translateY(-34px) scale(1.05);
  }
  65% {
    transform: translateY(-12px) scale(0.98);
  }
  100% {
    transform: translateY(0) scale(1);
  }
}

@keyframes pet-shadow {
  0%,
  100% {
    opacity: 0.7;
    transform: translateX(-50%) scaleX(1);
  }
  50% {
    opacity: 0.4;
    transform: translateX(-50%) scaleX(0.82);
  }
}


.pet-meta {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px 18px;
  border-top: 1px solid var(--line);
}

.pet-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.pet-name strong {
  color: #eaf6ff;
  font-size: 16px;
  letter-spacing: 0.08em;
}

.pet-name small {
  color: var(--text-muted);
  font-size: 11.5px;
  line-height: 1.5;
}

.pet-counts {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 10.5px;
  text-align: right;
}

.pet-counts i {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-right: 6px;
  border-radius: 50%;
}

.pet-counts i.online {
  background: var(--xl-lime);
  box-shadow: 0 0 8px rgba(139, 255, 176, 0.8);
}

.pet-counts i.offline {
  background: var(--xl-red);
  box-shadow: 0 0 8px rgba(255, 95, 126, 0.8);
}

@media (prefers-reduced-motion: reduce) {
  .pet-body,
  .pet-body.jump,
  .pet-shadow,
  .pet-blip,
  .pet-bubble,
  .pet-scanline,
  .pet-orbit-arm,
  .pet-orbit-counter,
  .pet-search.is-flying {
    animation: none !important;
  }
}
</style>
