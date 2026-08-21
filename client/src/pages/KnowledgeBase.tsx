import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BookOpen, 
  CheckCircle, 
  ShieldCheck, 
  Clock, 
  Search, 
  RefreshCw, 
  ExternalLink, 
  Brain, 
  Wrench, 
  Layers, 
  AlertTriangle 
} from 'lucide-react';

interface KnowledgeEntry {
  _id?: string;
  bugId: string;
  title: string;
  description: string;
  stackTrace?: string;
  rootCause: string;
  fixAction: string;
  severity: string;
  priority: string;
  category: string;
  component: string;
  verified: boolean;
  resolutionDate: string;
}

interface KnowledgeStats {
  total: number;
  verified: number;
  unverified: number;
  verifiedRate: number;
}

const KnowledgeBase: React.FC = () => {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [stats, setStats] = useState<KnowledgeStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedEntry, setSelectedEntry] = useState<KnowledgeEntry | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [historyRes, statsRes] = await Promise.all([
        axios.get('/api/knowledge/history'),
        axios.get('/api/knowledge/stats')
      ]);
      setEntries(historyRes.data || []);
      setStats(statsRes.data || null);
      if (historyRes.data && historyRes.data.length > 0) {
        setSelectedEntry(historyRes.data[0]);
      }
    } catch (e) {
      console.error("Knowledge base fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleVerify = async (bugId: string, currentStatus: boolean) => {
    try {
      await axios.post('/api/knowledge/verify', {
        bugId,
        verified: !currentStatus
      });
      // Update local state
      setEntries(entries.map(e => e.bugId === bugId ? { ...e, verified: !currentStatus } : e));
      if (selectedEntry?.bugId === bugId) {
        setSelectedEntry({ ...selectedEntry, verified: !currentStatus });
      }
    } catch (e) {
      alert("Failed to verify knowledge entry");
    }
  };

  const filteredEntries = entries.filter(e => 
    e.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.bugId.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.component.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 dark:border-white/5 pb-5">
        <div>
          <h2 className="text-xl font-black text-slate-800 dark:text-white tracking-tight flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-brand-500 dark:text-cyber-neon" /> Knowledge Base & RAG Memory
          </h2>
          <p className="text-xs text-slate-500 dark:text-dark-400 font-medium mt-0.5">
            Verified resolution playbooks indexed in the FAISS vector database.
          </p>
        </div>

        <button 
          onClick={fetchData} 
          className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-dark-800 hover:bg-slate-200 dark:hover:bg-dark-700 text-slate-700 dark:text-dark-200 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh Index
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="glass p-4 rounded-2xl border border-slate-200 dark:border-white/5">
            <span className="text-[10px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Total Vectors</span>
            <div className="text-2xl font-black text-slate-800 dark:text-white mt-1">{stats.total}</div>
          </div>
          <div className="glass p-4 rounded-2xl border border-slate-200 dark:border-white/5">
            <span className="text-[10px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Verified Playbooks</span>
            <div className="text-2xl font-black text-emerald-500 dark:text-cyber-green mt-1">{stats.verified}</div>
          </div>
          <div className="glass p-4 rounded-2xl border border-slate-200 dark:border-white/5">
            <span className="text-[10px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Pending Review</span>
            <div className="text-2xl font-black text-amber-500 mt-1">{stats.unverified}</div>
          </div>
          <div className="glass p-4 rounded-2xl border border-slate-200 dark:border-white/5">
            <span className="text-[10px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Trust Accuracy</span>
            <div className="text-2xl font-black text-brand-500 dark:text-cyber-neon mt-1">{stats.verifiedRate}%</div>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        
        {/* Left List Column (Col span 5) */}
        <div className="xl:col-span-5 glass p-5 rounded-2xl border border-slate-200 dark:border-white/5 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-black text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="h-4 w-4 text-brand-500" /> Historical Solutions ({filteredEntries.length})
            </h3>
          </div>

          {/* Search box */}
          <div className="relative">
            <Search className="h-3.5 w-3.5 absolute left-3 top-3 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search knowledge by bug ID, title, module..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-2 text-xs rounded-xl bg-slate-100 dark:bg-dark-800 border border-slate-200 dark:border-white/5 text-slate-700 dark:text-white focus:outline-none"
            />
          </div>

          {/* Entries list */}
          <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
            {loading ? (
              <div className="py-12 text-center text-xs text-slate-400">Loading knowledge memories...</div>
            ) : filteredEntries.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-400 italic">No matching knowledge entries found.</div>
            ) : (
              filteredEntries.map((item) => (
                <div 
                  key={item.bugId}
                  onClick={() => setSelectedEntry(item)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-1.5 ${
                    selectedEntry?.bugId === item.bugId 
                      ? 'bg-brand-500/10 border-brand-500/30 dark:border-cyber-neon/30' 
                      : 'bg-slate-50 dark:bg-dark-900/40 border-slate-200/50 dark:border-white/5 hover:bg-slate-100 dark:hover:bg-dark-800/50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] font-bold text-brand-500 dark:text-cyber-neon">{item.bugId}</span>
                    <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold ${
                      item.verified ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                    }`}>
                      {item.verified ? 'VERIFIED' : 'PENDING'}
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-800 dark:text-white truncate">{item.title}</h4>
                  <div className="text-[10px] text-slate-500 dark:text-dark-400 flex items-center gap-2">
                    <span>Component: {item.component}</span> • <span>{new Date(item.resolutionDate).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Details Column (Col span 7) */}
        <div className="xl:col-span-7 space-y-6">
          {selectedEntry ? (
            <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-5">
              
              <div className="flex justify-between items-start border-b border-slate-200 dark:border-white/5 pb-4">
                <div>
                  <span className="text-[10px] font-mono text-brand-500 dark:text-cyber-neon font-bold">{selectedEntry.bugId}</span>
                  <h3 className="text-base font-black text-slate-800 dark:text-white mt-0.5">{selectedEntry.title}</h3>
                </div>
                <button
                  onClick={() => handleToggleVerify(selectedEntry.bugId, selectedEntry.verified)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                    selectedEntry.verified 
                      ? 'bg-emerald-500/15 text-emerald-600 dark:text-cyber-green border border-emerald-500/30'
                      : 'bg-amber-500/15 text-amber-600 dark:text-amber-500 border border-amber-500/30'
                  }`}
                >
                  <ShieldCheck className="h-4 w-4" />
                  {selectedEntry.verified ? 'Verified in Vector DB' : 'Click to Verify'}
                </button>
              </div>

              {/* Bug Description */}
              <div className="space-y-1">
                <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Defect Problem Statement</span>
                <p className="p-3.5 rounded-xl bg-slate-50 dark:bg-dark-900 border border-slate-200/50 dark:border-white/5 text-xs text-slate-600 dark:text-dark-200 leading-relaxed">
                  {selectedEntry.description}
                </p>
              </div>

              {/* Root Cause Card */}
              <div className="p-4 rounded-xl bg-orange-500/10 border border-orange-500/20 space-y-2 dark:bg-amber-500/10 dark:border-amber-500/20">
                <span className="text-[10px] text-orange-600 dark:text-amber-500 font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                  <Brain className="h-4 w-4" /> Root Cause Breakdown
                </span>
                <p className="text-xs font-bold text-slate-800 dark:text-white leading-relaxed">
                  {selectedEntry.rootCause}
                </p>
              </div>

              {/* Fix Action Playbook */}
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 space-y-2 dark:bg-cyber-green/10 dark:border-cyber-green/20">
                <span className="text-[10px] text-emerald-600 dark:text-cyber-green font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                  <Wrench className="h-4 w-4" /> Verified Remediation Playbook
                </span>
                <p className="text-xs font-bold text-slate-800 dark:text-emerald-400 leading-relaxed">
                  {selectedEntry.fixAction}
                </p>
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-3 gap-3 pt-2 text-xs">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900 border border-slate-200/50 dark:border-white/5">
                  <span className="text-[9px] text-slate-400 font-bold uppercase block">Severity</span>
                  <span className="font-bold text-slate-800 dark:text-white mt-0.5 block">{selectedEntry.severity}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900 border border-slate-200/50 dark:border-white/5">
                  <span className="text-[9px] text-slate-400 font-bold uppercase block">Component</span>
                  <span className="font-bold text-slate-800 dark:text-white mt-0.5 block">{selectedEntry.component}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-dark-900 border border-slate-200/50 dark:border-white/5">
                  <span className="text-[9px] text-slate-400 font-bold uppercase block">Resolved On</span>
                  <span className="font-mono text-[10px] text-slate-600 dark:text-dark-300 mt-0.5 block">
                    {new Date(selectedEntry.resolutionDate).toLocaleDateString()}
                  </span>
                </div>
              </div>

            </div>
          ) : (
            <div className="glass p-12 rounded-2xl text-center text-slate-400 space-y-2 h-96 flex flex-col justify-center border border-dashed border-slate-200 dark:border-white/5">
              <BookOpen className="h-8 w-8 mx-auto opacity-30" />
              <p className="text-xs">Select a knowledge entry from the list to view resolution specifics.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default KnowledgeBase;
