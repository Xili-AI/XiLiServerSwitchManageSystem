import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Service, Settings } from '@/types'
import { buildServiceUrl, fallbackBaseDomain, isLoopbackHost } from '@/utils/url'

function makeService(overrides: Partial<Service> = {}): Service {
  return {
    id: '1',
    name: 'Demo',
    slug: 'demo',
    target_url: 'http://demo:8080',
    entry_path: '',
    strip_prefix: true,
    description: '',
    color: '#5fd3f3',
    icon: 'server',
    mode: 'auto',
    is_enabled: true,
    sort_order: 0,
    is_online: true,
    last_checked_at: null,
    latency_ms: 12,
    last_error: null,
    created_at: '',
    updated_at: '',
    public_url: null,
    path_url: '/p/demo/',
    local_port: 18100,
    ...overrides,
  }
}

function makeSettings(overrides: Partial<Settings> = {}): Settings {
  return {
    base_domain: 'example.com',
    public_scheme: 'https',
    public_port: '',
    health_interval: 20,
    skip_tls_verify: false,
    site_name: '矽励科技服务网关管理系统',
    ...overrides,
  }
}

function stubLocation(hostname: string, port = '', protocol = 'https:') {
  vi.stubGlobal('window', { location: { hostname, port, protocol } })
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('isLoopbackHost', () => {
  it('detects loopback hostnames', () => {
    expect(isLoopbackHost('localhost')).toBe(true)
    expect(isLoopbackHost('127.0.0.1')).toBe(true)
    expect(isLoopbackHost('files.localhost')).toBe(true)
    expect(isLoopbackHost('example.com')).toBe(false)
  })
})

describe('fallbackBaseDomain', () => {
  it('uses the configured domain first', () => {
    expect(fallbackBaseDomain(makeSettings())).toBe('example.com')
  })

  it('removes the www prefix from the current host', () => {
    stubLocation('www.example.com')
    expect(fallbackBaseDomain(null)).toBe('example.com')
  })

  it('ignores the localhost default on a real tunnel hostname', () => {
    stubLocation('www.tunnel.example')
    expect(fallbackBaseDomain(makeSettings({ base_domain: 'localhost' }))).toBe('tunnel.example')
  })
})

describe('buildServiceUrl', () => {
  it('uses the path fallback for path mode', () => {
    stubLocation('example.com')
    const url = buildServiceUrl(makeService({ mode: 'path' }), makeSettings())
    expect(url).toBe('/p/demo/')
  })

  it('uses the upstream target for origin mode', () => {
    stubLocation('192.168.1.10', '8080', 'http:')
    const url = buildServiceUrl(
      makeService({ mode: 'origin', target_url: 'http://192.168.1.12:8099' }),
      makeSettings({ base_domain: 'localhost', public_port: '8080' }),
    )
    expect(url).toBe('http://192.168.1.12:8099')
  })

  it('uses *.localhost for local console access', () => {
    stubLocation('127.0.0.1', '3000', 'http:')
    const url = buildServiceUrl(makeService(), makeSettings({ base_domain: 'localhost' }))
    expect(url).toBe('http://demo.localhost:8080/')
  })

  it('uses the configured public domain', () => {
    stubLocation('console.example.com')
    const url = buildServiceUrl(makeService(), makeSettings())
    expect(url).toBe('https://demo.example.com/')
  })

  it('infers the tunnel root and browser scheme from a dev console', () => {
    stubLocation('www.tunnel.example', '', 'https:')
    const url = buildServiceUrl(
      makeService(),
      makeSettings({ base_domain: 'localhost', public_scheme: 'http', public_port: '' }),
    )
    expect(url).toBe('https://demo.tunnel.example/')
  })

  it('preserves a non-standard public port from the address bar', () => {
    stubLocation('console.example.com', '8443')
    const url = buildServiceUrl(makeService(), makeSettings({ public_port: '8080' }))
    expect(url).toBe('https://demo.example.com:8443/')
  })

  it('appends the optional entry path', () => {
    stubLocation('127.0.0.1', '8080', 'http:')
    const url = buildServiceUrl(
      makeService({ entry_path: '/dashboard' }),
      makeSettings({ base_domain: 'localhost' }),
    )
    expect(url).toBe('http://demo.localhost:8080/dashboard')
  })

  it('uses same-origin path mode for a LAN IP console', () => {
    stubLocation('192.168.1.10', '8080', 'http:')
    const url = buildServiceUrl(
      makeService(),
      makeSettings({ base_domain: 'localhost', public_port: '8080' }),
    )
    expect(url).toBe('/p/demo/')
  })
})
