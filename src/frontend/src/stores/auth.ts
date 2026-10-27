import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import type { User } from '@/types'
import {
  clearSessionStorage,
  getStoredUser,
  getToken,
  setStoredUser,
  setToken,
} from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(getToken())
  const user = ref<User | null>(getStoredUser())
  const initialized = ref(false)
  const loading = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value))
  const isAdmin = computed(() => Boolean(user.value?.is_admin))
  const displayName = computed(() => user.value?.display_name || user.value?.username || '操作员')

  function clearSession(): void {
    token.value = ''
    user.value = null
    clearSessionStorage()
  }

  async function bootstrap(): Promise<void> {
    if (!token.value) {
      initialized.value = true
      return
    }
    try {
      const profile = await authApi.profile()
      user.value = profile
      setStoredUser(profile)
    } catch {
      clearSession()
    } finally {
      initialized.value = true
    }
  }

  async function login(username: string, password: string): Promise<User> {
    loading.value = true
    try {
      const result = await authApi.login(username, password)
      token.value = result.token
      user.value = result.user
      setToken(result.token)
      setStoredUser(result.user)
      return result.user
    } finally {
      loading.value = false
    }
  }

  async function logout(remote = true): Promise<void> {
    try {
      if (remote && token.value) await authApi.logout()
    } catch {
      // A local logout must still succeed when the backend is unreachable.
    } finally {
      clearSession()
    }
  }

  async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await authApi.changePassword(oldPassword, newPassword)
    clearSession()
  }

  return {
    token,
    user,
    initialized,
    loading,
    isAuthenticated,
    isAdmin,
    displayName,
    bootstrap,
    login,
    logout,
    clearSession,
    changePassword,
  }
})
