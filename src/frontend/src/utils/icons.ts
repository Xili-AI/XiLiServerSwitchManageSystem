import type { Component } from 'vue'
import {
  Activity,
  Boxes,
  Cloud,
  Container,
  Cpu,
  Database,
  FolderOpen,
  Globe,
  HardDrive,
  Server,
  Shield,
  Terminal,
} from 'lucide-vue-next'

export const SERVICE_ICONS: Record<string, Component> = {
  server: Server,
  container: Container,
  database: Database,
  folder: FolderOpen,
  terminal: Terminal,
  activity: Activity,
  cpu: Cpu,
  cloud: Cloud,
  shield: Shield,
  globe: Globe,
  'hard-drive': HardDrive,
  boxes: Boxes,
}

export const ICON_OPTIONS = [
  { value: 'server', label: '服务器' },
  { value: 'container', label: '容器' },
  { value: 'database', label: '数据库' },
  { value: 'folder', label: '文件' },
  { value: 'terminal', label: '终端' },
  { value: 'activity', label: '监控' },
  { value: 'cpu', label: '算力' },
  { value: 'cloud', label: '云服务' },
  { value: 'shield', label: '安全' },
  { value: 'globe', label: '网站' },
  { value: 'hard-drive', label: '存储' },
  { value: 'boxes', label: '应用' },
]

export function resolveServiceIcon(name: string): Component {
  return SERVICE_ICONS[name] || Server
}
