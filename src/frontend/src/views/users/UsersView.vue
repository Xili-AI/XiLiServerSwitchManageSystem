<template>
  <div class="users-page">
    <header class="page-head">
      <div>
        <span class="hud-label">// ACCESS CONTROL</span>
        <h1>用户管理</h1>
        <p>管理员可以编辑账号和服务授权；普通用户只能打开被授权的服务入口。</p>
      </div>
      <PixelButton variant="primary" @click="openCreate">
        <Plus />
        添加用户
      </PixelButton>
    </header>

    <div class="pixel-panel table-wrap">
      <table class="table-cyber">
        <thead>
          <tr>
            <th>用户</th>
            <th>角色</th>
            <th>状态</th>
            <th>可访问服务</th>
            <th>最后登录</th>
            <th class="actions-head">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>
              <div class="user-cell">
                <span class="avatar">{{ initial(user) }}</span>
                <div>
                  <strong>{{ user.display_name || user.username }}</strong>
                  <small>@{{ user.username }}</small>
                </div>
              </div>
            </td>
            <td>
              <span class="tag" :class="{ admin: user.is_admin }">
                {{ user.is_admin ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td>
              <span class="state" :class="{ off: !user.is_active }">
                {{ user.is_active ? '启用' : '停用' }}
              </span>
            </td>
            <td class="mono-cell" :title="serviceNames(user)">
              {{ serviceNames(user) }}
            </td>
            <td class="mono-cell">{{ formatTime(user.last_login_at) }}</td>
            <td>
              <div class="row-actions">
                <button class="icon-action" type="button" title="编辑" @click="openEdit(user)">
                  <Pencil />
                </button>
                <button
                  class="icon-action danger"
                  type="button"
                  title="删除"
                  :disabled="user.id === auth.user?.id"
                  @click="removeUser(user)"
                >
                  <Trash2 />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!users.length && !loading">
            <td colspan="6" class="empty-cell">暂无用户</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="modalOpen" class="modal-backdrop" @click.self="closeModal">
      <div class="pixel-panel modal">
        <header class="modal-head">
          <div>
            <span class="hud-label">{{ editingId ? '// EDIT USER' : '// NEW USER' }}</span>
            <h2>{{ editingId ? '编辑用户' : '添加用户' }}</h2>
          </div>
          <button class="icon-action" type="button" title="关闭" @click="closeModal">
            <X />
          </button>
        </header>

        <form class="modal-body" @submit.prevent="save">
          <label class="field">
            <span>用户名</span>
            <input v-model.trim="form.username" class="pixel-input" autocomplete="off" required />
          </label>
          <label class="field">
            <span>显示名</span>
            <input v-model.trim="form.display_name" class="pixel-input" autocomplete="off" />
          </label>
          <label class="field">
            <span>邮箱</span>
            <input v-model.trim="form.email" class="pixel-input" type="email" autocomplete="off" />
          </label>
          <label class="field">
            <span>{{ editingId ? '新密码（留空不修改）' : '密码' }}</span>
            <input
              v-model="form.password"
              class="pixel-input"
              type="password"
              autocomplete="new-password"
              :required="!editingId"
            />
          </label>

          <div class="switch-row">
            <label class="switch-item">
              <input v-model="form.is_admin" type="checkbox" />
              <span><strong>管理员</strong><small>可以管理服务、用户和系统设置</small></span>
            </label>
            <label class="switch-item">
              <input v-model="form.is_active" type="checkbox" />
              <span><strong>启用</strong><small>停用后无法登录</small></span>
            </label>
          </div>

          <div v-if="!form.is_admin" class="service-picker">
            <div class="picker-head">
              <strong>可访问服务</strong>
              <small>不勾选则看不到任何服务</small>
            </div>
            <div v-if="services.length" class="picker-grid">
              <label v-for="service in services" :key="service.id" class="picker-item">
                <input v-model="form.service_ids" type="checkbox" :value="service.id" />
                <span>
                  <strong>{{ service.name }}</strong>
                  <small>/p/{{ service.slug }}/</small>
                </span>
              </label>
            </div>
            <p v-else class="picker-empty">还没有服务，先在「服务管理」里添加。</p>
          </div>

          <p v-if="error" class="form-error">{{ error }}</p>

          <footer class="modal-foot">
            <PixelButton variant="ghost" type="button" @click="closeModal">取消</PixelButton>
            <PixelButton variant="primary" type="submit" :disabled="saving">
              {{ saving ? '保存中…' : '保存' }}
            </PixelButton>
          </footer>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import { Pencil, Plus, Trash2, X } from 'lucide-vue-next'
import PixelButton from '@/components/cyber/PixelButton.vue'
import { servicesApi } from '@/api/services'
import { usersApi } from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import type { Service, User, UserPayload } from '@/types'

const auth = useAuthStore()
const message = useMessage()
const dialog = useDialog()

const users = ref<User[]>([])
const services = ref<Service[]>([])
const loading = ref(false)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const error = ref('')

const form = reactive<UserPayload>(emptyForm())

function emptyForm(): UserPayload {
  return {
    username: '',
    display_name: '',
    email: '',
    password: '',
    is_admin: false,
    is_active: true,
    service_ids: [],
  }
}

watch(
  () => form.is_admin,
  (value) => {
    if (value) form.service_ids = []
  },
)

function initial(user: User): string {
  return (user.display_name || user.username || '?').slice(0, 1).toUpperCase()
}

function formatTime(value: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function serviceNames(user: User): string {
  if (user.is_admin) return '全部服务'
  const names = services.value
    .filter((service) => (user.service_ids || []).includes(service.id))
    .map((service) => service.name)
  if (!names.length) return '未授权'
  return names.length > 2 ? `${names.slice(0, 2).join('、')} +${names.length - 2}` : names.join('、')
}

async function load(): Promise<void> {
  loading.value = true
  try {
    const [userData, serviceData] = await Promise.all([usersApi.list(), servicesApi.list()])
    users.value = userData.users
    services.value = serviceData.services
  } catch (err) {
    message.error(err instanceof Error ? err.message : '加载用户失败')
  } finally {
    loading.value = false
  }
}

function openCreate(): void {
  editingId.value = null
  error.value = ''
  Object.assign(form, emptyForm())
  modalOpen.value = true
}

function openEdit(user: User): void {
  editingId.value = user.id
  error.value = ''
  Object.assign(form, {
    username: user.username,
    display_name: user.display_name,
    email: user.email || '',
    password: '',
    is_admin: user.is_admin,
    is_active: user.is_active,
    service_ids: [...(user.service_ids || [])],
  })
  modalOpen.value = true
}

function closeModal(): void {
  modalOpen.value = false
  saving.value = false
}

async function save(): Promise<void> {
  error.value = ''
  saving.value = true
  try {
    const payload: UserPayload = {
      username: form.username,
      display_name: form.display_name,
      email: form.email,
      is_admin: form.is_admin,
      is_active: form.is_active,
      service_ids: form.is_admin ? [] : [...form.service_ids],
    }
    if (form.password) payload.password = form.password

    if (editingId.value) {
      await usersApi.update(editingId.value, payload)
      message.success('用户已更新')
    } else {
      await usersApi.create(payload)
      message.success('用户已创建')
    }
    modalOpen.value = false
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败'
  } finally {
    saving.value = false
  }
}

function removeUser(user: User): void {
  dialog.warning({
    title: '删除用户',
    content: `确定删除「${user.display_name || user.username}」？该账号将立即失效。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await usersApi.remove(user.id)
        message.success('用户已删除')
        await load()
      } catch (err) {
        message.error(err instanceof Error ? err.message : '删除失败')
      }
    },
  })
}

onMounted(load)
</script>

<style scoped>
.users-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.page-head h1 {
  margin: 4px 0 6px;
  font-size: 24px;
  letter-spacing: 0.06em;
}

.page-head p {
  margin: 0;
  color: var(--text-muted);
  font-size: 12.5px;
}

.table-wrap {
  padding: 0;
  overflow-x: auto;
}

.table-cyber th,
.table-cyber td {
  white-space: nowrap;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-cell strong {
  display: block;
  font-size: 13px;
}

.user-cell small {
  color: var(--text-muted);
  font-size: 11px;
}

.avatar {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: linear-gradient(135deg, rgba(95, 211, 243, 0.2), rgba(124, 92, 255, 0.2));
  color: var(--xl-cyan);
  font-weight: 700;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  font-size: 11px;
  color: var(--text-dim);
}

.tag.admin {
  border-color: rgba(95, 211, 243, 0.5);
  color: var(--xl-cyan);
}

.state {
  color: var(--ok, #6ee7a8);
  font-size: 11.5px;
}

.state.off {
  color: var(--danger, #ff8d8d);
}

.actions-head {
  text-align: right;
}

.row-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.empty-cell {
  text-align: center;
  color: var(--text-muted);
  padding: 28px 0;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(2, 6, 14, 0.76);
  backdrop-filter: blur(4px);
}

.modal {
  width: min(560px, 100%);
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 18px 20px 12px;
  border-bottom: 1px solid var(--line);
}

.modal-head h2 {
  margin: 4px 0 0;
  font-size: 18px;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px 20px 20px;
  min-height: 0;
  overflow-y: auto;
  scrollbar-gutter: stable;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: var(--text-dim);
}

.switch-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.switch-item,
.picker-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
}

.switch-item span,
.picker-item span {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.switch-item small,
.picker-item small {
  color: var(--text-muted);
  font-size: 11px;
}

.service-picker {
  border: 1px dashed var(--line);
  border-radius: 8px;
  padding: 12px;
}

.picker-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 10px;
}

.picker-head strong {
  font-size: 12.5px;
}

.picker-head small,
.picker-empty {
  color: var(--text-muted);
  font-size: 11px;
}

.picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.form-error {
  margin: 0;
  color: var(--danger, #ff8d8d);
  font-size: 12px;
}

.modal-foot {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 4px;
}

@media (max-width: 560px) {
  .switch-row {
    grid-template-columns: 1fr;
  }
}
</style>
