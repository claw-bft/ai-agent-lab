import { useState } from 'react'
import {
  User,
  Bell,
  Shield,
  Globe,
  Palette,
  Database,
  Key,
  Save,
  RefreshCw,
  CheckCircle,
  Moon,
  Sun,
  Monitor,
  Laptop
} from 'lucide-react'

interface SettingSection {
  id: string
  title: string
  icon: React.ElementType
  description: string
}

const sections: SettingSection[] = [
  { id: 'general', title: '常规', icon: User, description: '基本用户设置' },
  { id: 'notifications', title: '通知', icon: Bell, description: '消息和提醒设置' },
  { id: 'appearance', title: '外观', icon: Palette, description: '主题和显示选项' },
  { id: 'security', title: '安全', icon: Shield, description: '安全和隐私设置' },
  { id: 'integrations', title: '集成', icon: Globe, description: '第三方服务连接' },
  { id: 'storage', title: '存储', icon: Database, description: '数据和缓存管理' },
]

export default function Settings() {
  const [activeSection, setActiveSection] = useState('general')
  const [saved, setSaved] = useState(false)
  const [settings, setSettings] = useState({
    username: 'admin',
    email: 'admin@openclaw.local',
    language: 'zh-CN',
    theme: 'dark',
    notifications: true,
    soundEffects: true,
    autoUpdate: true,
    compactMode: false,
  })

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const renderSettingContent = () => {
    switch (activeSection) {
      case 'general':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">用户名</label>
              <input
                type="text"
                value={settings.username}
                onChange={(e) => setSettings({ ...settings, username: e.target.value })}
                className="input-dark w-full max-w-md"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">邮箱</label>
              <input
                type="email"
                value={settings.email}
                onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                className="input-dark w-full max-w-md"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">语言</label>
              <select
                value={settings.language}
                onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                className="input-dark w-full max-w-md"
              >
                <option value="zh-CN">简体中文</option>
                <option value="en-US">English</option>
                <option value="ja-JP">日本語</option>
              </select>
            </div>

            <div className="flex items-center justify-between py-4 border-t border-border">
              <div>
                <p className="font-medium text-text-primary">自动更新</p>
                <p className="text-sm text-muted">自动检查并安装更新</p>
              </div>
              <button
                onClick={() => setSettings({ ...settings, autoUpdate: !settings.autoUpdate })}
                className={`relative w-12 h-6 rounded-full transition-colors ${settings.autoUpdate ? 'bg-primary' : 'bg-surface-hover'}`}
              >
                <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${settings.autoUpdate ? 'left-7' : 'left-1'}`} />
              </button>
            </div>
          </div>
        )
      
      case 'appearance':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-4">主题</label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { id: 'dark', label: '深色', icon: Moon },
                  { id: 'light', label: '浅色', icon: Sun },
                  { id: 'system', label: '跟随系统', icon: Monitor },
                ].map((theme) => (
                  <button
                    key={theme.id}
                    onClick={() => setSettings({ ...settings, theme: theme.id })}
                    className={`p-4 rounded-xl border transition-all ${
                      settings.theme === theme.id
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-border-hover'
                    }`}
                  >
                    <theme.icon className={`w-6 h-6 mx-auto mb-2 ${settings.theme === theme.id ? 'text-primary' : 'text-muted'}`} />
                    <p className={`text-sm ${settings.theme === theme.id ? 'text-primary' : 'text-text-secondary'}`}>
                      {theme.label}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between py-4 border-t border-border">
              <div>
                <p className="font-medium text-text-primary">紧凑模式</p>
                <p className="text-sm text-muted">减小间距和元素大小</p>
              </div>
              <button
                onClick={() => setSettings({ ...settings, compactMode: !settings.compactMode })}
                className={`relative w-12 h-6 rounded-full transition-colors ${settings.compactMode ? 'bg-primary' : 'bg-surface-hover'}`}
              >
                <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${settings.compactMode ? 'left-7' : 'left-1'}`} />
              </button>
            </div>
          </div>
        )
      
      case 'notifications':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between py-4">
              <div>
                <p className="font-medium text-text-primary">启用通知</p>
                <p className="text-sm text-muted">接收系统和任务通知</p>
              </div>
              <button
                onClick={() => setSettings({ ...settings, notifications: !settings.notifications })}
                className={`relative w-12 h-6 rounded-full transition-colors ${settings.notifications ? 'bg-primary' : 'bg-surface-hover'}`}
              >
                <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${settings.notifications ? 'left-7' : 'left-1'}`} />
              </button>
            </div>

            <div className="flex items-center justify-between py-4 border-t border-border">
              <div>
                <p className="font-medium text-text-primary">音效</p>
                <p className="text-sm text-muted">播放操作音效</p>
              </div>
              <button
                onClick={() => setSettings({ ...settings, soundEffects: !settings.soundEffects })}
                className={`relative w-12 h-6 rounded-full transition-colors ${settings.soundEffects ? 'bg-primary' : 'bg-surface-hover'}`}
              >
                <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${settings.soundEffects ? 'left-7' : 'left-1'}`} />
              </button>
            </div>
          </div>
        )
      
      case 'security':
        return (
          <div className="space-y-6">
            <div className="p-4 rounded-xl bg-surface-hover border border-border">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-success" />
                </div>
                <div>
                  <p className="font-medium text-text-primary">安全状态</p>
                  <p className="text-sm text-muted">您的账户是安全的</p>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">API 密钥</label>
              <div className="flex gap-2">
                <input
                  type="password"
                  value="sk-••••••••••••••••••••••••••••••"
                  readOnly
                  className="input-dark flex-1"
                />
                <button className="btn-secondary">
                  <Key className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-error/5 border border-error/20">
              <p className="font-medium text-error mb-2">危险区域</p>
              <p className="text-sm text-text-secondary mb-4">这些操作不可逆，请谨慎操作。</p>
              <div className="flex gap-2">
                <button className="px-4 py-2 rounded-lg bg-error/10 text-error hover:bg-error/20 transition-colors">
                  清除所有数据
                </button>
                <button className="px-4 py-2 rounded-lg bg-error/10 text-error hover:bg-error/20 transition-colors">
                  重置设置
                </button>
              </div>
            </div>
          </div>
        )
      
      case 'integrations':
        return (
          <div className="space-y-4">
            {[
              { name: 'GitHub', description: '代码仓库访问', connected: true, icon: 'GH' },
              { name: 'Discord', description: '消息发送', connected: true, icon: 'DC' },
              { name: 'OpenAI', description: 'AI 服务', connected: true, icon: 'AI' },
              { name: 'Feishu', description: '飞书集成', connected: false, icon: 'FS' },
            ].map((integration) => (
              <div
                key={integration.name}
                className="flex items-center justify-between p-4 rounded-xl bg-surface-hover border border-border"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold">
                    {integration.icon}
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">{integration.name}</p>
                    <p className="text-sm text-muted">{integration.description}</p>
                  </div>
                </div>
                <button
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    integration.connected
                      ? 'bg-success/10 text-success hover:bg-success/20'
                      : 'bg-primary text-white hover:bg-primary-hover'
                  }`}
                >
                  {integration.connected ? '已连接' : '连接'}
                </button>
              </div>
            ))}
          </div>
        )
      
      case 'storage':
        return (
          <div className="space-y-6">
            <div className="p-4 rounded-xl bg-surface-hover border border-border">
              <div className="flex items-center justify-between mb-2">
                <span className="text-text-primary">存储使用</span>
                <span className="text-muted">2.4 GB / 10 GB</span>
              </div>
              <div className="h-2 bg-background rounded-full overflow-hidden">
                <div className="h-full w-1/4 bg-primary rounded-full" />
              </div>
            </div>

            <div className="space-y-2">
              {[
                { label: '任务数据', size: '156 MB' },
                { label: '技能缓存', size: '432 MB' },
                { label: '日志文件', size: '1.2 GB' },
                { label: '临时文件', size: '612 MB' },
              ].map((item) => (
                <div
                  key={item.label}
                  className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-surface-hover transition-colors"
                >
                  <span className="text-text-secondary">{item.label}</span>
                  <span className="text-muted">{item.size}</span>
                </div>
              ))}
            </div>

            <div className="flex gap-2 pt-4 border-t border-border">
              <button className="btn-secondary flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
                清理缓存
              </button>
              <button className="btn-secondary flex items-center gap-2">
                <Database className="w-4 h-4" />
                导出数据
              </button>
            </div>
          </div>
        )
      
      default:
        return null
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">系统设置</h1>
        <p className="text-text-secondary mt-1">配置您的 OpenClaw 控制面板</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-64 space-y-1">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                activeSection === section.id
                  ? 'bg-primary/10 text-primary border border-primary/30'
                  : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
              }`}
            >
              <section.icon className="w-5 h-5" />
              <div className="text-left">
                <p className="font-medium">{section.title}</p>
                <p className="text-xs opacity-70">{section.description}</p>
              </div>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="bg-surface border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-text-primary">
                {sections.find(s => s.id === activeSection)?.title}
              </h2>
              <button
                onClick={handleSave}
                className={`btn-primary flex items-center gap-2 ${saved ? 'bg-success' : ''}`}
              >
                {saved ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    已保存
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    保存
                  </>
                )}
              </button>
            </div>

            {renderSettingContent()}
          </div>
        </div>
      </div>
    </div>
  )
}
