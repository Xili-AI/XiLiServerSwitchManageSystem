<template>
  <div class="login-view" @mousemove="handleParallax">
    <CyberBackground variant="login" />
    <ScanlineOverlay />

    <header class="login-topbar">
      <AppLogo size="sm" />
      <div class="topbar-right">
        <span class="status-pill">
          <span class="led" :class="online ? 'online' : 'offline'" />
          {{ online ? 'SECURE LINK' : 'LINK OFFLINE' }}
        </span>
        <span class="hud-label">v{{ version }}</span>
      </div>
    </header>

    <main ref="stageRef" class="login-stage">
      <section class="login-brand">
        <div class="brand-badges">
          <span class="pixel-tag">PIXEL</span>
          <span class="pixel-tag violet">CYBER</span>
          <span class="pixel-tag lime">SELF-HOSTED</span>
        </div>

        <GlitchText text="XILI GATEWAY" tag="h1" class="brand-title" />
        <p class="brand-kicker">XILI-AI · SINGLE TUNNEL SERVICE GATEWAY</p>
        <p class="brand-desc">
          苏州矽励科技服务网关管理平台
        </p>

        <div class="brand-terminal terminal-window">
          <div class="terminal-bar">
            <span class="terminal-dot red" />
            <span class="terminal-dot amber" />
            <span class="terminal-dot green" />
            <span class="term-title">xili@gateway:~</span>
            <span class="terminal-tag">SSH / TLS 1.3</span>
          </div>
          <div class="terminal-body">
            <div class="terminal-line">
              <span class="term-prompt">➜</span>
              <span class="terminal-key">boot</span>
              gateway --secure
            </div>
            <div class="terminal-line">
              <span class="term-prompt">➜</span>
              <span class="terminal-key">tunnel</span>
              single / routes dynamic
            </div>
            <div class="terminal-line">
              <span class="term-prompt">➜</span>
              <span class="terminal-key">status</span>
              <span :class="online ? 'term-ok' : 'term-bad'">
                {{ online ? 'secure link established' : 'waiting for gateway' }}
              </span>
              <span class="terminal-caret" />
            </div>
          </div>
        </div>

        <div class="brand-bot-wrap">
          <div class="holo-ring ring-a" />
          <div class="holo-ring ring-b" />
          <div class="bot-scan" />
          <img class="brand-bot" src="@/assets/brand/robot.png" alt="XILI-AI robot" />
          <span class="bot-chip">XILI-AI CORE</span>
        </div>
      </section>

      <section ref="cardRef" class="login-card pixel-panel">
        <div class="card-scan" />
        <div class="terminal-bar card-bar">
          <span class="terminal-dot red" />
          <span class="terminal-dot amber" />
          <span class="terminal-dot green" />
          <span class="term-title">AUTH TERMINAL</span>
          <span class="card-bar-tag">ENCRYPTED</span>
        </div>

        <div class="login-card-body">
          <div class="card-brandline">
            <img src="@/assets/brand/logo.png" alt="XILI-AI" class="card-logo" />
            <span class="hud-label">ACCESS CONSOLE</span>
          </div>

          <h2>接入控制台</h2>
          <p class="card-sub">AUTHORIZED PERSONNEL ONLY / 仅限授权人员</p>

          <form @submit.prevent="submit">
            <label class="pixel-label" for="login-user">OPERATOR ID</label>
            <div class="input-shell" :class="{ focus: focused === 'user' }">
              <UserRound />
              <input
                id="login-user"
                v-model="username"
                autocomplete="username"
                placeholder="输入管理员账号"
                @focus="focused = 'user'"
                @blur="focused = ''"
              />
              <span class="input-code">ID</span>
            </div>

            <label class="pixel-label" for="login-pass">ACCESS KEY</label>
            <div class="input-shell" :class="{ focus: focused === 'pass' }">
              <LockKeyhole />
              <input
                id="login-pass"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="输入访问密码"
                @focus="focused = 'pass'"
                @blur="focused = ''"
              />
              <button class="eye-btn" type="button" :title="showPassword ? '隐藏密码' : '显示密码'" @click="showPassword = !showPassword">
                <EyeOff v-if="showPassword" />
                <Eye v-else />
              </button>
            </div>

            <transition name="fade">
              <div v-if="error" class="login-error" role="alert">
                <TriangleAlert />
                <span>{{ error }}</span>
              </div>
            </transition>

            <PixelButton
              class="submit-btn"
              :class="{ 'anim-shake': shake }"
              type="submit"
              variant="primary"
              size="lg"
              block
              :loading="auth.loading"
            >
              <span class="submit-label">
                <span>进入系统</span>
                <span class="submit-code">ENTER</span>
              </span>
            </PixelButton>
          </form>

          <div class="card-status">
            <span class="status-pill">
              <span class="led" :class="online ? 'online' : 'offline'" />
              {{ online ? 'GATEWAY ONLINE' : 'GATEWAY OFFLINE' }}
            </span>
            <span class="hud-label">v{{ version }}</span>
          </div>

          <div class="card-foot">苏州矽励科技有限公司 · XILI-AI</div>
        </div>
      </section>
    </main>

    <footer class="login-footer">
      <span>© 2026 XILI-AI · SUZHOU XILI TECHNOLOGY</span>
      <span>SINGLE TUNNEL / ZERO EXTRA QUOTA</span>
    </footer>

    <div ref="flashRef" class="login-flash" />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import gsap from 'gsap'
