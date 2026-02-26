import { useState, useEffect } from 'react'
import {
  Search,
  Filter,
  Grid,
  List,
  Download,
  RefreshCw,
  Globe,
  Folder,
  Zap,
  CheckCircle,
  XCircle,
  Settings,
  ExternalLink,
  Package
} from 'lucide-react'
import SkillCard, { type Skill } from '../components/SkillCard'

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [sourceFilter, setSourceFilter] = useState<'all' | 'global' | 'local'>('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading skills from directories
    setTimeout(() => {
      const mockSkills: Skill[] = [
        // Communication
        { name: 'discord', description: 'Discord bot integration for sending messages and managing channels', version: '1.0.0', author: 'OpenClaw', category: 'communication', tags: ['chat', 'bot', 'messaging'], global: true },
        { name: 'slack', description: 'Slack workspace integration', version: '1.1.0', author: 'OpenClaw', category: 'communication', tags: ['chat', 'workspace'], global: true },
        { name: 'feishu', description: 'Feishu/Lark enterprise messaging platform integration', version: '1.0.5', author: 'OpenClaw', category: 'communication', tags: ['docs', 'chat', 'enterprise'], global: true },
        { name: 'imsg', description: 'iMessage integration for macOS', version: '0.9.0', author: 'Community', category: 'communication', tags: ['macos', 'messaging'], global: true },
        
        // Productivity
        { name: 'github', description: 'GitHub repository and issue management', version: '1.2.0', author: 'OpenClaw', category: 'productivity', tags: ['git', 'api', 'dev'], global: true },
        { name: 'notion', description: 'Notion workspace integration', version: '1.0.0', author: 'OpenClaw', category: 'productivity', tags: ['docs', 'wiki'], global: true },
        { name: 'trello', description: 'Trello board management', version: '0.8.0', author: 'Community', category: 'productivity', tags: ['kanban', 'project'], global: true },
        { name: 'obsidian', description: 'Obsidian vault operations', version: '1.0.0', author: 'OpenClaw', category: 'productivity', tags: ['notes', 'markdown'], global: true },
        
        // Media
        { name: 'openai-image-gen', description: 'DALL-E image generation', version: '1.0.0', author: 'OpenClaw', category: 'media', tags: ['ai', 'image', 'generation'], global: true },
        { name: 'openai-whisper', description: 'Whisper speech-to-text transcription', version: '1.0.0', author: 'OpenClaw', category: 'media', tags: ['audio', 'transcription', 'ai'], global: true },
        { name: 'spotify-player', description: 'Spotify playback control', version: '0.9.0', author: 'Community', category: 'media', tags: ['music', 'audio'], global: true },
        { name: 'video-frames', description: 'Extract frames from video files', version: '1.0.0', author: 'OpenClaw', category: 'media', tags: ['video', 'processing'], global: true },
        
        // Utility
        { name: 'weather', description: 'Weather information and forecasts', version: '0.9.0', author: 'Community', category: 'utility', tags: ['api', 'data', 'forecast'], global: true },
        { name: '1password', description: '1Password vault access', version: '1.0.0', author: 'OpenClaw', category: 'utility', tags: ['security', 'password'], global: true },
        { name: 'tmux', description: 'Tmux session management', version: '1.0.0', author: 'OpenClaw', category: 'utility', tags: ['terminal', 'session'], global: true },
        { name: 'canvas', description: 'Canvas presentation and screenshots', version: '1.0.0', author: 'OpenClaw', category: 'utility', tags: ['visual', 'screenshot'], global: true },
        
        // AI
        { name: 'gemini', description: 'Google Gemini AI integration', version: '1.0.0', author: 'OpenClaw', category: 'ai', tags: ['llm', 'google', 'ai'], global: true },
        { name: 'sag', description: 'ElevenLabs text-to-speech', version: '1.0.0', author: 'OpenClaw', category: 'ai', tags: ['tts', 'voice', 'audio'], global: true },
        { name: 'summarize', description: 'AI-powered text summarization', version: '1.0.0', author: 'OpenClaw', category: 'ai', tags: ['nlp', 'text', 'ai'], global: true },
        { name: 'coding-agent', description: 'AI coding assistant', version: '1.0.0', author: 'OpenClaw', category: 'ai', tags: ['code', 'development', 'ai'], global: true },
        
        // Local skills
        { name: 'vercel-deploy', description: 'Deploy projects to Vercel', version: '1.0.0', author: 'User', category: 'productivity', tags: ['deploy', 'vercel', 'web'], global: false },
        { name: 'channels-setup', description: 'Channel configuration helper', version: '0.5.0', author: 'User', category: 'utility', tags: ['config', 'setup'], global: false },
      ]
      setSkills(mockSkills)
      setLoading(false)
    }, 800)
  }, [])

  const categories = ['all', ...Array.from(new Set(skills.map(s => s.category)))]

  const filteredSkills = skills.filter((skill) => {
    const matchesSearch = skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         skill.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         skill.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesCategory = categoryFilter === 'all' || skill.category === categoryFilter
    const matchesSource = sourceFilter === 'all' || 
                         (sourceFilter === 'global' && skill.global) ||
                         (sourceFilter === 'local' && !skill.global)
    return matchesSearch && matchesCategory && matchesSource
  })

  const stats = {
    total: skills.length,
    global: skills.filter(s => s.global).length,
    local: skills.filter(s => !s.global).length,
    categories: new Set(skills.map(s => s.category)).size,
  }

  const categoryLabels: Record<string, string> = {
    all: '全部',
    communication: '通讯',
    productivity: '生产力',
    media: '媒体',
    utility: '工具',
    ai: 'AI',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
          <p className="text-text-secondary">加载技能中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">技能管理</h1>
          <p className="text-text-secondary mt-1">浏览和管理您的 OpenClaw 技能</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            刷新
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Download className="w-4 h-4" />
            安装技能
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '总技能', value: stats.total, icon: Zap, color: 'text-primary', bg: 'bg-primary/10' },
          { label: '全局技能', value: stats.global, icon: Globe, color: 'text-accent', bg: 'bg-accent/10' },
          { label: '本地技能', value: stats.local, icon: Folder, color: 'text-warning', bg: 'bg-warning/10' },
          { label: '分类', value: stats.categories, icon: Package, color: 'text-secondary', bg: 'bg-secondary/10' },
        ].map((stat) => (
          <div key={stat.label} className="bg-surface border border-border rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg ${stat.bg} flex items-center justify-center`}>
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div>
                <p className="text-muted text-sm">{stat.label}</p>
                <p className="text-2xl font-bold text-text-primary">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-surface border border-border rounded-xl p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input
              type="text"
              placeholder="搜索技能..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-dark pl-10 w-full"
            />
          </div>
          
          <div className="flex gap-2 flex-wrap">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="input-dark"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {categoryLabels[cat] || cat}
                </option>
              ))}
            </select>
            
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value as 'all' | 'global' | 'local')}
              className="input-dark"
            >
              <option value="all">所有来源</option>
              <option value="global">全局</option>
              <option value="local">本地</option>
            </select>
            
            <div className="flex items-center gap-1 bg-background border border-border rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded transition-colors ${viewMode === 'grid' ? 'bg-surface-hover text-text-primary' : 'text-muted hover:text-text-primary'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded transition-colors ${viewMode === 'list' ? 'bg-surface-hover text-text-primary' : 'text-muted hover:text-text-primary'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Skills Grid/List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <p className="text-muted text-sm">
            显示 {filteredSkills.length} 个技能
          </p>
        </div>

        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredSkills.map((skill) => (
              <SkillCard key={skill.name} skill={skill} />
            ))}
          </div>
        ) : (
          <div className="bg-surface border border-border rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface-hover">
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">技能</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">分类</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">来源</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">版本</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-muted">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredSkills.map((skill) => (
                  <tr key={skill.name} className="border-b border-border/50 hover:bg-surface-hover/50 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                          <Zap className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                          <div className="font-medium text-text-primary">{skill.name}</div>
                          <div className="text-sm text-muted">{skill.description.slice(0, 50)}...</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 rounded text-xs bg-surface-hover text-text-secondary border border-border">
                        {categoryLabels[skill.category] || skill.category}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1 text-xs ${skill.global ? 'text-accent' : 'text-warning'}`}>
                        {skill.global ? <Globe className="w-3 h-3" /> : <Folder className="w-3 h-3" />}
                        {skill.global ? '全局' : '本地'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-muted">{skill.version}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end gap-1">
                        <button className="p-1.5 rounded hover:bg-surface-hover text-muted hover:text-text-primary transition-colors">
                          <Settings className="w-4 h-4" />
                        </button>
                        <button className="p-1.5 rounded hover:bg-surface-hover text-muted hover:text-text-primary transition-colors">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {filteredSkills.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-full bg-surface border border-border flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-muted" />
            </div>
            <p className="text-text-secondary">没有找到匹配的技能</p>
            <button
              onClick={() => {
                setSearchQuery('')
                setCategoryFilter('all')
                setSourceFilter('all')
              }}
              className="mt-2 text-primary hover:text-primary-hover"
            >
              清除筛选
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
