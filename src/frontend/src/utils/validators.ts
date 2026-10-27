export const SLUG_PATTERN = /^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/

export function isValidSlug(value: string): boolean {
  return SLUG_PATTERN.test(value || '')
}

export function slugify(value: string): string {
  return (value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 32)
    .replace(/-+$/g, '')
}

export function isValidHexColor(value: string): boolean {
  return /^#[0-9a-f]{6}$/i.test(value || '')
}

export function validateTarget(value: string): string | null {
  const text = (value || '').trim()
  if (!text) return '目标地址不能为空'
  const candidate = /^[a-z][a-z0-9+.-]*:\/\//i.test(text) ? text : `http://${text}`
  let parsed: URL
  try {
    parsed = new URL(candidate)
  } catch {
    return '目标地址格式不正确'
  }
  if (!['http:', 'https:'].includes(parsed.protocol)) return '只支持 http:// 或 https://'
  if (!parsed.hostname) return '目标地址缺少主机名'
  if (parsed.pathname !== '/' && parsed.pathname !== '') return '目标地址只填写协议、主机和端口'
  if (parsed.search || parsed.hash) return '目标地址不要带查询参数或锚点'
  return null
}

export function validatePassword(value: string): string | null {
  if (value.length < 8) return '密码至少需要 8 个字符'
  if (value.length > 128) return '密码最多 128 个字符'
  if (!/[A-Za-z]/.test(value) || !/\d/.test(value)) return '密码必须同时包含字母和数字'
  return null
}
