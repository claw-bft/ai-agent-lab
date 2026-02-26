import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  CheckSquare,
  Zap,
  MessageSquare,
  Settings,
  ChevronLeft,
  ChevronRight,
  Terminal
} from 'lucide-react'

interface SidebarProps {
  collapsed: boolean
  setCollapsed: (collapsed: boolean) => void
}

const navItems = [
  { path: '/', icon: LayoutDashboard, label: '概览' },
  { path: '/tasks', icon: CheckSquare, label: '任务' },
  { path: '/skills', icon: Zap, label: '技能' },
  { path: '/chat', icon: MessageSquare, label: '终端' },
  { path: '/settings', icon: Settings, label: '设置' },
]

export default function Sidebar({ collapsed, setCollapsed }: SidebarProps) {
  return (
    <aside
      className={`fixed left-0 top-0 h-full bg-surface border-r border-border z-50 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center glow">
              <Terminal className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <span className="font-bold text-lg gradient-text">OpenClaw</span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2">
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-primary/20 text-primary border border-primary/30'
                        : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
                    }`
                  }
                  title={collapsed ? item.label : undefined}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  {!collapsed && <span className="font-medium">{item.label}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Collapse Button */}
        <div className="p-2 border-t border-border">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-all duration-200"
          >
            {collapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <>
                <ChevronLeft className="w-5 h-5" />
                <span className="text-sm">收起侧边栏</span>
              </>
            )}
          </button>
        </div>
      </div>
    </aside>
  )
}
