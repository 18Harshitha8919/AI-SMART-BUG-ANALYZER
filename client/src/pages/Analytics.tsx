import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart3, 
  PieChart as PieIcon, 
  TrendingUp, 
  Layers, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Download, 
  Search, 
  Filter, 
  RefreshCw,
  Terminal,
  Activity,
  Brain,
  ShieldCheck
} from 'lucide-react';

interface DefectAnalytics {
  totalBugs: number;
  severityDistribution: Record<string, number>;
  priorityDistribution: Record<string, number>;
  moduleCounts: Record<string, number>;
  componentCounts: { name: string; count: number }[];
  topExceptions: { name: string; count: number }[];
  rootCauseFrequency: { name: string; count: number }[];
  duplicatePercentage: number;
  avgAgentConfidence: number;
  avgResponseTime: string;
  resolutionSuccessRate: number;
  frequentlySuggestedFixes: { fix: string; count: number }[];
  monthlyTrends: Record<string, number>;
}

const Analytics: React.FC = () => {
  const [data, setData] = useState<DefectAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');

  const getApiBaseUrl = (): string => {
    let url = import.meta.env.VITE_API_URL || 'https://bugsense-server.onrender.com';
    url = url.trim();
    if (url.endsWith('/')) {
      url = url.slice(0, -1);
    }
    if (url.endsWith('/api')) {
      url = url.slice(0, -4);
    }
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = `https://${url}`;
    }
    return url;
  };

  const fetchAnalytics = async () => {
    setLoading(true);
    setError('');
    try {
      const cleanURL = getApiBaseUrl();
      const res = await axios.get(`${cleanURL}/api/analytics/defect-patterns`);
      setData(res.data);
    } catch (e: any) {
      setError(e.message || 'Failed to load defect pattern analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const handleExportCSV = () => {
    const cleanURL = getApiBaseUrl();
    window.open(`${cleanURL}/api/analytics/export-csv`, '_blank');
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw className="h-10 w-10 text-brand-500 animate-spin" />
        <p className="text-xs font-mono text-slate-400 dark:text-dark-400">Compiling Defect Analytics & Knowledge Trends...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 glass rounded-2xl border border-red-500/20 text-center space-y-3">
        <AlertTriangle className="h-8 w-8 text-red-500 mx-auto" />
        <h3 className="text-sm font-bold text-slate-800 dark:text-white">Analytics Unavailable</h3>
        <p className="text-xs text-slate-500 dark:text-dark-400">{error || 'No telemetry data recorded.'}</p>
        <button onClick={fetchAnalytics} className="btn-primary text-xs px-4 py-2 mt-2">Retry</button>
      </div>
    );
  }

  // Filtered exceptions
  const filteredExceptions = data.topExceptions.filter(exc => 
    exc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 dark:border-white/5 pb-5">
        <div>
          <h2 className="text-xl font-black text-slate-800 dark:text-white tracking-tight flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-brand-500 dark:text-cyber-neon" /> Defect Pattern Analytics
          </h2>
          <p className="text-xs text-slate-500 dark:text-dark-400 font-medium mt-0.5">
            Automated telemetry aggregations over historical bug reports and vector embeddings.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={fetchAnalytics} 
            className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-dark-800 hover:bg-slate-200 dark:hover:bg-dark-700 text-slate-700 dark:text-dark-200 text-xs font-bold transition-all flex items-center gap-1.5"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </button>
          <button 
            onClick={handleExportCSV} 
            className="px-4 py-2 rounded-xl bg-brand-500 text-white hover:bg-brand-600 shadow-glass-glow text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <Download className="h-3.5 w-3.5" /> Export to CSV
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass p-5 rounded-2xl border border-slate-200 dark:border-white/5 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 dark:text-dark-500 uppercase tracking-wider font-extrabold">Total Bugs Logged</span>
            <div className="text-3xl font-black text-slate-800 dark:text-white">{data.totalBugs}</div>
            <div className="text-[10px] text-slate-500 dark:text-dark-400 font-mono">Aggregated DB Entries</div>
          </div>
          <div className="bg-brand-500/10 p-3.5 rounded-2xl text-brand-500">
            <Layers className="h-6 w-6" />
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-slate-200 dark:border-white/5 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 dark:text-dark-500 uppercase tracking-wider font-extrabold">Duplicate Bug Ratio</span>
            <div className="text-3xl font-black text-purple-600 dark:text-cyber-purple">{data.duplicatePercentage}%</div>
            <div className="text-[10px] text-purple-500 font-mono">Similarity &gt; 80%</div>
          </div>
          <div className="bg-purple-500/10 p-3.5 rounded-2xl text-purple-500">
            <TrendingUp className="h-6 w-6" />
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-slate-200 dark:border-white/5 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 dark:text-dark-500 uppercase tracking-wider font-extrabold">Agent Confidence</span>
            <div className="text-3xl font-black text-emerald-500 dark:text-cyber-green">{data.avgAgentConfidence}%</div>
            <div className="text-[10px] text-emerald-500 font-mono">Avg Diagnostic Score</div>
          </div>
          <div className="bg-emerald-500/10 p-3.5 rounded-2xl text-emerald-500">
            <ShieldCheck className="h-6 w-6" />
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-slate-200 dark:border-white/5 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 dark:text-dark-500 uppercase tracking-wider font-extrabold">Resolution Rate</span>
            <div className="text-3xl font-black text-cyan-500">{data.resolutionSuccessRate}%</div>
            <div className="text-[10px] text-cyan-500 font-mono">Avg Latency: {data.avgResponseTime}</div>
          </div>
          <div className="bg-cyan-500/10 p-3.5 rounded-2xl text-cyan-500">
            <CheckCircle2 className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Row 2: Charts & Visuals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Component-Wise Defect Frequency (Custom Bar Chart) */}
        <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-black text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <Layers className="h-4 w-4 text-brand-500" /> Component-Wise Defect Count
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Total: {data.componentCounts.length} Components</span>
          </div>

          <div className="space-y-3 pt-2">
            {data.componentCounts.length === 0 ? (
              <p className="text-xs text-slate-400 dark:text-dark-500 italic">No component metrics available.</p>
            ) : (
              data.componentCounts.slice(0, 6).map((comp, idx) => {
                const maxVal = Math.max(...data.componentCounts.map(c => c.count), 1);
                const percent = Math.round((comp.count / maxVal) * 100);
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between items-center text-xs font-semibold text-slate-700 dark:text-dark-200">
                      <span>{comp.name}</span>
                      <span className="font-mono text-brand-500 font-bold">{comp.count} bugs</span>
                    </div>
                    <div className="w-full bg-slate-100 dark:bg-white/5 rounded-full h-2 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-brand-500 to-cyber-neon h-2 rounded-full transition-all duration-500" 
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Severity & Priority Distribution (Donut & Badges) */}
        <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-4">
          <h3 className="text-xs font-black text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-2">
            <PieIcon className="h-4 w-4 text-purple-500" /> Severity & Priority Breakdown
          </h3>

          <div className="grid grid-cols-2 gap-4 pt-2">
            {/* Severity list */}
            <div className="space-y-2">
              <span className="text-[10px] font-bold text-slate-400 dark:text-dark-500 uppercase block tracking-wider">Severity</span>
              {['Critical', 'High', 'Medium', 'Low'].map((sev) => {
                const count = data.severityDistribution[sev] || 0;
                const total = Math.max(data.totalBugs, 1);
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={sev} className="p-2.5 rounded-xl bg-slate-50 dark:bg-dark-900/50 border border-slate-200/40 dark:border-white/5 flex justify-between items-center text-xs">
                    <span className={`font-bold ${
                      sev === 'Critical' ? 'text-red-500' :
                      sev === 'High' ? 'text-orange-500' :
                      sev === 'Medium' ? 'text-yellow-500' : 'text-blue-500'
                    }`}>{sev}</span>
                    <span className="font-mono font-bold text-slate-700 dark:text-white">{count} ({pct}%)</span>
                  </div>
                );
              })}
            </div>

            {/* Priority list */}
            <div className="space-y-2">
              <span className="text-[10px] font-bold text-slate-400 dark:text-dark-500 uppercase block tracking-wider">Priority</span>
              {['P1', 'P2', 'P3', 'P4'].map((pri) => {
                const count = data.priorityDistribution[pri] || 0;
                const total = Math.max(data.totalBugs, 1);
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={pri} className="p-2.5 rounded-xl bg-slate-50 dark:bg-dark-900/50 border border-slate-200/40 dark:border-white/5 flex justify-between items-center text-xs">
                    <span className="font-mono font-bold text-slate-700 dark:text-white">{pri}</span>
                    <span className="font-mono font-bold text-slate-500 dark:text-dark-300">{count} ({pct}%)</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

      </div>

      {/* Row 3: Monthly Trends & Top Recurring Exceptions Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Monthly Timeline Area Chart */}
        <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-4 lg:col-span-1">
          <h3 className="text-xs font-black text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-emerald-500" /> Monthly Bug Trends
          </h3>
          <p className="text-[11px] text-slate-500 dark:text-dark-400">Defect submission velocity timeline.</p>

          <div className="space-y-3 pt-2">
            {Object.keys(data.monthlyTrends).length === 0 ? (
              <p className="text-xs text-slate-400 italic">No historical timeline recorded.</p>
            ) : (
              Object.entries(data.monthlyTrends).map(([month, count]) => (
                <div key={month} className="flex justify-between items-center p-2 rounded-xl bg-slate-50 dark:bg-dark-900/40 border border-slate-200/40 dark:border-white/5 text-xs font-mono">
                  <span className="text-slate-600 dark:text-dark-300 font-bold">{month}</span>
                  <span className="bg-brand-500/10 text-brand-500 dark:text-cyber-neon px-2.5 py-0.5 rounded font-bold">{count} bugs</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Top Recurring Exceptions Heatmap / Table */}
        <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-4 lg:col-span-2">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
            <h3 className="text-xs font-black text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <Terminal className="h-4 w-4 text-pink-500" /> Top Recurring Exceptions & Root Causes
            </h3>
            
            {/* Search filter */}
            <div className="relative">
              <Search className="h-3.5 w-3.5 absolute left-3 top-2.5 text-slate-400" />
              <input 
                type="text" 
                placeholder="Filter exceptions..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs rounded-xl bg-slate-100 dark:bg-dark-800 border border-slate-200 dark:border-white/5 text-slate-700 dark:text-white focus:outline-none"
              />
            </div>
          </div>

          <div className="overflow-x-auto min-w-0 pt-2">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-white/5 text-slate-400 dark:text-dark-400 uppercase font-mono text-[10px]">
                  <th className="py-2.5 px-2">Exception Signature</th>
                  <th className="py-2.5 px-2">Occurrences</th>
                  <th className="py-2.5 px-2">Heat Indicator</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/5 font-sans">
                {filteredExceptions.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="py-6 text-center text-slate-400 italic">No exceptions matching query.</td>
                  </tr>
                ) : (
                  filteredExceptions.slice(0, 5).map((exc, idx) => {
                    const maxVal = Math.max(...data.topExceptions.map(e => e.count), 1);
                    const pct = Math.round((exc.count / maxVal) * 100);
                    return (
                      <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-dark-800/30">
                        <td className="py-2.5 px-2 font-mono font-bold text-pink-500 text-[11px]">{exc.name}</td>
                        <td className="py-2.5 px-2 font-mono font-bold text-slate-800 dark:text-white">{exc.count} times</td>
                        <td className="py-2.5 px-2">
                          <div className="w-32 bg-slate-100 dark:bg-white/5 rounded-full h-1.5 overflow-hidden">
                            <div 
                              className={`h-1.5 rounded-full ${pct > 60 ? 'bg-pink-500' : 'bg-brand-500'}`} 
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      {/* Frequently Suggested Fixes */}
      <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-4">
        <h3 className="text-xs font-black text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-2">
          <Brain className="h-4 w-4 text-amber-500" /> Frequently Suggested Fixes & Mitigations
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-1">
          {data.frequentlySuggestedFixes.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No suggested fixes recorded yet.</p>
          ) : (
            data.frequentlySuggestedFixes.map((item, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-50 dark:bg-dark-900/40 border border-slate-200/50 dark:border-white/5 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-500 font-mono text-[9px] font-bold">Fix Recommendation</span>
                  <span className="text-[10px] font-mono text-slate-400 font-bold">{item.count}x Applied</span>
                </div>
                <p className="text-xs font-semibold text-slate-700 dark:text-slate-200 leading-relaxed">{item.fix}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;
