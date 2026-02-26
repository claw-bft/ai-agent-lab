import { Bell, Search, User, Menu } from 'lucide-react'

interface HeaderProps {
  sidebarCollapsed: boolean
}

export default function Header({ sidebarCollapsed }: HeaderProps) {
  return (
    <header className="h-16 bg-surface/50 backdrop-blur-md border-b border-border flex items-center justify-between px-6 sticky top-0 z-40">
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="搜索..."
            className="input-dark pl-10 w-64"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="relative p-2 rounded-lg text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-all duration-200">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full animate-pulse"></span>
        </button>

        <div className="flex items-center gap-3 pl-4 border-l border-border">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-text-primary">管理员</p>
            <p className="text-xs text-muted">在线</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
        </div>
      </div>
    </header>
  )
}