import { Eye, EyeOff, LockKeyhole, TriangleAlert, UserRound } from 'lucide-vue-next'
import CyberBackground from '@/components/cyber/CyberBackground.vue'
import ScanlineOverlay from '@/components/cyber/ScanlineOverlay.vue'
import GlitchText from '@/components/cyber/GlitchText.vue'
import PixelButton from '@/components/cyber/PixelButton.vue'
import AppLogo from '@/components/brand/AppLogo.vue'
import { systemApi } from '@/api/system'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const stageRef = ref<HTMLElement | null>(null)
const cardRef = ref<HTMLElement | null>(null)
const flashRef = ref<HTMLElement | null>(null)
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const focused = ref('')
const error = ref('')
const shake = ref(false)
const online = ref(false)
const version = ref('1.0.0')
let healthTimer = 0
let signingIn = false

function motionDisabled(): boolean {
  return (
    window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
    new URLSearchParams(window.location.search).has('nofx')
  )
}

function resolveRedirect(): string {
  const target = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  if (target.startsWith('/') && !target.startsWith('//')) return target
  return '/'
}

function handleParallax(event: MouseEvent): void {
  if (!stageRef.value) return
  if (motionDisabled()) return
  const x = (event.clientX / window.innerWidth - 0.5) * 2
  const y = (event.clientY / window.innerHeight - 0.5) * 2
  stageRef.value.style.setProperty('--mx', x.toFixed(3))
  stageRef.value.style.setProperty('--my', y.toFixed(3))
}

async function checkHealth(): Promise<void> {
  try {
    const result = await systemApi.health()
    online.value = result.status === 'ok'
    version.value = result.version || version.value
  } catch {
    online.value = false
  }
}

async function loadPublicInfo(): Promise<void> {
  try {
    const info = await systemApi.publicInfo()
    version.value = info.version || version.value
  } catch {
    // The health check already covers availability.
  }
}

