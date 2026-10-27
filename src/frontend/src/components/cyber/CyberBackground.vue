<template>
  <div class="cyber-bg" aria-hidden="true">
    <div class="cyber-grid" />
    <div class="cyber-glow top" />
    <div class="cyber-glow bottom" />
    <canvas ref="canvasRef" class="cyber-canvas" />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  alpha: number
  hue: string
}

const props = withDefaults(
  defineProps<{
    variant?: 'login' | 'app'
  }>(),
  { variant: 'app' },
)

const canvasRef = ref<HTMLCanvasElement | null>(null)
let frame = 0
let particles: Particle[] = []
let width = 0
let height = 0
let context: CanvasRenderingContext2D | null = null

function createParticle(): Particle {
  const cyan = Math.random() > 0.45
  return {
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.24,
    vy: (Math.random() - 0.5) * 0.24,
    size: Math.random() > 0.86 ? 3 : 2,
    alpha: 0.18 + Math.random() * 0.46,
    hue: cyan ? '95, 211, 243' : '124, 92, 255',
  }
}

function resize(): void {
  const canvas = canvasRef.value
  if (!canvas) return
  const ratio = Math.min(window.devicePixelRatio || 1, 2)
  width = window.innerWidth
  height = window.innerHeight
  canvas.width = Math.floor(width * ratio)
  canvas.height = Math.floor(height * ratio)
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`
  context = canvas.getContext('2d')
  if (!context) return
  context.setTransform(ratio, 0, 0, ratio, 0, 0)
  const base = props.variant === 'login' ? 64 : 26
  const count = width < 760 ? Math.floor(base / 2) : base
  particles = Array.from({ length: count }, createParticle)
}

function draw(): void {
  if (!context) return
  context.clearRect(0, 0, width, height)

  for (let index = 0; index < particles.length; index += 1) {
    const particle = particles[index]
    particle.x += particle.vx
    particle.y += particle.vy
    if (particle.x < -20) particle.x = width + 20
    if (particle.x > width + 20) particle.x = -20
    if (particle.y < -20) particle.y = height + 20
    if (particle.y > height + 20) particle.y = -20

    context.fillStyle = `rgba(${particle.hue}, ${particle.alpha})`
    context.fillRect(particle.x, particle.y, particle.size, particle.size)

    for (let otherIndex = index + 1; otherIndex < particles.length; otherIndex += 1) {
      const other = particles[otherIndex]
      const dx = particle.x - other.x
      const dy = particle.y - other.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      if (distance > 128) continue
      context.strokeStyle = `rgba(95, 211, 243, ${(1 - distance / 128) * 0.07})`
      context.lineWidth = 1
      context.beginPath()
      context.moveTo(particle.x, particle.y)
      context.lineTo(other.x, other.y)
      context.stroke()
    }
  }

  frame = window.requestAnimationFrame(draw)
}

onMounted(() => {
  resize()
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduced) {
    draw()
    window.cancelAnimationFrame(frame)
    return
  }
  draw()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.cancelAnimationFrame(frame)
  window.removeEventListener('resize', resize)
})
</script>

<style scoped>
.cyber-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}
</style>
