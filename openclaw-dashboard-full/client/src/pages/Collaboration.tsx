import { useState, useEffect } from 'react';
import { 
  Users, 
  Workflow, 
  MessageSquare, 
  Activity,
  CheckCircle2,
  Clock,
  AlertCircle,
  Play,
  Pause,
  RotateCcw,
  GitBranch,
  Zap,
  Server,
  Cpu,
  BarChart3
} from 'lucide-react';
import { cn } from '../lib/utils';

// Types
interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'busy' | 'offline';
  lastHeartbeat: number;
  capabilities: string[];
  tasksCompleted: number;
}

interface Task {
  id: string;
  type: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  assignedTo?: string;
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
  dependencies: string[];
  result?: any;
  error?: string;
}

interface Workflow {
  id: string;
  name: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  tasks: string[];
  createdAt: number;
  completedAt?: number;
  progress: number;
}

interface Message {
  id: string;
  from: string;
  to: string;
  type: 'direct' | 'broadcast';
  content: string;
  timestamp: number;
}

interface CollaborationStats {
  totalAgents: number;
  activeAgents: number;
  totalTasks: number;
  completedTasks: number;
  runningWorkflows: number;
  messagesExchanged: number;
  avgTaskCompletionTime: number;
}

// Mock data generator
function generateMockAgents(): Agent[] {
  return [
    {
      id: 'finance-pro',
      name: 'Finance Pro',
      type: 'skill',
      status: 'idle',
      lastHeartbeat: Date.now(),
      capabilities: ['stock_analysis', 'portfolio_tracking', 'market_data'],
      tasksCompleted: 156
    },
    {
      id: 'coding-pro',
      name: 'Coding Pro',
      type: 'skill',
      status: 'active',
      lastHeartbeat: Date.now() - 30000,
      capabilities: ['code_generation', 'code_review', 'refactoring'],
      tasksCompleted: 234
    },
    {
      id: 'product-pro',
      name: 'Product Pro',
      type: 'skill',
      status: 'busy',
      lastHeartbeat: Date.now() - 60000,
      capabilities: ['competitor_analysis', 'prd_generation', 'user_research'],
      tasksCompleted: 89
    },
    {
      id: 'research-pro',
      name: 'Research Pro',
      type: 'skill',
      status: 'idle',
      lastHeartbeat: Date.now() - 120000,
      capabilities: ['web_search', 'data_analysis', 'report_generation'],
      tasksCompleted: 178
    },
    {
      id: 'master-agent',
      name: 'Master Agent',
      type: 'orchestrator',
      status: 'active',
      lastHeartbeat: Date.now(),
      capabilities: ['task_orchestration', 'workflow_management', 'result_aggregation'],
      tasksCompleted: 456
    }
  ];
}

function generateMockTasks(): Task[] {
  return [
    {
      id: 'task-001',
      type: 'finance.quote',
      description: 'Query Moutai stock price',
      status: 'completed',
      assignedTo: 'finance-pro',
      createdAt: Date.now() - 3600000,
      startedAt: Date.now() - 3500000,
      completedAt: Date.now() - 3400000,
      dependencies: [],
      result: { price: 1688.88, change: '+2.34%' }
    },
    {
      id: 'task-002',
      type: 'code.generate',
      description: 'Generate Python data pipeline',
      status: 'running',
      assignedTo: 'coding-pro',
      createdAt: Date.now() - 1800000,
      startedAt: Date.now() - 1700000,
      dependencies: [],
    },
    {
      id: 'task-003',
      type: 'research.competitor',
      description: 'Analyze competitor features',
      status: 'pending',
      createdAt: Date.now() - 900000,
      dependencies: ['task-002'],
    },
    {
      id: 'task-004',
      type: 'product.prd',
      description: 'Generate PRD document',
      status: 'pending',
      createdAt: Date.now() - 600000,
      dependencies: ['task-003'],
    }
  ];
}

function generateMockWorkflows(): Workflow[] {
  return [
    {
      id: 'wf-001',
      name: 'Stock Research Pipeline',
      type: 'stock-research',
      status: 'running',
      tasks: ['task-001', 'task-002', 'task-003'],
      createdAt: Date.now() - 3600000,
      progress: 66
    },
    {
      id: 'wf-002',
      name: 'Product Development',
      type: 'product-dev',
      status: 'pending',
      tasks: ['task-004'],
      createdAt: Date.now() - 1800000,
      progress: 0
    }
  ];
}

function generateMockMessages(): Message[] {
  return [
    {
      id: 'msg-001',
      from: 'master-agent',
      to: 'finance-pro',
      type: 'direct',
      content: 'Please query stock price for 600519.SH',
      timestamp: Date.now() - 3600000
    },
    {
      id: 'msg-002',
      from: 'finance-pro',
      to: 'master-agent',
      type: 'direct',
      content: 'Stock query completed: 1688.88 (+2.34%)',
      timestamp: Date.now() - 3400000
    },
    {
      id: 'msg-003',
      from: 'master-agent',
      to: 'broadcast',
      type: 'broadcast',
      content: 'Starting new workflow: Product Development',
      timestamp: Date.now() - 1800000
    }
  ];
}

