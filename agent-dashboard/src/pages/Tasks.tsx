import type { FC } from 'react';
import { useState } from 'react';
import { TaskList } from '../components/TaskList';
import { usePolling } from '../hooks/usePolling';
import { taskService } from '../services/api';
import { Search, Filter } from 'lucide-react';
import type { Task } from '../types';

export const Tasks: FC = () => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<Task['status'] | 'all'>('all');
  const [agentFilter, setAgentFilter] = useState('all');

  const { data: allTasksData, loading } = usePolling(
    () => taskService.getAll({
      status: statusFilter === 'all' ? undefined : statusFilter,
      search: search || undefined,
    }),
    5000,
    [statusFilter, search]
  );

  const allTasks: Task[] = allTasksData || [];

  const filteredTasks = allTasks.filter(task => {
    if (agentFilter !== 'all' && task.agentId !== agentFilter) return false;
    return true;
  });

  // 获取所有唯一的agent
  const agents = Array.from(new Map(allTasks.map(t => [t.agentId, t.agentName])).entries());

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">任务管理</h1>
        <p className="text-gray-500">查看和管理所有Agent任务</p>
      </div>

      {/* 筛选栏 */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="搜索任务..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Task['status'] | 'all')}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">所有状态</option>
              <option value="running">运行中</option>
              <option value="completed">已完成</option>
              <option value="failed">失败</option>
              <option value="pending">等待中</option>
            </select>
          </div>

          <div>
            <select
              value={agentFilter}
              onChange={(e) => setAgentFilter(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">所有Agent</option>
              {agents.map(([id, name]) => (
                <option key={id} value={id}>{name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 任务列表 */}
      <TaskList
        tasks={filteredTasks}
        loading={loading}
        title={`任务列表 (${filteredTasks.length})`}
        emptyText="没有找到匹配的任务"
      />
    </div>
  );
};