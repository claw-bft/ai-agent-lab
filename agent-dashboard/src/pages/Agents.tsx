import type React from 'react';
import { AgentCard } from '../components/AgentCard';
import { usePolling } from '../hooks/usePolling';
import { agentService } from '../services/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import type { Agent } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export const Agents: React.FC = () => {
  const { data: agentStats, loading } = usePolling(
    () => agentService.getStats(),
    10000
  );

  const agents = agentStats?.agents || [];

  // 准备图表数据
  const chartData = {
    labels: agents.map(a => a.name),
    datasets: [
      {
        label: '已完成任务',
        data: agents.map(a => a.completedTasks),
        backgroundColor: '#10b981',
        borderRadius: 4,
      },
      {
        label: '失败任务',
        data: agents.map(a => a.failedTasks),
        backgroundColor: '#ef4444',
        borderRadius: 4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Agent任务完成情况',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const tokenData = {
    labels: agents.map(a => a.name),
    datasets: [
      {
        label: 'Token使用量 (千)',
        data: agents.map(a => a.totalTokens / 1000),
        backgroundColor: '#0ea5e9',
        borderRadius: 4,
      },
    ],
  };

  const tokenOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Token使用量统计',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Agent团队</h1>
        <p className="text-gray-500">查看所有Agent的状态和性能统计</p>
      </div>

      {/* Agent卡片网格 */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-64 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent: Agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}

      {/* 统计图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="h-80">
            <Bar data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="h-80">
            <Bar data={tokenData} options={tokenOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};