function generateMockStats(): CollaborationStats {
  return {
    totalAgents: 5,
    activeAgents: 3,
    totalTasks: 156,
    completedTasks: 142,
    runningWorkflows: 1,
    messagesExchanged: 1247,
    avgTaskCompletionTime: 45.6
  };
}

// Components
function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  description,
  trend,
  className 
}: { 
  title: string; 
  value: string | number; 
  icon: React.ElementType;
  description?: string;
  trend?: { value: number; positive: boolean };
  className?: string;
}) {
  return (
    <div className={cn("bg-card rounded-xl border border-border p-6", className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <h3 className="text-2xl font-bold mt-1">{value}</h3>
          {description && (
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          )}
          {trend && (
            <p className={cn("text-xs mt-1", trend.positive ? "text-green-500" : "text-red-500")}>
              {trend.positive ? '↑' : '↓'} {trend.value}%
            </p>
          )}
        </div>
        <div className="p-3 bg-primary/10 rounded-lg">
          <Icon className="w-5 h-5 text-primary" />
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles = {
    active: 'bg-green-500/10 text-green-500 border-green-500/20',
    idle: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    busy: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    offline: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
    pending: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    running: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    completed: 'bg-green-500/10 text-green-500 border-green-500/20',
    failed: 'bg-red-500/10 text-red-500 border-red-500/20',
  };

  return (
    <span className={cn(
      "px-2 py-0.5 text-xs font-medium rounded-full border",
      styles[status as keyof typeof styles] || styles.idle
    )}>
      {status}
    </span>
  );
}

function AgentCard({ agent }: { agent: Agent }) {
  return (
    <div className="bg-card rounded-lg border border-border p-4 hover:border-primary/50 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={cn(
            "w-10 h-10 rounded-lg flex items-center justify-center",
            agent.status === 'active' ? 'bg-green-500/10' :
            agent.status === 'busy' ? 'bg-blue-500/10' :
            agent.status === 'idle' ? 'bg-yellow-500/10' : 'bg-gray-500/10'
          )}>
            <Server className={cn("w-5 h-5",
              agent.status === 'active' ? 'text-green-500' :
              agent.status === 'busy' ? 'text-blue-500' :
              agent.status === 'idle' ? 'text-yellow-500' : 'text-gray-500'
            )} />
          </div>
          <div>
            <h4 className="font-medium">{agent.name}</h4>
            <p className="text-xs text-muted-foreground">{agent.type}</p>
          </div>
        </div>
        <StatusBadge status={agent.status} />
      </div>
      
      <div className="space-y-2">
        <div className="flex flex-wrap gap-1">
          {agent.capabilities.slice(0, 3).map((cap, i) => (
            <span key={i} className="text-xs px-2 py-0.5 bg-muted rounded">
              {cap}
            </span>
          ))}
          {agent.capabilities.length > 3 && (
            <span className="text-xs px-2 py-0.5 bg-muted rounded">
              +{agent.capabilities.length - 3}
            </span>
          )}
        </div>
        
        <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t border-border">
          <span className="flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            {agent.tasksCompleted} tasks
          </span>
          <span className="flex items-center gap-1">
            <Activity className="w-3 h-3" />
            {Math.floor((Date.now() - agent.lastHeartbeat) / 1000)}s ago
          </span>
        </div>
      </div>
    </div>
  );
}

function TaskItem({ task }: { task: Task }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg border border-border/50">
      <div className={cn("w-2 h-2 rounded-full",
        task.status === 'completed' ? 'bg-green-500' :
        task.status === 'running' ? 'bg-blue-500 animate-pulse' :
        task.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
      )} />
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm truncate">{task.description}</span>
          <StatusBadge status={task.status} />
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
          <span className="font-mono">{task.id}</span>
          <span>•</span>
          <span>{task.type}</span>
          {task.assignedTo && (
            <>
              <span>•</span>
              <span className="text-primary">@{task.assignedTo}</span>
            </>
          )}
        </div>
      </div>
      
      {task.dependencies.length > 0 && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <GitBranch className="w-3 h-3" />
          <span>{task.dependencies.length} deps</span>
        </div>
      )}
    </div>
  );
}

