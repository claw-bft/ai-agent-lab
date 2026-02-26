import { Zap, FileText, Settings, ExternalLink } from 'lucide-react'

export interface Skill {
  name: string
  description: string
  version: string
  author: string
  category: string
  tags: string[]
  global: boolean
}

interface SkillCardProps {
  skill: Skill
}

const categoryColors: Record<string, string> = {
  communication: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  productivity: 'bg-green-500/20 text-green-400 border-green-500/30',
  media: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  utility: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  ai: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  default: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

export default function SkillCard({ skill }: SkillCardProps) {
  const categoryClass = categoryColors[skill.category] || categoryColors.default

  return (
    <div className="bg-surface border border-border rounded-xl p-5 card-hover group">
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center group-hover:from-primary/30 group-hover:to-secondary/30 transition-all duration-300">
          <Zap className="w-6 h-6 text-primary" />
        </div>
        <div className="flex items-center gap-2">
          {skill.global ? (
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-primary/20 text-primary border border-primary/30">
              全局
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-secondary/20 text-secondary border border-secondary/30">
              本地
            </span>
          )}
          <span className={`px-2 py-0.5 rounded text-xs font-medium border ${categoryClass}`}>
            {skill.category}
          </span>
        </div>
      </div>

      <h3 className="text-lg font-semibold text-text-primary mb-1">{skill.name}</h3>
      <p className="text-sm text-text-secondary mb-3">{skill.description}</p>

      <div className="flex items-center justify-between text-xs text-muted mb-4">
        <div className="flex items-center gap-3">
          <span>版本 {skill.version}</span>
          <span>•</span>
          <span>{skill.author}</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {skill.tags.slice(0, 3).map((tag) => (
          <span
            key={tag}
            className="px-2 py-1 rounded-md text-xs bg-surface-hover text-text-secondary border border-border"
          >
            {tag}
          </span>
        ))}
        {skill.tags.length > 3 && (
          <span className="px-2 py-1 rounded-md text-xs bg-surface-hover text-muted">
            +{skill.tags.length - 3}
          </span>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
        <button className="flex items-center gap-1 text-sm text-primary hover:text-primary-hover transition-colors">
          <FileText className="w-4 h-4" />
          文档
        </button>
        <button className="flex items-center gap-1 text-sm text-text-secondary hover:text-text-primary transition-colors">
          <Settings className="w-4 h-4" />
          配置
        </button>
      </div>
    </div>
  )
}
