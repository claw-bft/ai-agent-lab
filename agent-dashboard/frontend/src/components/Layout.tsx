import { 
  LayoutDashboard, 
  ListTodo, 
  Bot, 
  Settings, 
  Menu,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import clsx from 'clsx'

interface LayoutProps {
  children: React.ReactNode
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
}

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/tasks', icon: ListTodo, label: 'Tasks' },
  { path: '/agents', icon: Bot, label: 'Agents' },
]

export default function Layout({ children, sidebarOpen, setSidebarOpen }: LayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-50 bg-slate-900 border-r border-slate-800 transition-all duration-300 ease-in-out lg:static',
          sidebarOpen ? 'w-64' : 'w-0 lg:w-16'
        )}
      >
        <div className={clsx('h-full flex flex-col', !sidebarOpen && 'lg:items-center')} >
          {/* Logo */}
          <div className="h-16 flex items-center px-4 border-b border-slate-800">
            {sidebarOpen ? (
              <>
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <span className="ml-3 font-semibold text-lg text-slate-100">AgentHub</span>
              </>
            ) : (
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 py-4 px-2 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center px-3 py-2.5 rounded-lg transition-colors',
                    isActive
                      ? 'bg-blue-600/10 text-blue-400'
                      : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200',
                    !sidebarOpen && 'lg:justify-center lg:px-2'
                  )
                }
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && <span className="ml-3">{item.label}</span>}
              </NavLink>
            ))}
          </nav>

          {/* Settings */}
          <div className="p-2 border-t border-slate-800">
            <button
              className={clsx(
                'flex items-center w-full px-3 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors',
                !sidebarOpen && 'lg:justify-center lg:px-2'
              )}
            >
              <Settings className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && <span className="ml-3">Settings</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 bg-slate-900/50 backdrop-blur-sm border-b border-slate-800 flex items-center px-4 lg:px-6">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            {sidebarOpen ? (
              <ChevronLeft className="w-5 h-5" />
            ) : (
              <ChevronRight className="w-5 h-5" />
            )}
          </button>
          
          <div className="ml-auto flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              System Online
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 lg:p-6 overflow-auto scrollbar-thin">
          {children}
        </main>
      </div>
    </div>
  )
}