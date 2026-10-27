import type {
  GatewaySyncResult,
  Service,
  ServiceListData,
  ServicePayload,
} from '@/types'
import { request } from './http'

export interface ServiceMutationResult {
  service: Service
  gateway: GatewaySyncResult
}

export interface ServiceDeleteResult {
  deleted_id: string
  gateway: GatewaySyncResult
}

export const servicesApi = {
  list() {
    return request<ServiceListData>({ url: '/services' })
  },
  create(payload: ServicePayload) {
    return request<ServiceMutationResult>({
      url: '/services',
      method: 'post',
      data: payload,
    })
  },
  update(id: string, payload: ServicePayload) {
    return request<ServiceMutationResult>({
      url: `/services/${encodeURIComponent(id)}`,
      method: 'put',
      data: payload,
    })
  },
  remove(id: string) {
    return request<ServiceDeleteResult>({
      url: `/services/${encodeURIComponent(id)}`,
      method: 'delete',
    })
  },
  check(id: string) {
    return request<{ service: Service }>({
      url: `/services/${encodeURIComponent(id)}/check`,
      method: 'post',
    })
  },
  reorder(orderedIds: string[]) {
    return request<{ services: Service[]; gateway: GatewaySyncResult }>({
      url: '/services/reorder',
      method: 'put',
      data: { ordered_ids: orderedIds },
    })
  },
}