async function submit(): Promise<void> {
  if (signingIn) return
  error.value = ''
  if (!username.value.trim() || !password.value) {
    error.value = '请输入操作员账号和访问密码'
    triggerShake()
    return
  }

  signingIn = true
  try {
    await auth.login(username.value.trim(), password.value)
    if (!motionDisabled()) {
      gsap
        .timeline()
        .to('.login-brand', { opacity: 0, y: -16, duration: 0.35, ease: 'power2.in' })
        .to('.login-card', { scale: 0.96, opacity: 0, duration: 0.4, ease: 'power2.in' }, '<')
        .to(stageRef.value, { scale: 1.08, duration: 0.55, ease: 'power2.inOut' }, '<')
        .to(flashRef.value, { opacity: 1, duration: 0.16 }, '-=0.18')
      window.setTimeout(() => router.push(resolveRedirect()), 620)
    } else {
      await router.push(resolveRedirect())
    }
  } catch (loginError) {
    error.value = loginError instanceof Error ? loginError.message : '登录失败'
    triggerShake()
  } finally {
    signingIn = false
  }
}

function triggerShake(): void {
  shake.value = false
  window.requestAnimationFrame(() => {
    shake.value = true
    window.setTimeout(() => {
      shake.value = false
    }, 400)
  })
}

onMounted(async () => {
  await Promise.allSettled([checkHealth(), loadPublicInfo()])
  healthTimer = window.setInterval(checkHealth, 20000)

  if (motionDisabled()) return
  gsap.from('.login-topbar', { y: -18, opacity: 0, duration: 0.6, ease: 'power2.out' })
  gsap.from('.brand-badges', { y: 18, opacity: 0, duration: 0.7, delay: 0.1, ease: 'power3.out' })
  gsap.from('.brand-title', { y: 28, opacity: 0, duration: 0.9, delay: 0.16, ease: 'power3.out' })
  gsap.from('.brand-kicker, .brand-desc', { y: 20, opacity: 0, duration: 0.8, delay: 0.28, stagger: 0.08, ease: 'power3.out' })
  gsap.from('.brand-terminal', { y: 24, opacity: 0, duration: 0.8, delay: 0.4, ease: 'power3.out' })
  gsap.from('.brand-bot-wrap', { scale: 0.55, opacity: 0, duration: 1, delay: 0.42, ease: 'back.out(1.6)' })
  gsap.from('.login-card', { x: 46, opacity: 0, duration: 0.9, delay: 0.18, ease: 'power3.out' })
  gsap.from('.login-footer', { y: 16, opacity: 0, duration: 0.6, delay: 0.7, ease: 'power2.out' })
})

onBeforeUnmount(() => {
  window.clearInterval(healthTimer)
  gsap.killTweensOf('.login-brand, .login-card, .login-stage, .login-flash')
})
</script>

<style scoped>
.login-view {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(1000px 620px at 18% -10%, rgba(58, 110, 216, 0.22), transparent 65%),
    radial-gradient(850px 540px at 88% 108%, rgba(124, 92, 255, 0.14), transparent 62%),
    #04070f;
}

.login-view::after {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background: linear-gradient(90deg, transparent 49.8%, rgba(95, 211, 243, 0.05) 50%, transparent 50.2%);
}

.login-topbar {
  position: relative;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  width: min(1380px, calc(100vw - 48px));
  margin: 0 auto;
  padding: 22px 0;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.login-stage {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(380px, 0.82fr);
  align-items: center;
  gap: 44px;
  width: min(1280px, calc(100vw - 48px));
  min-height: calc(100vh - 170px);
  margin: 0 auto;
  padding: 12px 0 74px;
  transform-style: preserve-3d;
}

.login-brand {
  position: relative;
  max-width: 650px;
  padding-bottom: 10px;
}

.brand-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-bottom: 18px;
}

.brand-title {
  margin: 0;
  font-family: var(--pixel);
  font-size: clamp(30px, 4.2vw, 56px);
  line-height: 1.18;
  letter-spacing: 0.04em;
  color: #fff;
}

.brand-kicker {
  margin: 16px 0 0;
  color: var(--xl-cyan);
  font-family: var(--mono);
  font-size: clamp(17px, 1.7vw, 21px);
  letter-spacing: 0.16em;
  text-shadow: 0 0 18px rgba(95, 211, 243, 0.3);
}

