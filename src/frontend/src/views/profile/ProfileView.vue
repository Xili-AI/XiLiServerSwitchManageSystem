<template>
  <div class="profile-page">
    <header class="page-head">
      <div>
        <span class="hud-label">// OPERATOR PROFILE</span>
        <h1>操作员档案</h1>
        <p>查看当前操作员信息并管理账户访问密钥。</p>
      </div>
    </header>

    <div class="profile-grid">
      <div class="profile-stack">
        <section class="pixel-panel identity-card">
        <div class="identity-bg" />
        <div class="identity-top">
          <div class="big-avatar">{{ initial }}</div>
          <div class="identity-name">
            <span class="hud-label">OPERATOR</span>
            <h2>{{ auth.displayName }}</h2>
            <span class="username">@{{ auth.user?.username }}</span>
          </div>
          <span class="pixel-tag lime">{{ auth.user?.is_admin ? 'ADMIN' : 'OPERATOR' }}</span>
        </div>
        <div class="identity-divider" />
        <div class="identity-rows">
          <div class="identity-row">
            <span>邮箱</span>
            <strong>{{ auth.user?.email || '未设置' }}</strong>
          </div>
          <div class="identity-row">
            <span>账号状态</span>
            <strong>{{ auth.user?.is_active ? 'ACTIVE' : 'DISABLED' }}</strong>
          </div>
          <div class="identity-row">
            <span>最近登录</span>
            <strong>{{ formatDateTime(auth.user?.last_login_at) }}</strong>
          </div>
          <div class="identity-row">
            <span>创建时间</span>
            <strong>{{ formatDateTime(auth.user?.created_at) }}</strong>
          </div>
        </div>
        <div class="identity-foot">
          <span class="led online" />
          SESSION ENCRYPTED · JWT / 12H
        </div>
      </section>

      <form class="pixel-panel password-card" @submit.prevent="submit">
        <div class="panel-head">
          <div>
            <span class="hud-label">ACCESS KEY ROTATION</span>
            <h2>修改访问密钥</h2>
          </div>
          <KeyRound class="head-icon" />
        </div>
        <div class="password-body">
          <div class="field">
            <label class="pixel-label" for="old-password">当前密码</label>
            <input id="old-password" v-model="oldPassword" class="pixel-input" type="password" autocomplete="current-password" />
          </div>
          <div class="field">
            <label class="pixel-label" for="new-password">新密码</label>
            <input id="new-password" v-model="newPassword" class="pixel-input" type="password" autocomplete="new-password" />
            <span class="pixel-hint">至少 8 位，必须同时包含字母和数字。</span>
          </div>
          <div class="field">
            <label class="pixel-label" for="confirm-password">确认新密码</label>
            <input id="confirm-password" v-model="confirmPassword" class="pixel-input" type="password" autocomplete="new-password" />
          </div>
          <div v-if="error" class="form-error">{{ error }}</div>
          <div class="password-foot">
            <PixelButton variant="primary" type="submit" :loading="saving">
              <ShieldCheck />
              更新访问密钥
            </PixelButton>
            <span class="foot-hint">更新后所有登录令牌立即失效。</span>
          </div>
        </div>
      </form>
      </div>

      <aside class="profile-deco">
        <PetRobot :services="services.services" :online="onlineCount" :offline="offlineCount" />
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { KeyRound, ShieldCheck } from 'lucide-vue-next'
import PixelButton from '@/components/cyber/PixelButton.vue'
import PetRobot from '@/components/profile/PetRobot.vue'
import { useAuthStore } from '@/stores/auth'
import { useServicesStore } from '@/stores/services'
import { formatDateTime } from '@/utils/format'
import { validatePassword } from '@/utils/validators'

const auth = useAuthStore()
const services = useServicesStore()
const router = useRouter()
const message = useMessage()

const onlineCount = computed(() => services.stats.online ?? 0)
const offlineCount = computed(() => services.stats.offline ?? 0)

onMounted(() => {
  services.fetchAll(true).catch(() => {})
})

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const saving = ref(false)

const initial = computed(() => (auth.displayName || 'X').slice(0, 1).toUpperCase())

async function submit(): Promise<void> {
  error.value = ''
  if (!oldPassword.value) {
    error.value = '请输入当前密码'
    return
  }
  const issue = validatePassword(newPassword.value)
  if (issue) {
    error.value = issue
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次输入的新密码不一致'
    return
  }
  if (newPassword.value === oldPassword.value) {
    error.value = '新密码不能与当前密码相同'
    return
  }

  saving.value = true
  try {
    await auth.changePassword(oldPassword.value, newPassword.value)
    message.success('访问密钥已更新，请重新登录')
    await router.push({ name: 'login' })
  } catch (submitError) {
    error.value = submitError instanceof Error ? submitError.message : '更新失败'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-head h1 {
  margin: 3px 0 0;
  color: #f2f8ff;
  font-size: 26px;
}

.page-head p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 18px;
  align-items: stretch;
}

.profile-stack {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

.profile-deco {
  display: flex;
  min-width: 0;
}

.identity-card {
  position: relative;
  overflow: hidden;
  padding: 28px;
}

.identity-bg {
  position: absolute;
  right: -80px;
  top: -100px;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(95, 211, 243, 0.12), transparent 68%);
  pointer-events: none;
}

.identity-top {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.big-avatar {
  display: grid;
  place-items: center;
  width: 84px;
  height: 84px;
  flex: 0 0 auto;
  border: 1px solid rgba(95, 211, 243, 0.45);
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(58, 110, 216, 0.7), rgba(95, 211, 243, 0.16));
  color: #fff;
  font-family: var(--pixel);
  font-size: 19px;
  box-shadow: 0 6px 0 #03060d, 0 0 32px rgba(95, 211, 243, 0.14);
}

.identity-name {
  flex: 1;
  min-width: 160px;
}

.identity-name h2 {
  margin: 2px 0 0;
  color: #f2f8ff;
  font-size: 24px;
}

.username {
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 15px;
}

.identity-divider {
  height: 1px;
  margin: 22px 0 6px;
  background: linear-gradient(90deg, var(--line-strong), transparent);
}

.identity-rows {
  display: flex;
  flex-direction: column;
}

.identity-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 11px 0;
  border-bottom: 1px solid rgba(95, 211, 243, 0.07);
}

.identity-row span {
  color: var(--text-muted);
  font-size: 13px;
}

.identity-row strong {
  color: var(--text);
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 400;
  text-align: right;
}

.identity-foot {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 18px;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.08em;
}

.password-card {
  overflow: hidden;
}

.panel-head h2 {
  margin: 2px 0 0;
  font-size: 18px;
}

.head-icon {
  width: 20px;
  height: 20px;
  color: var(--xl-cyan);
}

.password-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 24px;
}

.field {
  display: flex;
  flex-direction: column;
}

.form-error {
  padding: 8px 10px;
  border: 1px solid rgba(255, 95, 126, 0.4);
  border-radius: 5px;
  background: rgba(255, 95, 126, 0.08);
  color: #ffb3c0;
  font-size: 12.5px;
}

.password-foot {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 4px;
}

.foot-hint {
  color: var(--text-muted);
  font-size: 12px;
}

@media (max-width: 1200px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .profile-deco {
    display: none;
  }
}
</style>
