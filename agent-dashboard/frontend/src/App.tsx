import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Tasks from './pages/Tasks'
import Agents from './pages/Agents'

// Mock data for demonstration
const mockStats = {
  totalAgents: 12,
  activeAgents: 8,
  totalTasks: 156,
  pendingTasks: 23,
  completedTasks: 120,
  failedTasks: 13
}

const mockChartData = {
  labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
  datasets: [
    {
      label: 'Active Tasks',
      data: [12, 8, 25, 45, 38, 22],
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true
    },
    {
      label: 'Completed Tasks',
      data: [8, 5, 18, 32, 28, 15],
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      fill: true
    }
  ]
}

const mockTasks = [
  { id: '1', title: 'Data Processing', status: 'running', agent: 'Agent-01', priority: 'high', progress: 65, createdAt: '2024-01-15 10:30' },
  { id: '2', title: 'Report Generation', status: 'pending', agent: '-', priority: 'medium', progress: 0, createdAt: '2024-01-15 11:00' },
  { id: '3', title: 'Image Analysis', status: 'completed', agent: 'Agent-03', priority: 'low', progress: 100, createdAt: '2024-01-15 09:00' },
  { id: '4', title: 'Email Notification', status: 'failed', agent: 'Agent-02', priority: 'high', progress: 30, createdAt: '2024-01-15 10:00' },
  { id: '5', title: 'Database Backup', status: 'running', agent: 'Agent-04', priority: 'medium', progress: 80, createdAt: '2024-01-15 11:30' },
]

const mockAgents = [
  { id: '1', name: 'Agent-01', status: 'busy', type: 'Worker', cpu: 45, memory: 62, tasksCompleted: 45 },
  { id: '2', name: 'Agent-02', status: 'idle', type: 'Worker', cpu: 12, memory: 28, tasksCompleted: 38 },
  { id: '3', name: 'Agent-03', status: 'busy', type: 'Analyzer', cpu: 78, memory: 85, tasksCompleted: 52 },
  { id: '4', name: 'Agent-04', status: 'offline', type: 'Worker', cpu: 0, memory: 0, tasksCompleted: 21 },
  { id: '5', name: 'Agent-05', status: 'busy', type: 'Coordinator', cpu: 35, memory: 45, tasksCompleted: 67 },
]

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <Layout sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen}>
      <Routes>
        <Route 
          path="/" 
          element={<Dashboard 
            stats={mockStats} 
            chartData={mockChartData} 
          />} 
        />
        <Route 
          path="/tasks" 
          element={<Tasks tasks={mockTasks} />} 
        />
        <Route 
          path="/agents" 
          element={<Agents agents={mockAgents} />} 
        />
      </Routes>
    </Layout>
  )
}

export default App