.brand-desc {
  max-width: 560px;
  margin: 13px 0 0;
  color: var(--text-dim);
  font-size: 14px;
  line-height: 1.8;
}

.brand-terminal {
  max-width: 560px;
  margin-top: 22px;
  box-shadow: 0 8px 0 rgba(3, 6, 13, 0.65), 0 20px 50px rgba(0, 0, 0, 0.3);
}

.term-title {
  margin-left: 4px;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.1em;
}

.terminal-tag {
  margin-left: auto;
  color: var(--xl-cyan);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.08em;
}

.term-prompt {
  margin-right: 7px;
  color: var(--xl-violet);
}

.terminal-key {
  display: inline-block;
  min-width: 62px;
  margin-right: 7px;
  color: var(--xl-cyan);
}

.term-ok {
  color: var(--xl-lime);
}

.term-bad {
  color: var(--xl-amber);
}

.brand-bot-wrap {
  position: absolute;
  right: -46px;
  bottom: -96px;
  width: 226px;
  height: 226px;
  transform: translate3d(calc(var(--mx, 0) * 11px), calc(var(--my, 0) * 11px), 0);
  transition: transform 0.16s ease-out;
  pointer-events: none;
}

.holo-ring {
  width: 200px;
  height: 200px;
}

.ring-a {
  left: 13px;
  top: 12px;
  animation: ring-spin 22s linear infinite;
}

.ring-b {
  left: 0;
  top: 0;
  width: 226px;
  height: 226px;
  border-style: dashed;
  animation: ring-spin-reverse 30s linear infinite;
}

.brand-bot {
  position: absolute;
  left: 34px;
  top: 26px;
  width: 158px;
  height: 158px;
  object-fit: contain;
  image-rendering: pixelated;
  animation: float-soft 5.2s ease-in-out infinite;
  filter: drop-shadow(0 0 22px rgba(95, 211, 243, 0.3));
}

.bot-scan {
  position: absolute;
  left: 4px;
  right: 4px;
  top: 4px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(95, 211, 243, 0.8), transparent);
  box-shadow: 0 0 14px rgba(95, 211, 243, 0.6);
  animation: bot-scan 4.2s ease-in-out infinite;
}

.bot-chip {
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  padding: 3px 8px;
  border: 1px solid rgba(95, 211, 243, 0.3);
  background: rgba(3, 8, 18, 0.86);
  color: var(--xl-cyan);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.1em;
  white-space: nowrap;
}

@keyframes bot-scan {
  0%,
  100% {
    transform: translateY(0);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  80% {
    opacity: 1;
  }
  50% {
    transform: translateY(190px);
  }
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 480px;
  justify-self: end;
  overflow: hidden;
  box-shadow: 0 10px 0 rgba(3, 6, 13, 0.9), 0 42px 90px rgba(0, 0, 0, 0.55);
}

.card-scan {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
}

.card-scan::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: -40%;
  height: 30%;
  background: linear-gradient(180deg, transparent, rgba(95, 211, 243, 0.05), transparent);
  animation: card-scan 6s linear infinite;
}

@keyframes card-scan {
  to {
    transform: translateY(560px);
  }
}

.card-bar {
  display: flex;
}

.card-bar-tag {
  margin-left: auto;
  color: var(--xl-lime);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.1em;
}

.login-card-body {
  position: relative;
  z-index: 2;
  padding: 23px 24px 20px;
}

.card-brandline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.card-logo {
  width: auto;
  height: 20px;
  image-rendering: pixelated;
  filter: drop-shadow(0 0 14px rgba(95, 211, 243, 0.2));
}

