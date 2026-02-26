import type { FC } from 'react';
import { HealthCard } from '../components/HealthCard';
import { TaskList } from '../components/TaskList';
import { usePolling } from '../hooks/usePolling';
import { healthService, taskService, agentService } from '../services/api';
import type { Agent, Task } from '../types';

export const Dashboard: FC = () => {
  const { data: health, loading: healthLoading } = usePolling(
    () => healthService.getStatus(),
    5000
  );

  const { data: runningTasksData, loading: tasksLoading } = usePolling(
    () => taskService.getRunning(),
    3000
  );

  const { data: recentTasksData, loading: recentLoading } = usePolling(
    () => taskService.getRecent(5),
    5000
  );

  const { data: agentStats } = usePolling(
    () => agentService.getStats(),
    10000
  );

  const runningTasks: Task[] = runningTasksData || [];
  const recentTasks: Task[] = recentTasksData || [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-500">实时监控Agent团队状态和任务执行情况</p>
        </div>
        <div className="text-sm text-gray-400">
          最后更新: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl p-6 text-white">
          <p className="text-primary-100 text-sm">总Agent数</p>
          <p className="text-3xl font-bold mt-1">{agentStats?.agents.length || 0}</p>
          <div className="mt-2 text-sm text-primary-100">
            {agentStats?.agents.filter((a: Agent) => a.status === 'active').length || 0} 个活跃中
          </div>
        </div>

        <div className="bg-gradient-to-br from-success to-emerald-600 rounded-xl p-6 text-white">
          <p className="text-emerald-100 text-sm">总完成任务</p>
          <p className="text-3xl font-bold mt-1">{agentStats?.totalCompleted || 0}</p>
          <div className="mt-2 text-sm text-emerald-100">
            成功率 {agentStats ? 
              ((agentStats.totalCompleted / (agentStats.totalCompleted + agentStats.totalFailed)) * 100).toFixed(1) 
              : 100}%
          </div>
        </div>

        <div className="bg-gradient-to-br from-warning to-amber-600 rounded-xl p-6 text-white">
          <p className="text-amber-100 text-sm">运行中任务</p>
          <p className="text-3xl font-bold mt-1">{runningTasks.length}</p>
          <div className="mt-2 text-sm text-amber-100">
            平均耗时 {runningTasks.length > 0 
              ? (runningTasks.reduce((acc, t) => acc + (t.duration || 0), 0) / runningTasks.length / 1000).toFixed(1)
              : 0}s
          </div>
        </div>

        <div className="bg-gradient-to-br from-danger to-red-600 rounded-xl p-6 text-white">
          <p className="text-red-100 text-sm">总失败任务</p>
          <p className="text-3xl font-bold mt-1">{agentStats?.totalFailed || 0}</p>
          <div className="mt-2 text-sm text-red-100">
            失败率 {agentStats ? 
              ((agentStats.totalFailed / (agentStats.totalCompleted + agentStats.totalFailed)) * 100).toFixed(1) 
              : 0}%
          </div>
        </div>
      </div>

      {/* 系统健康状态 */}
      <HealthCard health={health} loading={healthLoading} />

      {/* 任务列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TaskList
          tasks={runningTasks}
          loading={tasksLoading}
          title="运行中任务"
          emptyText="暂无运行中的任务"
        />

        <TaskList
          tasks={recentTasks}
          loading={recentLoading}
          title="最近完成的任务"
          emptyText="暂无已完成任务"
        />
      </div>
    </div>
  );
};