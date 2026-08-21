import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  PlusCircle, 
  Database, 
  Binary, 
  BookOpen, 
  Bug, 
  Sun, 
  Moon,
  BarChart3
} from 'lucide-react';

interface SidebarProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ darkMode, toggleDarkMode }) => {
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/submit-bug', label: 'Submit Bug', icon: PlusCircle },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/knowledge-base', label: 'Knowledge Base', icon: BookOpen }
  ];

  return (
    <aside className="w-64 glass h-screen fixed left-0 top-0 flex flex-col justify-between border-r border-slate-200 dark:border-white/5 z-30 transition-all duration-200">
      <div>
        {/* Brand Logo Header */}
        <div className="p-6 flex items-center gap-3 border-b border-slate-200 dark:border-white/5">
          <div className="bg-brand-500 p-2 rounded-xl text-white shadow-glass-glow">
            <Bug className="h-6 w-6 text-cyber-neon" />
          </div>
          <div>
            <h1 className="font-extrabold text-[8.5px] text-slate-800 dark:text-white tracking-wider leading-snug uppercase">
              CREATION OF INTELLIGENT <span className="text-brand-500 dark:text-cyber-neon font-black">BUG DIAGNOSIS PLATFORM</span> WITH FIX RECOMMENDATION ASSISTANCE GROUP
            </h1>
          </div>
        </div>

        {/* Menu Navigation */}
        <nav className="p-4 space-y-1.5">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => 
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
                    isActive 
                      ? 'bg-brand-500 text-white shadow-glass-glow border-l-4 border-brand-300 dark:border-cyber-neon' 
                      : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:text-dark-300 dark:hover:bg-dark-800/50 dark:hover:text-white'
                  }`
                }
              >
                <Icon className="h-4.5 w-4.5 shrink-0" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Dark/Light mode toggle & footer */}
      <div className="p-4 border-t border-slate-200 dark:border-white/5 space-y-4">
        {/* Mode Switcher Button */}
        <button
          onClick={toggleDarkMode}
          className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-100 dark:border-white/5 dark:hover:bg-dark-800/50 text-xs font-semibold text-slate-600 dark:text-dark-300 transition-all cursor-pointer"
        >
          <span className="flex items-center gap-2">
            {darkMode ? <Sun className="h-4.5 w-4.5 text-yellow-400" /> : <Moon className="h-4.5 w-4.5 text-brand-500" />}
            {darkMode ? 'Light Theme' : 'Dark Theme'}
          </span>
          <span className="text-[9px] font-mono text-slate-400 dark:text-dark-500">MODE</span>
        </button>
        
        <div className="text-[10px] text-center text-slate-400 dark:text-dark-500 font-mono">
          &copy; 2026 Smart Bug Analyzer
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
