export function formatDateTime(value: string | null | undefined): string {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '--'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRelative(value: string | null | undefined): string {
  if (!value) return '从未'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '从未'
  const seconds = Math.round((date.getTime() - Date.now()) / 1000)
  const table: Array<[Intl.RelativeTimeFormatUnit, number]> = [
    ['year', 31536000],
    ['month', 2592000],
    ['day', 86400],
    ['hour', 3600],
    ['minute', 60],
    ['second', 1],
  ]
  const formatter = new Intl.RelativeTimeFormat('zh-CN', { numeric: 'auto' })
  for (const [unit, size] of table) {
    if (Math.abs(seconds) >= size || unit === 'second') {
      return formatter.format(Math.round(seconds / size), unit)
    }
  }
  return '刚刚'
}

export function formatLatency(value: number | null | undefined): string {
  if (value === null || value === undefined) return '--'
  if (value < 1000) return `${value} ms`
  return `${(value / 1000).toFixed(1)} s`
}

export function formatClock(date: Date = new Date()): string {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '--'
  return new Intl.NumberFormat('zh-CN').format(value)
}

export function actionLabel(action: string): string {
  const labels: Record<string, string> = {
    'auth.login': '登录成功',
    'auth.login_failed': '登录失败',
    'auth.logout': '退出登录',
    'auth.change_password': '修改密码',
    'service.create': '新增服务',
    'service.update': '更新服务',
    'service.delete': '删除服务',
    'service.reorder': '调整排序',
    'service.check': '健康检测',
    'settings.update': '更新设置',
  }
  return labels[action] || action
}

export function actionTone(action: string): 'cyan' | 'lime' | 'amber' | 'red' | 'violet' {
  if (action.includes('failed')) return 'red'
  if (action.includes('delete') || action.includes('logout')) return 'amber'
  if (action.includes('create') || action.includes('login')) return 'lime'
  if (action.includes('update') || action.includes('settings')) return 'violet'
  return 'cyan'
}