.login-card h2 {
  margin: 0;
  color: #f2f8ff;
  font-size: 25px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.card-sub {
  margin: 4px 0 20px;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.1em;
}

.input-shell {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 48px;
  margin-bottom: 15px;
  padding: 0 13px;
  border: 2px solid #1b3766;
  border-radius: 6px;
  background: rgba(4, 10, 22, 0.9);
  transition: 0.18s ease;
}

.input-shell.focus {
  border-color: var(--xl-cyan);
  background: rgba(6, 15, 32, 0.96);
  box-shadow: 0 0 0 3px rgba(95, 211, 243, 0.1), inset 0 0 22px rgba(95, 211, 243, 0.05);
}

.input-shell > svg {
  width: 17px;
  height: 17px;
  flex: 0 0 auto;
  color: var(--text-muted);
}

.input-shell.focus > svg {
  color: var(--xl-cyan);
}

.input-shell input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text);
  font-family: var(--body);
  font-size: 14px;
}

.input-shell input::placeholder {
  color: #4f6a99;
}

.input-code {
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.12em;
}

.eye-btn {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  border: 0;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted);
}

.eye-btn:hover {
  color: var(--xl-cyan);
  background: rgba(95, 211, 243, 0.06);
}

.eye-btn svg {
  width: 16px;
  height: 16px;
}

.login-error {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: -3px 0 14px;
  padding: 9px 11px;
  border: 1px solid rgba(255, 95, 126, 0.4);
  border-radius: 5px;
  background: rgba(255, 95, 126, 0.08);
  color: #ffb3c0;
  font-size: 12.5px;
  line-height: 1.5;
}

.login-error svg {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
  margin-top: 1px;
}

.submit-btn {
  margin-top: 3px;
}

.submit-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 4px;
}

.submit-code {
  color: rgba(255, 255, 255, 0.62);
  font-size: 15px;
  letter-spacing: 0.12em;
}

.card-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
}

.card-foot {
  margin-top: 14px;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-align: center;
}

.login-footer {
  position: absolute;
  left: 50%;
  bottom: 20px;
  z-index: 3;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  width: min(1280px, calc(100vw - 48px));
  transform: translateX(-50%);
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.1em;
}

.login-flash {
  position: fixed;
  inset: 0;
  z-index: 80;
  pointer-events: none;
  opacity: 0;
  background: radial-gradient(circle at center, rgba(95, 211, 243, 0.8), rgba(58, 110, 216, 0.2) 45%, transparent 72%);
}

@media (max-width: 1100px) {
  .login-stage {
    grid-template-columns: minmax(0, 1fr) minmax(360px, 0.9fr);
    gap: 28px;
  }

  .brand-bot-wrap {
    display: none;
  }

  .brand-desc {
    max-width: 500px;
  }
}

@media (max-width: 900px) {
  .login-topbar {
    width: calc(100vw - 32px);
    padding: 16px 0;
  }

  .login-stage {
    grid-template-columns: 1fr;
    width: min(560px, calc(100vw - 32px));
    min-height: auto;
    padding: 12px 0 90px;
    gap: 24px;
  }

  .login-brand {
    text-align: center;
    max-width: none;
  }

  .brand-badges {
    justify-content: center;
  }

  .brand-title {
    font-size: clamp(28px, 8vw, 42px);
  }

  .brand-kicker {
    font-size: 15px;
  }

  .brand-desc,
  .brand-terminal {
    display: none;
  }

  .login-card {
    max-width: 520px;
    justify-self: center;
  }

  .login-footer {
    position: static;
    width: calc(100vw - 32px);
    margin: 0 auto;
    padding: 0 0 24px;
    transform: none;
    font-size: 10px;
  }
}

@media (max-width: 560px) {
  .login-topbar .hud-label,
  .topbar-right .status-pill {
    display: none;
  }

  .login-card-body {
    padding: 20px 17px 17px;
  }

  .login-brand {
    padding-top: 8px;
  }

  .brand-title {
    font-size: 24px;
  }

  .brand-kicker {
    letter-spacing: 0.08em;
  }

  .card-bar-tag {
    display: none;
  }

  .login-footer {
    flex-direction: column;
    gap: 2px;
    text-align: center;
  }
}
</style>
