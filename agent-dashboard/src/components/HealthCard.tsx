import type React from 'react';
import type { SystemHealth } from '../types';
import { Activity, Users, Clock, AlertCircle } from 'lucide-react';

interface HealthCardProps {
  health: SystemHealth | null;
  loading: boolean;
}

export const HealthCard: React.FC<HealthCardProps> = ({ health, loading }) => {
  if (loading || !health) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  const getStatusColor = () => {
    switch (health.status) {
      case 'healthy': return 'bg-success';
      case 'warning': return 'bg-warning';
      case 'critical': return 'bg-danger';
      default: return 'bg-gray-400';
    }
  };

  const getStatusText = () => {
    switch (health.status) {
      case 'healthy': return '系统健康';
      case 'warning': return '警告';
      case 'critical': return '严重';
      default: return '未知';
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-800">系统健康状态</h2>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
          <span className="text-sm font-medium text-gray-600">{getStatusText()}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-50 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Activity className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">活跃会话</p>
              <p className="text-2xl font-bold text-gray-800">{health.activeSessions}</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-success/10 rounded-lg">
              <Users className="w-5 h-5 text-success" />
            </div>
            <div>
              <p className="text-sm text-gray-500">运行中任务</p>
              <p className="text-2xl font-bold text-gray-800">{health.runningTasks}</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-warning/10 rounded-lg">
              <Clock className="w-5 h-5 text-warning" />
            </div>
            <div>
              <p className="text-sm text-gray-500">队列任务</p>
              <p className="text-2xl font-bold text-gray-800">{health.queuedTasks}</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-info/10 rounded-lg">
              <AlertCircle className="w-5 h-5 text-info" />
            </div>
            <div>
              <p className="text-sm text-gray-500">运行时间</p>
              <p className="text-2xl font-bold text-gray-800">{formatUptime(health.uptime)}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-500">CPU 使用率</span>
            <span className="font-medium">{health.cpuUsage.toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 transition-all duration-500"
              style={{ width: `${Math.min(health.cpuUsage, 100)}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-500">内存使用率</span>
            <span className="font-medium">{health.memoryUsage.toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-success transition-all duration-500"
              style={{ width: `${Math.min(health.memoryUsage, 100)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};