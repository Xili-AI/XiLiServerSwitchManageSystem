import type { User, UserPayload } from '@/types'
import { request } from './http'

export interface UserMutationResult {
  user: User
}

export interface UserDeleteResult {
  deleted_id: number
  username: string
}

export const usersApi = {
  list() {
    return request<{ users: User[] }>({ url: '/users' })
  },
  create(payload: UserPayload) {
    return request<UserMutationResult>({
      url: '/users',
      method: 'post',
      data: payload,
    })
  },
  update(id: number, payload: UserPayload) {
    return request<UserMutationResult>({
      url: `/users/${id}`,
      method: 'put',
      data: payload,
    })
  },
  remove(id: number) {
    return request<UserDeleteResult>({
      url: `/users/${id}`,
      method: 'delete',
    })
  },
}
