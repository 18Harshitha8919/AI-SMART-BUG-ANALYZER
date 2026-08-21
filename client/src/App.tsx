import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import SubmitBug from './pages/SubmitBug';
import Analytics from './pages/Analytics';
import KnowledgeBase from './pages/KnowledgeBase';

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('darkMode');
    return saved === 'true' || saved === null; // Default to dark mode for rich cyber aesthetics
  });

  useEffect(() => {
    const root = window.document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('darkMode', darkMode.toString());
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 dark:bg-dark-900 transition-colors duration-200 flex">
        <Sidebar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        
        {/* Main Content Area */}
        <div className="flex-1 pl-64 flex flex-col min-h-screen overflow-x-hidden">
          {/* Top telemetry status bar */}
          <header className="h-16 glass-nav px-8 flex justify-between items-center sticky top-0 z-20">
            <div className="text-[10px] font-mono font-bold text-slate-400 dark:text-dark-400 uppercase tracking-widest">
              Telemetry Status: <span className="text-emerald-500 dark:text-cyber-green animate-pulse">GRID ONLINE</span>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono text-slate-500 dark:text-dark-400">
              <span>FastAPI port: <span className="text-brand-500 dark:text-cyber-neon font-bold">8000</span></span>
              <span className="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-dark-700" />
              <span>Node port: <span className="text-brand-500 dark:text-cyber-neon font-bold">5000</span></span>
            </div>
          </header>

          <main className="p-8 flex-1 w-full max-w-6xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/submit-bug" element={<SubmitBug />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/knowledge-base" element={<KnowledgeBase />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
