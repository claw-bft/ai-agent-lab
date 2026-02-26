import { useState, useEffect } from 'react';
import { 
  Settings, 
  Save, 
  FolderOpen,
  RefreshCw,
  Server,
  Globe,
  Shield
} from 'lucide-react';
import { fetchApi } from '../lib/utils';

interface Config {
  workspaceDir: string;
  port: number;
  autoRefresh: boolean;
  theme: 'light' | 'dark' | 'system';
}

export default function SettingsPage() {
  const [config, setConfig] = useState<Config>({
    workspaceDir: '/root/.openclaw/workspace',
    port: 3001,
    autoRefresh: true,
    theme: 'system',
  });
  const [memory, setMemory] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadMemory();
  }, []);

  const loadMemory = async () => {
    try {
      const data = await fetchApi('/memory');
      setMemory(data.content);
    } catch (error) {
      console.error('Failed to load memory:', error);
    }
  };

  const handleSaveMemory = async () => {
    setSaving(true);
    try {
      await fetchApi('/memory', {
        method: 'POST',
        body: JSON.stringify({ content: memory }),
      });
      setMessage({ type: 'success', text: 'Memory saved successfully' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save memory' });
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(null), 3000);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Configure your OpenClaw dashboard
        </p>
      </div>

      {message && (
        <div className={`
          p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-500/10 text-green-600 border border-green-500/20' 
              : 'bg-red-500/10 text-red-600 border border-red-500/20'
          }
        `}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* General Settings */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            General
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Workspace Directory</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={config.workspaceDir}
                  onChange={(e) => setConfig({ ...config, workspaceDir: e.target.value })}
                  className="flex-1 px-3 py-2 bg-muted border border-border rounded-lg"
                  disabled
                />
                <button className="px-3 py-2 border border-border rounded-lg hover:bg-muted">
                  <FolderOpen className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                The workspace directory is managed by OpenClaw
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Server Port</label>
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-muted-foreground" />
                <input
                  type="number"
                  value={config.port}
                  onChange={(e) => setConfig({ ...config, port: parseInt(e.target.value) })}
                  className="flex-1 px-3 py-2 bg-muted border border-border rounded-lg"
                  disabled
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Theme</label>
              <select
                value={config.theme}
                onChange={(e) => setConfig({ ...config, theme: e.target.value as Config['theme'] })}
                className="w-full px-3 py-2 bg-muted border border-border rounded-lg"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System</option>
              </select>
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-sm">Auto Refresh</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.autoRefresh}
                  onChange={(e) => setConfig({ ...config, autoRefresh: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Memory Editor */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5" />
            Memory
          </h2>
          
          <p className="text-sm text-muted-foreground mb-4">
            Edit the MEMORY.md file directly. This is your long-term memory storage.
          </p>
          
          <textarea
            value={memory}
            onChange={(e) => setMemory(e.target.value)}
            className="w-full h-64 px-3 py-2 bg-muted border border-border rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="# Memory&#10;&#10;Your memories will appear here..."
          />
          
          <div className="flex justify-end gap-2 mt-4">
            <button
              onClick={loadMemory}
              className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted"
            >
              <RefreshCw className="w-4 h-4" />
              Reload
            </button>
            <button
              onClick={handleSaveMemory}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save Memory'}
            </button>
          </div>
        </div>
      </div>

      {/* API Info */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          API Information
        </h2>
        
        <div className="space-y-3">
          <div className="flex justify-between py-2 border-b border-border">
            <span className="text-muted-foreground">API Base URL</span>
            <code className="bg-muted px-2 py-1 rounded text-sm">/api</code>
          </div>
          
          <div className="flex justify-between py-2 border-b border-border">
            <span className="text-muted-foreground">WebSocket Endpoint</span>
            <code className="bg-muted px-2 py-1 rounded text-sm">/ws</code>
          </div>
          
          <div className="flex justify-between py-2">
            <span className="text-muted-foreground">Documentation</span>
            <a 
              href="/api/health" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Health Check →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
