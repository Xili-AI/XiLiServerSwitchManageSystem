import type { LoginResult, User } from '@/types'
import { request } from './http'

export const authApi = {
  login(username: string, password: string) {
    return request<LoginResult>({
      url: '/auth/login',
      method: 'post',
      data: { username, password },
    })
  },
  logout() {
    return request<void>({ url: '/auth/logout', method: 'post' })
  },
  profile() {
    return request<User>({ url: '/auth/profile' })
  },
  changePassword(oldPassword: string, newPassword: string) {
    return request<void>({
      url: '/auth/change-password',
      method: 'post',
      data: { old_password: oldPassword, new_password: newPassword },
    })
  },
}
