import { useState } from 'react'
import { 
  Search, 
  Filter, 
  MoreVertical, 
  Play, 
  Pause, 
  RotateCcw, 
  Trash2,
  X,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  AlertCircle
} from 'lucide-react'
import clsx from 'clsx'

interface Task {
  id: string
  title: string
  status: 'running' | 'pending' | 'completed' | 'failed'
  agent: string
  priority: 'high' | 'medium' | 'low'
  progress: number
  createdAt: string
}

interface TasksProps {
  tasks: Task[]
}

const statusConfig = {
  running: { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'Running' },
  pending: { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-500/10', label: 'Pending' },
  completed: { icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-500/10', label: 'Completed' },
  failed: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', label: 'Failed' },
}

const priorityConfig = {
  high: { color: 'text-red-400', bg: 'bg-red-500/10', label: 'High' },
  medium: { color: 'text-yellow-400', bg: 'bg-yellow-500/10', label: 'Medium' },
  low: { color: 'text-green-400', bg: 'bg-green-500/10', label: 'Low' },
}

export default function Tasks({ tasks }: TasksProps) {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Tasks</h1>
          <p className="text-slate-400 mt-1">Manage and monitor all tasks</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-medium transition-colors">
          + New Task
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-2.5 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="running">Running</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Task List */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left text-slate-400 font-medium py-4 px-4">Task</th>
                <th className="text-left text-slate-400 font-medium py-4 px-4">Status</th>
                <th className="text-left text-slate-400 font-medium py-4 px-4">Agent</th>
                <th className="text-left text-slate-400 font-medium py-4 px-4">Priority</th>
                <th className="text-left text-slate-400 font-medium py-4 px-4">Progress</th>
                <th className="text-left text-slate-400 font-medium py-4 px-4">Created</th>
                <th className="text-right text-slate-400 font-medium py-4 px-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredTasks.map((task) => {
                const StatusIcon = statusConfig[task.status].icon
                return (
                  <tr
                    key={task.id}
                    className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors cursor-pointer"
                    onClick={() => setSelectedTask(task)}
                  >
                    <td className="py-4 px-4">
                      <div className="font-medium text-slate-100">{task.title}</div>
                      <div className="text-sm text-slate-500">#{task.id}</div>
                    </td>
                    <td className="py-4 px-4">
                      <div className={clsx('inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm', statusConfig[task.status].bg)}>
                        <StatusIcon className={clsx('w-4 h-4', statusConfig[task.status].color, task.status === 'running' && 'animate-spin')} />
                        <span className={statusConfig[task.status].color}>{statusConfig[task.status].label}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-slate-300">{task.agent}</td>
                    <td className="py-4 px-4">
                      <span className={clsx('inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium', priorityConfig[task.priority].bg, priorityConfig[task.priority].color)}>
                        {priorityConfig[task.priority].label}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden w-24">
                          <div
                            className={clsx(
                              'h-full rounded-full transition-all',
                              task.status === 'completed' ? 'bg-green-500' :
                              task.status === 'failed' ? 'bg-red-500' :
                              'bg-blue-500'
                            )}
                            style={{ width: `${task.progress}%` }}
                          />
                        </div>
                        <span className="text-sm text-slate-400 w-10">{task.progress}%</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-slate-400 text-sm">{task.createdAt}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            // Handle play/pause
                          }}
                          className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
                        >
                          {task.status === 'running' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={(e) => e.stopPropagation()}
                          className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
                        >
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Task Detail Drawer */}
      {selectedTask && (
        <>
          <div
            className="fixed inset-0 bg-black/50 z-40"
            onClick={() => setSelectedTask(null)}
          />
          <div className="fixed right-0 top-0 h-full w-full max-w-md bg-slate-900 border-l border-slate-800 z-50 shadow-2xl">
            <div className="h-full flex flex-col">
              {/* Drawer Header */}
              <div className="flex items-center justify-between p-6 border-b border-slate-800">
                <div>
                  <h2 className="text-xl font-semibold text-slate-100">{selectedTask.title}</h2>
                  <p className="text-sm text-slate-400 mt-1">Task #{selectedTask.id}</p>
                </div>
                <button
                  onClick={() => setSelectedTask(null)}
                  className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Drawer Content */}
              <div className="flex-1 overflow-auto p-6 space-y-6">
                {/* Status */}
                <div className="space-y-2">
                  <label className="text-sm text-slate-400">Status</label>
                  <div className={clsx('inline-flex items-center gap-2 px-4 py-2 rounded-lg', statusConfig[selectedTask.status].bg)}>
                    {(() => {
                      const StatusIcon = statusConfig[selectedTask.status].icon
                      return <StatusIcon className={clsx('w-5 h-5', statusConfig[selectedTask.status].color, selectedTask.status === 'running' && 'animate-spin')} />
                    })()}
                    <span className={clsx('font-medium', statusConfig[selectedTask.status].color)}>
                      {statusConfig[selectedTask.status].label}
                    </span>
                  </div>
                </div>

                {/* Progress */}
                <div className="space-y-2">
                  <label className="text-sm text-slate-400">Progress</label>
                  <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={clsx(
                        'h-full rounded-full transition-all',
                        selectedTask.status === 'completed' ? 'bg-green-500' :
                        selectedTask.status === 'failed' ? 'bg-red-500' :
                        'bg-blue-500'
                      )}
                      style={{ width: `${selectedTask.progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Completion</span>
                    <span className="text-slate-100 font-medium">{selectedTask.progress}%</span>
                  </div>
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm text-slate-400">Assigned Agent</label>
                    <div className="bg-slate-800/50 rounded-lg px-4 py-3 text-slate-100">
                      {selectedTask.agent}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm text-slate-400">Priority</label>
                    <div className={clsx('rounded-lg px-4 py-3 font-medium', priorityConfig[selectedTask.priority].bg, priorityConfig[selectedTask.priority].color)}>
                      {priorityConfig[selectedTask.priority].label}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm text-slate-400">Created</label>
                    <div className="bg-slate-800/50 rounded-lg px-4 py-3 text-slate-100">
                      {selectedTask.createdAt}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm text-slate-400">Duration</label>
                    <div className="bg-slate-800/50 rounded-lg px-4 py-3 text-slate-100">
                      2h 34m
                    </div>
                  </div>
                </div>

                {/* Logs */}
                <div className="space-y-2">
                  <label className="text-sm text-slate-400">Recent Logs</label>
                  <div className="bg-slate-950 rounded-lg p-4 font-mono text-xs space-y-2">
                    <div className="text-slate-500">[10:30:15] Task initialized</div>
                    <div className="text-slate-500">[10:30:16] Agent assigned: {selectedTask.agent}</div>
                    <div className="text-blue-400">[10:30:20] Processing started</div>
                    <div className="text-slate-500">[10:32:45] Progress: 25%</div>
                    <div className="text-slate-500">[10:35:12] Progress: 50%</div>
                    <div className="text-slate-500">[10:37:30] Progress: {selectedTask.progress}%</div>
                  </div>
                </div>
              </div>

              {/* Drawer Footer */}
              <div className="p-6 border-t border-slate-800 space-y-3">
                <div className="flex gap-3">
                  <button className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2">
                    {selectedTask.status === 'running' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    {selectedTask.status === 'running' ? 'Pause' : 'Resume'}
                  </button>
                  <button className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-100 py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2">
                    <RotateCcw className="w-4 h-4" />
                    Restart
                  </button>
                </div>
                <button className="w-full bg-red-500/10 hover:bg-red-500/20 text-red-400 py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete Task
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}