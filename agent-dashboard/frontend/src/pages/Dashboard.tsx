import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  CheckCircle2, 
  XCircle, 
  Clock,
  Bot
} from 'lucide-react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import clsx from 'clsx'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ElementType
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}

const colorMap = {
  blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  green: 'bg-green-500/10 text-green-400 border-green-500/20',
  yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  red: 'bg-red-500/10 text-red-400 border-red-500/20',
  purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
}

function StatCard({ title, value, change, icon: Icon, color }: StatCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <div className={clsx('p-3 rounded-lg border', colorMap[color])}>
          <Icon className="w-5 h-5" />
        </div>
        {change !== undefined && (
          <div
            className={clsx(
              'flex items-center gap-1 text-sm font-medium',
              change >= 0 ? 'text-green-400' : 'text-red-400'
            )}
          >
            {change >= 0 ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            {Math.abs(change)}%
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-slate-400 text-sm">{title}</p>
        <p className="text-2xl font-bold text-slate-100 mt-1">{value}</p>
      </div>
    </div>
  )
}

interface DashboardProps {
  stats: {
    totalAgents: number
    activeAgents: number
    totalTasks: number
    pendingTasks: number
    completedTasks: number
    failedTasks: number
  }
  chartData: {
    labels: string[]
    datasets: {
      label: string
      data: number[]
      borderColor: string
      backgroundColor: string
      fill: boolean
    }[]
  }
}

export default function Dashboard({ stats, chartData }: DashboardProps) {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#94a3b8',
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: {
          color: '#334155',
          drawBorder: false,
        },
        ticks: {
          color: '#94a3b8',
        },
      },
      y: {
        grid: {
          color: '#334155',
          drawBorder: false,
        },
        ticks: {
          color: '#94a3b8',
        },
      },
    },
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>
        <p className="text-slate-400 mt-1">Overview of your agent fleet and task status</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Agents"
          value={stats.totalAgents}
          change={12}
          icon={Bot}
          color="blue"
        />
        <StatCard
          title="Active Tasks"
          value={stats.totalTasks - stats.completedTasks - stats.failedTasks}
          change={8}
          icon={Activity}
          color="green"
        />
        <StatCard
          title="Pending Tasks"
          value={stats.pendingTasks}
          change={-5}
          icon={Clock}
          color="yellow"
        />
        <StatCard
          title="Failed Tasks"
          value={stats.failedTasks}
          change={-2}
          icon={XCircle}
          color="red"
        />
      </div>

      {/* Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-100">Task Activity</h2>
            <select className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>Last 24 hours</option>
              <option>Last 7 days</option>
              <option>Last 30 days</option>
            </select>
          </div>
          <div className="h-72">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-slate-100 mb-4">Task Summary</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Completed</p>
                  <p className="text-lg font-semibold text-slate-100">{stats.completedTasks}</p>
                </div>
              </div>
              <span className="text-green-400 text-sm">+12%</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-yellow-500/10 rounded-lg flex items-center justify-center">
                  <Clock className="w-5 h-5 text-yellow-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Pending</p>
                  <p className="text-lg font-semibold text-slate-100">{stats.pendingTasks}</p>
                </div>
              </div>
              <span className="text-yellow-400 text-sm">-5%</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-red-500/10 rounded-lg flex items-center justify-center">
                  <XCircle className="w-5 h-5 text-red-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Failed</p>
                  <p className="text-lg font-semibold text-slate-100">{stats.failedTasks}</p>
                </div>
              </div>
              <span className="text-red-400 text-sm">-2%</span>
            </div>

            <div className="pt-4 border-t border-slate-800">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Success Rate</span>
                <span className="text-slate-100 font-medium">92.3%</span>
              </div>
              <div className="mt-2 h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full" style={{ width: '92.3%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}