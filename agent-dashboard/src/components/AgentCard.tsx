import type React from 'react';
import type { Agent } from '../types';
import { User, CheckCircle, XCircle, Activity } from 'lucide-react';

interface AgentCardProps {
  agent: Agent;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent }) => {
  const getStatusColor = () => {
    switch (agent.status) {
      case 'active': return 'bg-success';
      case 'busy': return 'bg-warning';
      case 'idle': return 'bg-gray-400';
      case 'error': return 'bg-danger';
      default: return 'bg-gray-400';
    }
  };

  const getStatusText = () => {
    switch (agent.status) {
      case 'active': return '活跃';
      case 'busy': return '忙碌';
      case 'idle': return '空闲';
      case 'error': return '错误';
      default: return '未知';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-primary-100 rounded-xl">
            <User className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800">{agent.name}</h3>
            <p className="text-sm text-gray-500">ID: {agent.id.slice(0, 8)}...</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2.5 h-2.5 rounded-full ${getStatusColor()}`}></div>
          <span className="text-sm font-medium text-gray-600">{getStatusText()}</span>
        </div>
      </div>

      {agent.currentTask && (
        <div className="mb-4 p-3 bg-slate-50 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">当前任务</p>
          <p className="text-sm text-gray-700 truncate">{agent.currentTask}</p>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="p-2 bg-slate-50 rounded-lg">
          <div className="flex items-center justify-center gap-1 mb-1">
            <CheckCircle className="w-3.5 h-3.5 text-success" />
            <span className="text-lg font-bold text-gray-800">{agent.completedTasks}</span>
          </div>
          <p className="text-xs text-gray-500">已完成</p>
        </div>

        <div className="p-2 bg-slate-50 rounded-lg">
          <div className="flex items-center justify-center gap-1 mb-1">
            <XCircle className="w-3.5 h-3.5 text-danger" />
            <span className="text-lg font-bold text-gray-800">{agent.failedTasks}</span>
          </div>
          <p className="text-xs text-gray-500">失败</p>
        </div>

        <div className="p-2 bg-slate-50 rounded-lg">
          <div className="flex items-center justify-center gap-1 mb-1">
            <Activity className="w-3.5 h-3.5 text-primary-500" />
            <span className="text-lg font-bold text-gray-800">{(agent.totalTokens / 1000).toFixed(1)}k</span>
          </div>
          <p className="text-xs text-gray-500">Tokens</p>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">平均响应</span>
          <span className="font-medium">{agent.avgResponseTime.toFixed(0)}ms</span>
        </div>
        <div className="flex justify-between text-sm mt-1">
          <span className="text-gray-500">最后活跃</span>
          <span className="font-medium">{new Date(agent.lastActive).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};