function WorkflowCard({ workflow }: { workflow: Workflow }) {
  return (
    <div className="bg-card rounded-lg border border-border p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-medium">{workflow.name}</h4>
          <p className="text-xs text-muted-foreground font-mono">{workflow.type}</p>
        </div>
        <StatusBadge status={workflow.status} />
      </div>
      
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{workflow.progress}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className={cn(
                "h-full transition-all duration-500",
                workflow.status === 'completed' ? 'bg-green-500' :
                workflow.status === 'failed' ? 'bg-red-500' : 'bg-primary'
              )}
              style={{ width: `${workflow.progress}%` }}
            />
          </div>
        </div>
        
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            {workflow.tasks.length} tasks
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(workflow.createdAt).toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
}

function MessageItem({ message }: { message: Message }) {
  return (
    <div className="flex gap-3 p-3 bg-muted/30 rounded-lg">
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium",
        message.type === 'broadcast' ? 'bg-primary/20 text-primary' : 'bg-muted'
      )}>
        {message.from.charAt(0).toUpperCase()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 text-sm">
          <span className="font-medium">{message.from}</span>
          {message.type === 'broadcast' ? (
            <span className="text-xs px-1.5 py-0.5 bg-primary/10 text-primary rounded">
              broadcast
            </span>
          ) : (
            <>
              <span className="text-muted-foreground">→</span>
              <span className="text-muted-foreground">{message.to}</span>
            </>
          )}
        </div>
        <p className="text-sm mt-1">{message.content}</p>
        <p className="text-xs text-muted-foreground mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

export default function Collaboration() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [stats, setStats] = useState<CollaborationStats | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'tasks' | 'workflows' | 'messages'>('overview');

  useEffect(() => {
    // Load mock data
    setAgents(generateMockAgents());
    setTasks(generateMockTasks());
    setWorkflows(generateMockWorkflows());
    setMessages(generateMockMessages());
    setStats(generateMockStats());

    // Simulate real-time updates
    const interval = setInterval(() => {
      setAgents(prev => prev.map(agent => ({
        ...agent,
        lastHeartbeat: agent.status !== 'offline' ? Date.now() - Math.random() * 120000 : agent.lastHeartbeat
      })));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'agents', label: 'Agents', icon: Users },
    { id: 'tasks', label: 'Tasks', icon: CheckCircle2 },
    { id: 'workflows', label: 'Workflows', icon: Workflow },
    { id: 'messages', label: 'Messages', icon: MessageSquare },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">Agent Collaboration</h1>
          <p className="text-muted-foreground mt-1">
            Multi-agent orchestration and task coordination
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 text-green-500 rounded-lg text-sm">
            <Zap className="w-4 h-4" />
            <span>Protocol Active</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-muted rounded-lg w-fit">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors",
                activeTab === tab.id 
                  ? 'bg-background text-foreground shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Active Agents"
              value={`${stats.activeAgents}/${stats.totalAgents}`}
              icon={Users}
              description="Currently online"
            />
            <StatCard
              title="Task Completion"
              value={`${Math.round((stats.completedTasks / stats.totalTasks) * 100)}%`}
              icon={CheckCircle2}
              description={`${stats.completedTasks}/${stats.totalTasks} tasks`}
              trend={{ value: 12.5, positive: true }}
            />
            <StatCard
              title="Running Workflows"
              value={stats.runningWorkflows}
              icon={Workflow}
              description="Active pipelines"
            />
            <StatCard
              title="Messages"
              value={stats.messagesExchanged}
              icon={MessageSquare}
              description="Total exchanged"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quick Stats */}
            <div className="bg-card rounded-xl border border-border p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Cpu className="w-5 h-5" />
                System Performance
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted-foreground">Avg Task Completion Time</span>
                    <span className="font-medium">{stats.avgTaskCompletionTime}s</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-primary w-3/4" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted-foreground">Agent Utilization</span>
                    <span className="font-medium">{Math.round((stats.activeAgents / stats.totalAgents) * 100)}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500"
                      style={{ width: `${(stats.activeAgents / stats.totalAgents) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted-foreground">Task Success Rate</span>
                    <span className="font-medium">{Math.round((stats.completedTasks / stats.totalTasks) * 100)}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500"
                      style={{ width: `${(stats.completedTasks / stats.totalTasks) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-card rounded-xl border border-border p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Recent Activity
              </h3>
              <div className="space-y-3">
                {tasks.slice(0, 4).map((task) => (
                  <div key={task.id} className="flex items-center gap-3 p-2 hover:bg-muted rounded-lg transition-colors">
                    <div className={cn("w-2 h-2 rounded-full",
                      task.status === 'completed' ? 'bg-green-500' :
                      task.status === 'running' ? 'bg-blue-500' :
                      task.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                    )} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{task.description}</p>
                      <p className="text-xs text-muted-foreground">{task.type}</p>
                    </div>
                    <StatusBadge status={task.status} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agents Tab */}
      {activeTab === 'agents' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}

      {/* Tasks Tab */}
      {activeTab === 'tasks' && (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskItem key={task.id} task={task} />
          ))}
        </div>
      )}

      {/* Workflows Tab */}
      {activeTab === 'workflows' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workflows.map((workflow) => (
            <WorkflowCard key={workflow.id} workflow={workflow} />
          ))}
        </div>
      )}

      {/* Messages Tab */}
      {activeTab === 'messages' && (
        <div className="space-y-3">
          {messages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))}
        </div>
      )}
    </div>
  );
}
