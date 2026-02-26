import {
  Activity, 
  CheckCircle2, 
  Clock, 
  Cpu, 
  FolderOpen,
  HardDrive,
  MemoryStick,
  Wrench,
  Cloud,
  RefreshCw,
  Wifi,
  WifiOff
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useDashboardData } from '../hooks/useKVData';

function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  description,
  className 
}: { 
  title: string; 
  value: string | number; 
  icon: React.ElementType;
  description?: string;
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
        </div>
        <div className="p-3 bg-primary/10 rounded-lg">
          <Icon className="w-5 h-5 text-primary" />
        </div>
      </div>
    </div>
  );
}

function formatUptime(seconds: number): string {
  if (!seconds || seconds === 0) return '-';
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function formatBytes(bytes: number): string {
  if (!bytes || bytes === 0) return '0 B';
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

function formatTimeAgo(timestamp: number): string {
  if (!timestamp) return 'Never';
  const seconds = Math.floor((Date.now() - timestamp) / 1000);
  
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export default function Dashboard() {
  const { 
    sessions, 
    stats, 
    isLoading, 
    error, 
    isUsingKV, 
    isConnected, 
    lastUpdate,
    lastFetchTime,
    refresh 
  } = useDashboardData(3000);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            System overview and real-time status
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Connection Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-card border border-border rounded-lg">
            {isUsingKV ? (
              <>
                <Cloud className={cn("w-4 h-4", isConnected ? "text-green-500" : "text-red-500")} />
                <span className="text-sm">KV</span>
              </>
            ) : (
              <>
                {isConnected ? (
                  <Wifi className="w-4 h-4 text-green-500" />
                ) : (
                  <WifiOff className="w-4 h-4 text-red-500" />
                )}
                <span className="text-sm">WS</span>
              </>
            )}
            <div className={cn("w-2 h-2 rounded-full", isConnected ? 'bg-green-500' : 'bg-red-500')} />
          </div>
          
          {/* Refresh Button */}
          <button
            onClick={refresh}
            className="p-2 hover:bg-muted rounded-lg transition-colors"
            title="Refresh data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg">
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tasks"
          value={stats?.tasksCount || 0}
          icon={CheckCircle2}
          description="Total tasks in workspace"
        />
        <StatCard
          title="Skills"
          value={stats?.skillsCount || 0}
          icon={Wrench}
          description="Installed skills"
        />
        <StatCard
          title="Uptime"
          value={formatUptime(stats?.uptime || 0)}
          icon={Clock}
          description="Server running time"
        />
        <StatCard
          title="Connections"
          value={stats?.connectedClients || sessions.length || 0}
          icon={Activity}
          description="Active connections"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Resources */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5" />
            System Resources
          </h2>
          
          {stats?.memory ? (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="flex items-center gap-2">
                    <MemoryStick className="w-4 h-4" />
                    Heap Used
                  </span>
                  <span className="font-medium">{formatBytes(stats.memory.heapUsed)}</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all"
                    style={{ 
                      width: `${Math.min((stats.memory.heapUsed / stats.memory.heapTotal) * 100, 100)}%` 
                    }}
                  />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="flex items-center gap-2">
                    <HardDrive className="w-4 h-4" />
                    RSS Memory
                  </span>
                  <span className="font-medium">{formatBytes(stats.memory.rss)}</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-secondary transition-all"
                    style={{ width: '30%' }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground text-center py-8">No memory data available</p>
          )}
        </div>

        {/* Workspace Info */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FolderOpen className="w-5 h-5" />
            Workspace
          </h2>
          
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b border-border">
              <span className="text-muted-foreground">Path</span>
              <span className="font-mono text-sm truncate max-w-[200px]">{stats?.workspace || '-'}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-border">
              <span className="text-muted-foreground">Version</span>
              <span className="font-medium">{stats?.version || '-'}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-border">
              <span className="text-muted-foreground">Data Source</span>
              <span className="font-medium flex items-center gap-1">
                {isUsingKV ? (
                  <>
                    <Cloud className="w-3 h-3" /> Vercel KV
                  </>
                ) : (
                  <>
                    <Wifi className="w-3 h-3" /> WebSocket
                  </>
                )}
              </span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-muted-foreground">Last Update</span>
              <span className="text-sm">
                {lastUpdate ? formatTimeAgo(lastUpdate) : '-'}
              </span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-muted-foreground">Last Fetch</span>
              <span className="text-sm">
                {lastFetchTime ? formatTimeAgo(lastFetchTime) : '-'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Active Sessions */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Active Sessions
        </h2>
        
        {sessions.length > 0 ? (
          <div className="space-y-2">
            {sessions.map((session) => (
              <div key={session.id} className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <div className={cn("w-2 h-2 rounded-full", 
                  session.status === 'active' ? 'bg-green-500' : 
                  session.status === 'idle' ? 'bg-yellow-500' : 'bg-gray-500'
                )} />
                <div className="flex-1">
                  <p className="font-medium">{session.label}</p>
                  <p className="text-sm text-muted-foreground">
                    {session.channel} • {session.status}
                  </p>
                </div>
                <span className="text-xs text-muted-foreground">
                  {new Date(session.lastActivity).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-8">
            No active sessions
          </p>
        )}
      </div>
    </div>
  );
}
