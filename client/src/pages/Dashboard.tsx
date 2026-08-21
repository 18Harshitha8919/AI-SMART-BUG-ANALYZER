import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Bug, 
  Layers, 
  Activity, 
  AlertTriangle, 
  Clock, 
  User, 
  ExternalLink,
  ChevronRight,
  Database,
  Terminal,
  RefreshCw,
  FolderOpen,
  CheckCircle,
  Brain,
  Wrench
} from 'lucide-react';

interface BugReport {
  bugId: string;
  title: string;
  description: string;
  severity: string;
  priority: string;
  environment: string;
  module: string;
  reporterName: string;
  stackTrace: string;
  errorLog: string;
  cleanedDocument: string;
  attachments: any[];
  createdAt: string;
  agentInsights?: any;
}


const Dashboard: React.FC = () => {
  const [bugs, setBugs] = useState<BugReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Selected bug for detailed inspect sidebar/modal
  const [selectedBug, setSelectedBug] = useState<BugReport | null>(null);
  const [similarBugs, setSimilarBugs] = useState<any[]>([]);
  const [similarLoading, setSimilarLoading] = useState(false);

  const fetchBugs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get('/api/bugs');
      setBugs(res.data || []);
    } catch (e: any) {
      setError('Failed to fetch submitted bugs. Make sure the Node gateway server is online on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSimilar = async (bugId: string) => {
    setSimilarLoading(true);
    setSimilarBugs([]);
    try {
      const res = await axios.get(`/api/similar/${bugId}`);
      setSimilarBugs(res.data.similarBugs || []);
    } catch (e) {
      console.error("Failed to load similar bugs from RAG pipeline", e);
    } finally {
      setSimilarLoading(false);
    }
  };

  useEffect(() => {
    fetchBugs();
  }, []);

  const selectBugForInspect = (bug: BugReport) => {
    setSelectedBug(bug);
    fetchSimilar(bug.bugId);
  };

  const handleClearDatabase = async () => {
    if (window.confirm("Are you sure you want to delete all defect tickets and clear vector store database memory?")) {
      try {
        await axios.post('/api/bugs/clear');
        fetchBugs();
        setSelectedBug(null);
      } catch (e) {
        alert("Failed to clear database");
      }
    }
  };

  // Computations
  const totalBugs = bugs.length;
  const criticalCount = bugs.filter(b => b.severity.toLowerCase() === 'critical').length;
  const highCount = bugs.filter(b => b.severity.toLowerCase() === 'high').length;
  const devCount = bugs.filter(b => b.environment.toLowerCase() === 'development').length;
  const prodCount = bugs.filter(b => b.environment.toLowerCase() === 'production').length;

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex justify-between items-center border-b border-slate-200 dark:border-white/5 pb-4">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white tracking-tight">Telemetry Dashboard</h2>
          <p className="text-slate-500 dark:text-dark-400 text-xs">Real-time status of ingested bug reports and duplicate analysis.</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={handleClearDatabase}
            className="px-4 py-2.5 rounded-xl border border-red-500/20 hover:bg-red-500/10 text-red-600 dark:text-cyber-pink text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 shrink-0"
          >
            Clear All Tickets
          </button>
          <button 
            onClick={fetchBugs} 
            disabled={loading}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-white/5 hover:bg-slate-100 dark:hover:bg-dark-800 transition-all text-slate-600 dark:text-dark-300 cursor-pointer shrink-0"
          >
            <RefreshCw className={`h-4.5 w-4.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-cyber-pink text-xs font-semibold flex gap-2 items-center">
          <AlertTriangle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Stats counters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          { label: 'Total Ingested', val: totalBugs, color: 'text-brand-500 dark:text-cyber-neon', icon: Bug, desc: 'All submissions' },
          { label: 'Critical Severity', val: criticalCount, color: 'text-red-500 dark:text-cyber-pink', icon: AlertTriangle, desc: 'OOM / Security leaks' },
          { label: 'Production Tier', val: prodCount, color: 'text-amber-500 dark:text-cyber-purple', icon: Layers, desc: 'Live environment errors' },
          { label: 'Development Tier', val: devCount, color: 'text-emerald-500 dark:text-cyber-green', icon: Activity, desc: 'Sandbox runtime issues' }
        ].map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="glass p-5 rounded-2xl border border-slate-200 dark:border-white/5 flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-[10px] text-slate-400 dark:text-dark-400 uppercase tracking-wider font-extrabold">{card.label}</span>
                <div className={`text-2xl font-black ${card.color}`}>{card.val}</div>
                <div className="text-[10px] text-slate-400 dark:text-dark-500 font-mono">{card.desc}</div>
              </div>
              <div className="bg-slate-100 dark:bg-dark-900/60 p-3 rounded-xl">
                <Icon className={`h-5 w-5 ${card.color}`} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Grid list */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        
        {/* Left lists table (Col span 3) */}
        <div className="xl:col-span-3 glass p-5 rounded-2xl border border-slate-200 dark:border-white/5 space-y-4">
          <h3 className="text-slate-800 dark:text-white font-extrabold text-sm uppercase tracking-wider flex items-center gap-1.5">
            <FolderOpen className="h-4.5 w-4.5 text-brand-500" /> Ingested Defect Tickets
          </h3>
          
          {loading ? (
            <div className="py-12 flex justify-center items-center">
              <RefreshCw className="h-8 w-8 text-brand-500 animate-spin" />
            </div>
          ) : bugs.length === 0 ? (
            <div className="text-center py-16 text-slate-400 dark:text-dark-500 space-y-2">
              <Bug className="h-10 w-10 mx-auto opacity-30" />
              <p className="text-xs">No bug tickets submitted yet. Use the **Submit Bug** module to file report logs.</p>
            </div>
          ) : (
            <div className="overflow-x-auto min-w-0">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-white/5 text-slate-400 dark:text-dark-400 uppercase font-mono tracking-wider">
                    <th className="py-3 px-2 font-bold">Bug ID</th>
                    <th className="py-3 px-2 font-bold">Summary</th>
                    <th className="py-3 px-2 font-bold">Module</th>
                    <th className="py-3 px-2 font-bold">Severity</th>
                    <th className="py-3 px-2 font-bold">Priority</th>
                    <th className="py-3 px-2 font-bold">Reporter</th>
                    <th className="py-3 px-2"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                  {bugs.map((bug) => (
                    <tr 
                      key={bug.bugId} 
                      onClick={() => selectBugForInspect(bug)}
                      className={`hover:bg-slate-50 dark:hover:bg-dark-800/40 cursor-pointer transition-colors ${
                        selectedBug?.bugId === bug.bugId ? 'bg-brand-500/5 dark:bg-brand-500/10' : ''
                      }`}
                    >
                      <td className="py-3.5 px-2 font-mono font-bold text-brand-500 dark:text-cyber-neon">
                        {bug.bugId}
                      </td>
                      <td className="py-3.5 px-2 font-medium text-slate-800 dark:text-slate-100 max-w-[200px] truncate">
                        {bug.title}
                      </td>
                      <td className="py-3.5 px-2 text-slate-500 dark:text-dark-300 font-medium">
                        {bug.module}
                      </td>
                      <td className="py-3.5 px-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          bug.severity.toLowerCase() === 'critical' ? 'bg-red-100 text-red-700 dark:bg-cyber-pink/15 dark:text-cyber-pink' :
                          bug.severity.toLowerCase() === 'high' ? 'bg-purple-100 text-purple-700 dark:bg-cyber-purple/15 dark:text-cyber-purple' :
                          'bg-sky-100 text-sky-700 dark:bg-cyber-neon/15 dark:text-cyber-neon'
                        }`}>
                          {bug.severity}
                        </span>
                      </td>
                      <td className="py-3.5 px-2 text-slate-600 dark:text-dark-300 font-semibold">{bug.priority}</td>
                      <td className="py-3.5 px-2 text-slate-500 dark:text-dark-400 font-medium">{bug.reporterName}</td>
                      <td className="py-3.5 px-2 text-right">
                        <ChevronRight className="h-4.5 w-4.5 text-slate-400 dark:text-dark-500" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right drawer / inspection view (Col span 2 - wide and readable) */}
        <div className="xl:col-span-2 space-y-6">
          {selectedBug ? (
            <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-6">
              {/* Header */}
              <div className="border-b border-slate-200 dark:border-white/5 pb-4">
                <div className="flex justify-between items-start gap-2">
                  <div>
                    <span className="text-[10px] text-brand-500 dark:text-cyber-neon font-mono font-bold">{selectedBug.bugId}</span>
                    <h4 className="text-base font-black text-slate-800 dark:text-white mt-1 leading-snug">{selectedBug.title}</h4>
                  </div>
                </div>
                <div className="flex gap-2 items-center text-[10px] text-slate-400 dark:text-dark-400 font-mono mt-2">
                  <User className="h-3.5 w-3.5" /> {selectedBug.reporterName} • <Clock className="h-3.5 w-3.5" /> {new Date(selectedBug.createdAt).toLocaleDateString()}
                </div>
              </div>

              {/* Info grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-100 dark:bg-dark-900/40 border border-slate-200/50 dark:border-white/5">
                  <div className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Severity</div>
                  <span className={`inline-block mt-1 px-2.5 py-0.5 rounded font-extrabold text-[10px] ${
                    selectedBug.severity.toLowerCase() === 'critical' ? 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400' :
                    selectedBug.severity.toLowerCase() === 'high' ? 'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400' :
                    selectedBug.severity.toLowerCase() === 'medium' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400' :
                    'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400'
                  }`}>{selectedBug.severity}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-100 dark:bg-dark-900/40 border border-slate-200/50 dark:border-white/5">
                  <div className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Priority</div>
                  <span className={`inline-block mt-1 px-2.5 py-0.5 rounded font-mono font-black text-[10px] ${
                    selectedBug.priority === 'P1' ? 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400 animate-pulse' :
                    selectedBug.priority === 'P2' ? 'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400' :
                    selectedBug.priority === 'P3' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400' :
                    'bg-slate-100 text-slate-700 dark:bg-white/10 dark:text-slate-400'
                  }`}>{selectedBug.priority}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-100 dark:bg-dark-900/40 border border-slate-200/50 dark:border-white/5">
                  <div className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Environment</div>
                  <span className="text-slate-800 dark:text-white font-semibold block mt-1">{selectedBug.environment}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-100 dark:bg-dark-900/40 border border-slate-200/50 dark:border-white/5">
                  <div className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Module</div>
                  <span className="text-slate-800 dark:text-white font-semibold block mt-1">{selectedBug.module}</span>
                </div>
              </div>

              {/* Text Description */}
              <div className="space-y-1.5">
                <span className="text-[10px] text-slate-400 dark:text-dark-400 font-bold uppercase tracking-wider">Bug Description</span>
                <p className="p-4 rounded-xl bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-white/5 text-xs text-slate-600 dark:text-dark-200 whitespace-pre-wrap leading-relaxed max-h-36 overflow-y-auto">
                  {selectedBug.description}
                </p>
              </div>

              {/* AI Diagnostic Report */}
              {selectedBug.agentInsights?.triage && (
                <div className="p-5 rounded-xl bg-purple-500/10 border border-purple-500/20 space-y-3 dark:bg-cyber-purple/10 dark:border-cyber-purple/20">
                  <span className="text-[10px] text-purple-600 dark:text-cyber-purple font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                    <Activity className="h-4.5 w-4.5 shrink-0 text-purple-500" /> AI Diagnostic Report
                  </span>
                  
                  <div className="text-xs space-y-3">
                    <div className="grid grid-cols-2 gap-3 pb-3 border-b border-slate-200/50 dark:border-white/5">
                      <div>
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Predicted Module</span>
                        <span className="font-extrabold text-slate-800 dark:text-white block mt-0.5">{selectedBug.agentInsights.triage.triage_component}</span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Confidence Indicator</span>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="w-full bg-slate-200 dark:bg-white/10 rounded-full h-1.5 overflow-hidden">
                            <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${selectedBug.agentInsights.triage.confidence}%` }} />
                          </div>
                          <span className="font-mono font-bold text-purple-600 dark:text-cyber-purple text-[10px]">{selectedBug.agentInsights.triage.confidence}%</span>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Severity Reason</span>
                        <p className="text-[10px] text-slate-600 dark:text-dark-300 mt-1 leading-normal">{selectedBug.agentInsights.triage.severity_reason || selectedBug.agentInsights.triage.reasoning}</p>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Priority Reason</span>
                        <p className="text-[10px] text-slate-600 dark:text-dark-300 mt-1 leading-normal">{selectedBug.agentInsights.triage.priority_reason || selectedBug.agentInsights.triage.reasoning}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Log Analysis */}
              {selectedBug.agentInsights?.log_analysis && (
                <div className="p-5 rounded-xl bg-pink-500/10 border border-pink-500/20 space-y-3.5 dark:bg-cyber-pink/10 dark:border-cyber-pink/20">
                  <span className="text-[10px] text-pink-600 dark:text-cyber-pink font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                    <Terminal className="h-4.5 w-4.5 shrink-0 text-pink-500" /> AI Log Analysis
                  </span>

                  <div className="text-xs space-y-3">
                    <div className="grid grid-cols-2 gap-3 pb-2 border-b border-slate-200/50 dark:border-white/5">
                      <div>
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Exception Type</span>
                        <span className="font-mono text-[10px] text-pink-500 font-bold block mt-0.5">{selectedBug.agentInsights.log_analysis.exception_type}</span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Failing Execution Frame</span>
                        <span className="font-mono text-[10px] text-slate-700 dark:text-white font-semibold block mt-0.5">
                          {selectedBug.agentInsights.log_analysis.failed_class}.{selectedBug.agentInsights.log_analysis.failed_method}()
                        </span>
                      </div>
                    </div>

                    <div>
                      <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Error Message</span>
                      <p className="text-[10px] font-mono text-slate-600 dark:text-dark-200 mt-1 leading-normal italic bg-slate-950/5 dark:bg-black/20 p-2 rounded border border-slate-200/50 dark:border-white/5">
                        {selectedBug.agentInsights.log_analysis.error_message}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Failure Reason</span>
                        <p className="text-[10px] text-slate-600 dark:text-dark-300 mt-1 leading-normal">{selectedBug.agentInsights.log_analysis.failure_reason}</p>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Captured Timestamp</span>
                        <p className="text-[10px] font-mono text-slate-500 mt-1">{selectedBug.agentInsights.log_analysis.timestamp}</p>
                      </div>
                    </div>

                    {selectedBug.agentInsights.log_analysis.affected_code_path && selectedBug.agentInsights.log_analysis.affected_code_path.length > 0 && (
                      <div className="pt-2 border-t border-slate-200/50 dark:border-white/5">
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block mb-1">Affected Code Path Flow</span>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {selectedBug.agentInsights.log_analysis.affected_code_path.map((frame: string, idx: number) => (
                            <span key={idx} className="px-2 py-0.5 rounded bg-pink-500/10 text-pink-500 font-mono text-[9px] border border-pink-500/20">
                              {frame}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Stack trace raw */}
              {selectedBug.stackTrace && (
                <div className="space-y-1.5">
                  <span className="text-[10px] text-slate-400 dark:text-dark-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Terminal className="h-4 w-4" /> Stack Trace analysis
                  </span>
                  <pre className="p-4 rounded-xl bg-slate-900 border border-slate-950 text-emerald-400 font-mono text-[10px] overflow-x-auto max-h-36 select-all leading-relaxed shadow-inner">
                    <code>{selectedBug.stackTrace}</code>
                  </pre>
                </div>
              )}

              {/* Root Cause Hypothesis */}
              {selectedBug.agentInsights?.root_cause && (
                <div className="p-5 rounded-xl bg-orange-500/10 border border-orange-500/20 space-y-3 dark:bg-amber-500/10 dark:border-amber-500/20">
                  <span className="text-[10px] text-orange-600 dark:text-amber-500 font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                    <Brain className="h-4.5 w-4.5 shrink-0 text-amber-500" /> AI Root Cause Hypothesis
                  </span>
                  
                  <div className="text-xs space-y-3">
                    <div className="flex justify-between items-center pb-2 border-b border-slate-200/50 dark:border-white/5">
                      <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase">Root Cause</span>
                      <span className="font-mono font-bold text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">{selectedBug.agentInsights.root_cause.confidence}% Confidence</span>
                    </div>
                    
                    <p className="text-slate-800 dark:text-slate-100 font-extrabold text-[12px] leading-relaxed">
                      {selectedBug.agentInsights.root_cause.root_cause}
                    </p>

                    <div>
                      <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Explanation</span>
                      <p className="text-[10px] text-slate-600 dark:text-dark-300 mt-1 leading-relaxed">
                        {selectedBug.agentInsights.root_cause.explanation || selectedBug.agentInsights.root_cause.reasoning}
                      </p>
                    </div>

                    {selectedBug.agentInsights.root_cause.supporting_evidence?.length > 0 && (
                      <div className="pt-2 border-t border-slate-200/50 dark:border-white/5">
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block mb-1">Supporting Historical Bugs</span>
                        <div className="flex gap-1.5 flex-wrap">
                          {selectedBug.agentInsights.root_cause.supporting_evidence.map((bugId: string, idx: number) => (
                            <span key={idx} className="px-2.5 py-0.5 rounded bg-amber-500/10 text-amber-500 font-mono text-[9px] font-bold border border-amber-500/20">
                              {bugId}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* AI Remediation Agent */}
              {selectedBug.agentInsights?.remediation && (
                <div className="p-5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 space-y-3.5 dark:bg-cyber-green/10 dark:border-cyber-green/20">
                  <span className="text-[10px] text-emerald-600 dark:text-cyber-green font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                    <Wrench className="h-4.5 w-4.5 shrink-0 text-emerald-500" /> AI Remediation Recommender
                  </span>

                  <div className="text-xs space-y-3.5">
                    <div>
                      <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Recommended Fix</span>
                      <p className="text-slate-800 dark:text-emerald-400 font-extrabold mt-1 leading-normal">{selectedBug.agentInsights.remediation.immediate_fix}</p>
                    </div>
                    
                    <div>
                      <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block">Long-Term Recommendation</span>
                      <p className="text-slate-600 dark:text-dark-300 mt-1 leading-normal">{selectedBug.agentInsights.remediation.long_term}</p>
                    </div>

                    {selectedBug.agentInsights.remediation.best_practices?.length > 0 && (
                      <div className="border-t border-slate-200/50 dark:border-white/5 pt-3">
                        <span className="text-[9px] text-slate-400 dark:text-dark-500 font-bold uppercase block mb-1">Engineering Best Practices</span>
                        <ul className="list-disc pl-4 space-y-1.5 text-slate-600 dark:text-dark-300 text-[10px] mt-1.5 font-medium">
                          {selectedBug.agentInsights.remediation.best_practices.map((bp: string, idx: number) => (
                            <li key={idx} className="leading-relaxed">{bp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Resolution Verification (Milestone 4 Knowledge Growth Trigger) */}
              {selectedBug.agentInsights?.remediation && (
                <div className="p-5 rounded-xl border border-slate-200 dark:border-white/5 space-y-4 bg-slate-50 dark:bg-dark-900/30">
                  <span className="text-[10px] text-slate-500 dark:text-dark-400 font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                    <CheckCircle className="h-4.5 w-4.5 text-emerald-500" /> Resolution Verification
                  </span>
                  
                  {selectedBug.agentInsights.status === "resolved" ? (
                    <div className="space-y-2">
                      <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-cyber-green text-xs font-bold flex gap-2 items-center">
                        <CheckCircle className="h-5 w-5 shrink-0" />
                        <span>This defect has been verified & resolved. Resolution playbooks are indexed in RAG memory!</span>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4 text-xs">
                      <p className="text-[11px] text-slate-500 dark:text-dark-400">
                        Verify the resolution details below to commit this resolved defect to the vector store Knowledge Base.
                      </p>
                      
                      <div className="space-y-3 bg-slate-100 dark:bg-dark-900/50 p-3.5 rounded-xl">
                        <div>
                          <label className="text-[9px] font-bold text-slate-400 dark:text-dark-500 uppercase block mb-1 font-mono">Verified Resolution Action</label>
                          <textarea 
                            id="verified-fix-input"
                            defaultValue={selectedBug.agentInsights.remediation.immediate_fix}
                            className="w-full p-2.5 text-xs rounded-xl bg-white dark:bg-dark-950 border border-slate-200 dark:border-white/5 text-slate-800 dark:text-white focus:outline-none h-16"
                          />
                        </div>
                        <div>
                          <label className="text-[9px] font-bold text-slate-400 dark:text-dark-500 uppercase block mb-1 font-mono">Confirmed Root Cause</label>
                          <textarea 
                            id="verified-rc-input"
                            defaultValue={selectedBug.agentInsights.root_cause?.root_cause || selectedBug.description}
                            className="w-full p-2.5 text-xs rounded-xl bg-white dark:bg-dark-950 border border-slate-200 dark:border-white/5 text-slate-800 dark:text-white focus:outline-none h-16"
                          />
                        </div>
                      </div>

                      <button
                        onClick={async () => {
                          const fixVal = (document.getElementById("verified-fix-input") as HTMLTextAreaElement)?.value || selectedBug.agentInsights.remediation.immediate_fix;
                          const rcVal = (document.getElementById("verified-rc-input") as HTMLTextAreaElement)?.value || selectedBug.agentInsights.root_cause?.root_cause || selectedBug.description;
                          
                          try {
                            // 1. Trigger Knowledge Base growth
                            const kbRes = await axios.post('/api/knowledge/add', {
                              bugId: selectedBug.bugId,
                              title: selectedBug.title,
                              description: selectedBug.description,
                              stackTrace: selectedBug.stackTrace,
                              rootCause: rcVal,
                              fixAction: fixVal,
                              severity: selectedBug.severity,
                              priority: selectedBug.priority,
                              category: selectedBug.module,
                              component: selectedBug.agentInsights.triage?.triage_component || selectedBug.module
                            });

                            // 2. Mark bug as resolved in database
                            await axios.post('/api/bugs/resolve', { bugId: selectedBug.bugId });

                            alert(kbRes.data.message || "Resolution verified successfully!");
                            
                            // Reload Dashboard bug states
                            fetchBugs();
                            // Update local inspect state
                            setSelectedBug({
                              ...selectedBug,
                              agentInsights: {
                                ...selectedBug.agentInsights,
                                status: "resolved"
                              }
                            });
                          } catch (err: any) {
                            alert(err.response?.data?.error || "Failed to verify resolution");
                          }
                        }}
                        className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
                      >
                        <CheckCircle className="h-4.5 w-4.5" /> Mark as Resolved & Verify
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Duplicate Detection Agent */}
              {selectedBug.agentInsights?.duplicates && selectedBug.agentInsights.duplicates.length > 0 ? (
                <div className="space-y-3 border-t border-slate-200 dark:border-white/5 pt-4">
                  <span className="text-[10px] text-slate-400 dark:text-dark-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Database className="h-4 w-4 text-brand-500" />
                    Duplicate Detection Agent (Top Similar Defects)
                  </span>

                  <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                    {selectedBug.agentInsights.duplicates.map((dup: any, index: number) => (
                      <div key={index} className="p-4 rounded-xl bg-slate-100 dark:bg-dark-900 border border-slate-200/50 dark:border-white/5 text-[11px] space-y-2">
                        <div className="flex justify-between items-center border-b border-slate-200/30 dark:border-white/5 pb-1">
                          <span className="font-mono font-bold text-slate-800 dark:text-white">{dup.bug_id}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                            dup.similarity > 90 ? 'bg-red-100 text-red-700 dark:bg-cyber-pink/15 dark:text-cyber-pink animate-pulse' : 'bg-brand-500/10 text-brand-500 dark:text-cyber-neon'
                          }`}>
                            {dup.similarity}% Similarity
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-600 dark:text-dark-300 leading-normal font-sans">
                          <strong>Summary:</strong> {dup.summary}
                        </p>
                        <p className="text-[10px] text-slate-600 dark:text-dark-300 leading-normal font-sans border-t border-dashed border-slate-200 dark:border-white/5 pt-1.5">
                          <strong>Resolution:</strong> {dup.resolution}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                /* RAG pipeline matches fallback for older tickets */
                <div className="space-y-2 border-t border-slate-200 dark:border-white/5 pt-3">
                  <span className="text-[10px] text-slate-400 dark:text-dark-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Database className="h-3.5 w-3.5 text-brand-500" />
                    RAG Historical Match Retrieval
                  </span>

                  {similarLoading ? (
                    <div className="flex gap-2 items-center text-xs text-brand-500 font-mono py-2">
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" /> Querying FAISS...
                    </div>
                  ) : similarBugs.length === 0 ? (
                    <div className="text-xs text-slate-400 dark:text-dark-500 italic py-2">
                      No matching defects found.
                    </div>
                  ) : (
                    <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                      {similarBugs.map((sim, index) => (
                        <div key={index} className="p-3 rounded-xl bg-slate-100 dark:bg-dark-900 border border-slate-200/50 dark:border-white/5 text-[11px] space-y-1.5">
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-slate-800 dark:text-white truncate pr-2">{sim.title}</span>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                              sim.score > 0.90 ? 'bg-red-100 text-red-700 dark:bg-cyber-pink/15 dark:text-cyber-pink' : 'bg-brand-500/10 text-brand-500 dark:text-cyber-neon'
                            }`}>
                              {(sim.score * 100).toFixed(0)}% Match
                            </span>
                          </div>
                          <div className="text-slate-500 dark:text-dark-400 font-mono text-[9px] uppercase">
                            Source: {sim.source} • Code: {sim.bug_id}
                          </div>
                          <p className="text-[10px] text-slate-500 dark:text-dark-300 leading-normal line-clamp-3">
                            {sim.description}
                          </p>
                          <div className="grid grid-cols-1 gap-1 border-t border-slate-200/60 dark:border-white/5 pt-1.5 text-[10px]">
                            <div><span className="text-slate-400 dark:text-dark-500 font-bold uppercase">Root Cause:</span> <span className="text-slate-600 dark:text-dark-300">{sim.root_cause}</span></div>
                            <div><span className="text-slate-400 dark:text-dark-500 font-bold uppercase">Resolution:</span> <span className="text-slate-600 dark:text-dark-300">{sim.resolution}</span></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="glass p-8 rounded-2xl text-center text-slate-400 dark:text-dark-500 space-y-2 h-96 flex flex-col justify-center border border-dashed border-slate-200 dark:border-white/5">
              <Bug className="h-8 w-8 mx-auto opacity-35" />
              <p className="text-xs max-w-[200px] mx-auto leading-relaxed">Select a bug ticket from the grid list to trace details and RAG vector store matches.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
