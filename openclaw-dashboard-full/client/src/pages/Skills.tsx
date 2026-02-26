import { useState, useEffect } from 'react';
import { 
  Wrench, 
  Package, 
  CheckCircle2, 
  XCircle,
  RefreshCw,
  ExternalLink,
  FolderOpen
} from 'lucide-react';
import { fetchApi } from '../lib/utils';

interface Skill {
  name: string;
  description: string;
  version: string;
  installed: boolean;
}

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);

  useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = async () => {
    try {
      const data = await fetchApi('/skills');
      setSkills(data);
    } catch (error) {
      console.error('Failed to load skills:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInstall = async (name: string) => {
    setActionInProgress(name);
    try {
      await fetchApi(`/skills/${name}/install`, { method: 'POST' });
      loadSkills();
    } catch (error) {
      console.error('Failed to install skill:', error);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleUninstall = async (name: string) => {
    setActionInProgress(name);
    try {
      await fetchApi(`/skills/${name}/uninstall`, { method: 'POST' });
      loadSkills();
    } catch (error) {
      console.error('Failed to uninstall skill:', error);
    } finally {
      setActionInProgress(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Skills</h1>
          <p className="text-muted-foreground mt-1">
            Manage OpenClaw skills and tools
          </p>
        </div>
        <button
          onClick={loadSkills}
          className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-card rounded-lg border border-border p-4">
          <p className="text-sm text-muted-foreground">Total Skills</p>
          <p className="text-2xl font-bold">{skills.length}</p>
        </div>
        <div className="bg-card rounded-lg border border-border p-4">
          <p className="text-sm text-muted-foreground">Installed</p>
          <p className="text-2xl font-bold text-green-600">
            {skills.filter(s => s.installed).length}
          </p>
        </div>
        <div className="bg-card rounded-lg border border-border p-4">
          <p className="text-sm text-muted-foreground">Available</p>
          <p className="text-2xl font-bold text-blue-600">
            {skills.filter(s => !s.installed).length}
          </p>
        </div>
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {skills.map((skill) => (
          <div
            key={skill.name}
            className="bg-card rounded-xl border border-border p-6 hover:border-primary/50 transition-colors"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Wrench className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">{skill.name}</h3>
                  <p className="text-xs text-muted-foreground">v{skill.version}</p>
                </div>
              </div>
              
              {skill.installed ? (
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              ) : (
                <XCircle className="w-5 h-5 text-muted-foreground" />
              )}
            </div>
            
            <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
              {skill.description}
            </p>
            
            <div className="flex items-center gap-2">
              {skill.installed ? (
                <>
                  <a
                    href={`/api/files/skills/${skill.name}/SKILL.md`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm border border-border rounded-lg hover:bg-muted transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    View Docs
                  </a>
                  <button
                    onClick={() => handleUninstall(skill.name)}
                    disabled={actionInProgress === skill.name}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm border border-destructive text-destructive rounded-lg hover:bg-destructive/10 transition-colors disabled:opacity-50"
                  >
                    {actionInProgress === skill.name ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <XCircle className="w-4 h-4" />
                    )}
                    Uninstall
                  </button>
                </>
              ) : (
                <button
                  onClick={() => handleInstall(skill.name)}
                  disabled={actionInProgress === skill.name}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  {actionInProgress === skill.name ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Package className="w-4 h-4" />
                  )}
                  Install
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {skills.length === 0 && (
        <div className="text-center py-12">
          <FolderOpen className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
          <h3 className="text-lg font-medium">No skills found</h3>
          <p className="text-muted-foreground">
            Skills will appear here when they are added to the workspace
          </p>
        </div>
      )}
    </div>
  );
}
