import type { Service, ServiceMode, Settings } from '@/types'

export function isLoopbackHost(host: string): boolean {
  const value = (host || '').toLowerCase()
  return (
    value === 'localhost' ||
    value === '127.0.0.1' ||
    value === '::1' ||
    value === '[::1]' ||
    value.endsWith('.localhost')
  )
}

export function fallbackBaseDomain(settings: Settings | null): string {
  const configured = (settings?.base_domain || '').replace(/^\.+|\.+$/g, '')
  // "localhost" is the development default. On a real tunnel hostname it must
  // not leak into public service URLs, so infer the wildcard root from the
  // panel hostname instead.
  if (configured && configured !== 'localhost' && configured !== '127.0.0.1') {
    return configured
  }
  const host = window.location.hostname || ''
  return host.startsWith('www.') ? host.slice(4) : host
}

function formatPort(port: string, scheme: string): string {
  const value = String(port || '').trim()
  if (!value) return ''
  if (scheme === 'http' && value === '80') return ''
  if (scheme === 'https' && value === '443') return ''
  return `:${value}`
}

function isIpAddress(host: string): boolean {
  const value = (host || '').replace(/^\[|\]$/g, '')
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(value)) return true
  return value.includes(':')
}

function isLanHostname(host: string): boolean {
  const value = (host || '').toLowerCase()
  if (!value) return true
  if (value.endsWith('.local') || value.endsWith('.lan') || value.endsWith('.home')) return true
  return !value.includes('.')
}

export function effectiveMode(service: Service): ServiceMode {
  if (service.mode === 'origin') return 'origin'
  if (service.mode === 'path') return 'path'
  if (service.mode === 'subdomain') return 'subdomain'
  const host = window.location.hostname
  if (isLoopbackHost(host)) return 'subdomain'
  // A LAN client cannot resolve *.localhost, and <slug>.<LAN-IP> is not a
  // usable hostname. Use same-origin /p/<slug>/ URLs instead.
  if (isIpAddress(host) || isLanHostname(host)) return 'path'
  return 'subdomain'
}

function appendEntryPath(baseUrl: string, entryPath: string): string {
  const path = (entryPath || '').trim()
  if (!path || path === '/') return baseUrl
  return `${baseUrl.replace(/\/+$/, '')}${path.startsWith('/') ? path : `/${path}`}`
}

export function buildServiceUrl(service: Service, settings: Settings | null): string {
  if (effectiveMode(service) === 'origin') {
    // Direct-origin mode: no gateway route. The browser needs the wstunnel
    // client (SOCKS or a local forward) to reach the upstream address remotely.
    return appendEntryPath(service.target_url || service.path_url, service.entry_path)
  }

  if (effectiveMode(service) === 'path') {
    return appendEntryPath(service.path_url || `/p/${service.slug}/`, service.entry_path)
  }

  if (isLoopbackHost(window.location.hostname)) {
    const port = settings?.public_port || '8080'
    return appendEntryPath(
      `http://${service.slug}.localhost${formatPort(port, 'http')}/`,
      service.entry_path,
    )
  }

  const base = fallbackBaseDomain(settings)
  if (!base) {
    return appendEntryPath(service.path_url || `/p/${service.slug}/`, service.entry_path)
  }
  // The browser is the source of truth for the public scheme and (usually)
  // port. This keeps a dev console accessed through a real tunnel working
  // before production settings are filled in.
  // Follow the address bar for public links: the tunnel's public port may be
  // non-standard (22033, 8443, ...) and is not the local gateway port.
  const scheme = window.location.protocol.replace(':', '') || 'https'
  const port = window.location.port
  return appendEntryPath(
    `${scheme}://${service.slug}.${base}${formatPort(port, scheme)}/`,
    service.entry_path,
  )
}

export function modeLabel(service: Service): string {
  if (service.mode === 'path') return '路径'
  if (service.mode === 'subdomain') return '子域名'
  if (service.mode === 'origin') return '直连'
  return '智能'
}

export function statusLabel(service: Service): string {
  if (!service.is_enabled) return '已停用'
  if (service.is_online === true) return '在线'
  if (service.is_online === false) return '离线'
  return '检测中'
}

export function statusTone(service: Service): 'online' | 'offline' | 'warn' {
  if (!service.is_enabled) return 'warn'
  if (service.is_online === true) return 'online'
  if (service.is_online === false) return 'offline'
  return 'warn'
}

export async function copyText(value: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(value)
    return true
  } catch {
    const area = document.createElement('textarea')
    area.value = value
    area.style.position = 'fixed'
    area.style.opacity = '0'
    document.body.appendChild(area)
    area.select()
    let copied = false
    try {
      copied = document.execCommand('copy')
    } catch {
      copied = false
    }
    area.remove()
    return copied
  }
}
