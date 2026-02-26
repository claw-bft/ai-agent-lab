import type { FC } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Tasks } from './pages/Tasks';
import { Agents } from './pages/Agents';
import './index.css';

const App: FC = () => {
  return (
    <Router>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/agents" element={<Agents />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
