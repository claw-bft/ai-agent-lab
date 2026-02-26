import { 
  Bot, 
  Cpu, 
  HardDrive, 
  Activity, 
  CheckCircle2, 
  XCircle, 
  Clock,
  MoreVertical,
  Power,
  RefreshCw
} from 'lucide-react'
import clsx from 'clsx'

interface Agent {
  id: string
  name: string
  status: 'busy' | 'idle' | 'offline'
  type: string
  cpu: number
  memory: number
  tasksCompleted: number
}

interface AgentsProps {
  agents: Agent[]
}

const statusConfig = {
  busy: { icon: Activity, color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'Busy' },
  idle: { icon: Clock, color: 'text-green-400', bg: 'bg-green-500/10', label: 'Idle' },
  offline: { icon: XCircle, color: 'text-slate-400', bg: 'bg-slate-500/10', label: 'Offline' },
}

const typeColors: Record<string, string> = {
  Worker: 'bg-purple-500/10 text-purple-400',
  Analyzer: 'bg-orange-500/10 text-orange-400',
  Coordinator: 'bg-pink-500/10 text-pink-400',
}

export default function Agents({ agents }: AgentsProps) {
  const stats = {
    total: agents.length,
    busy: agents.filter(a => a.status === 'busy').length,
    idle: agents.filter(a => a.status === 'idle').length,
    offline: agents.filter(a => a.status === 'offline').length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Agents</h1>
          <p className="text-slate-400 mt-1">Manage your agent fleet</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2">
          <Power className="w-4 h-4" />
          Deploy Agent
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Total</p>
              <p className="text-xl font-bold text-slate-100">{stats.total}</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Busy</p>
              <p className="text-xl font-bold text-slate-100">{stats.busy}</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Idle</p>
              <p className="text-xl font-bold text-slate-100">{stats.idle}</p>
            </div>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-500/10 rounded-lg flex items-center justify-center">
              <XCircle className="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Offline</p>
              <p className="text-xl font-bold text-slate-100">{stats.offline}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {agents.map((agent) => {
          const StatusIcon = statusConfig[agent.status].icon
          return (
            <div
              key={agent.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={clsx(
                    'w-12 h-12 rounded-xl flex items-center justify-center',
                    agent.status === 'offline' ? 'bg-slate-800' : 'bg-blue-600'
                  )}>
                    <Bot className={clsx('w-6 h-6', agent.status === 'offline' ? 'text-slate-500' : 'text-white')} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-100">{agent.name}</h3>
                    <span className={clsx('inline-flex px-2 py-0.5 rounded text-xs font-medium mt-1', typeColors[agent.type] || 'bg-slate-700 text-slate-300')}>
                      {agent.type}
                    </span>
                  </div>
                </div>
                <button className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors">
                  <MoreVertical className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-4 flex items-center gap-2">
                <div className={clsx('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-sm', statusConfig[agent.status].bg)}>
                  <StatusIcon className={clsx('w-4 h-4', statusConfig[agent.status].color)} />
                  <span className={statusConfig[agent.status].color}>{statusConfig[agent.status].label}</span>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-slate-400">
                    <Cpu className="w-4 h-4" />
                    CPU
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={clsx(
                        'h-full rounded-full transition-all',
                        agent.cpu > 80 ? 'bg-red-500' :
                        agent.cpu > 60 ? 'bg-yellow-500' :
                        'bg-green-500'
                      )}
                      style={{ width: `${agent.cpu}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Usage</span>
                    <span className={clsx(
                      'font-medium',
                      agent.cpu > 80 ? 'text-red-400' :
                      agent.cpu > 60 ? 'text-yellow-400' :
                      'text-green-400'
                    )}>
                      {agent.cpu}%
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-slate-400">
                    <HardDrive className="w-4 h-4" />
                    Memory
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={clsx(
                        'h-full rounded-full transition-all',
                        agent.memory > 80 ? 'bg-red-500' :
                        agent.memory > 60 ? 'bg-yellow-500' :
                        'bg-blue-500'
                      )}
                      style={{ width: `${agent.memory}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Usage</span>
                    <span className={clsx(
                      'font-medium',
                      agent.memory > 80 ? 'text-red-400' :
                      agent.memory > 60 ? 'text-yellow-400' :
                      'text-blue-400'
                    )}>
                      {agent.memory}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{agent.tasksCompleted} tasks completed</span>
                </div>
                <button className="p-2 text-slate-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors">
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}