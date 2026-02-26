import type React from 'react';
import type { Task } from '../types';
import { Play, CheckCircle, XCircle, Clock } from 'lucide-react';

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  title: string;
  emptyText?: string;
}

export const TaskList: React.FC<TaskListProps> = ({ tasks, loading, title, emptyText = '暂无任务' }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'running':
        return <Play className="w-4 h-4 text-primary-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-success" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-danger" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-warning" />;
      default:
        return null;
    }
  };

  const getStatusClass = (status: Task['status']) => {
    switch (status) {
      case 'running':
        return 'bg-primary-50 text-primary-700 border-primary-200';
      case 'completed':
        return 'bg-success/10 text-success border-success/20';
      case 'failed':
        return 'bg-danger/10 text-danger border-danger/20';
      case 'pending':
        return 'bg-warning/10 text-warning border-warning/20';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return '-';
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <span className="text-sm text-gray-500">共 {tasks.length} 个</span>
      </div>

      {tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          {emptyText}
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="flex items-center justify-between p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                {getStatusIcon(task.status)}
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800 truncate">
                    {task.input.substring(0, 50)}{task.input.length > 50 ? '...' : ''}
                  </p>
                  <p className="text-sm text-gray-500">
                    {task.agentName} · {new Date(task.startTime).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusClass(task.status)}`}>
                  {task.status === 'running' && '运行中'}
                  {task.status === 'completed' && '已完成'}
                  {task.status === 'failed' && '失败'}
                  {task.status === 'pending' && '等待中'}
                </span>
                <span className="text-sm text-gray-500">
                  {formatDuration(task.duration)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};