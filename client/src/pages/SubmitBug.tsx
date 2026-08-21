import React, { useState } from 'react';
import axios from 'axios';
import { 
  Bug, 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  RefreshCw,
  Terminal,
  FileCode,
  Layers,
  Database,
  Info
} from 'lucide-react';

interface FileDetail {
  filename: string;
  filePath: string;
  extractedText: string;
}

const SubmitBug: React.FC = () => {
  // Form fields
  const [projectName, setProjectName] = useState('AI Smart Bug Analyzer');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState('Medium');
  const [priority, setPriority] = useState('Medium');
  const [environment, setEnvironment] = useState('Production');
  const [moduleName, setModuleName] = useState('Backend');
  const [reporterName, setReporterName] = useState('');
  const [stackTrace, setStackTrace] = useState('');
  const [errorLog, setErrorLog] = useState('');

  // File states
  const [fileLoading, setFileLoading] = useState(false);
  const [parsedFiles, setParsedFiles] = useState<FileDetail[]>([]);

  // Submission Results
  const [submitLoading, setSubmitLoading] = useState(false);
  const [successResult, setSuccessResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  // File Upload Ingestion (Module 1)
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    setFileLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const parsed = {
        filename: res.data.filename,
        filePath: res.data.filePath,
        extractedText: res.data.extractedText
      };
      
      setParsedFiles(prev => [...prev, parsed]);
      
      // Auto-extract content to populate trace or logs based on size
      if (res.data.extractedText.toLowerCase().includes('stack') || res.data.extractedText.toLowerCase().includes('trace')) {
        setStackTrace(prev => prev ? `${prev}\n\n[Extracted from ${file.name}]:\n${res.data.extractedText}` : res.data.extractedText);
      } else {
        setErrorLog(prev => prev ? `${prev}\n\n[Extracted from ${file.name}]:\n${res.data.extractedText}` : res.data.extractedText);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to extract text. File was uploaded, but the Python AI Service could not parse it.');
    } finally {
      setFileLoading(false);
    }
  };

  // Submit report handler (Module 1, 4, 5)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim() || !reporterName.trim()) {
      setError("Please fill out all required fields: Title, Description, and Reporter Name.");
      return;
    }

    setSubmitLoading(true);
    setError(null);
    setSuccessResult(null);

    const payload = {
      title,
      description,
      severity,
      priority,
      environment,
      moduleName,
      reporterName,
      stackTrace,
      errorLog,
      attachments: parsedFiles.map(f => ({ filename: f.filename, filePath: f.filePath }))
    };

    try {
      const res = await axios.post('/api/submitBug', payload);
      setSuccessResult(res.data);
      
      // Reset form on success
      setTitle('');
      setDescription('');
      setStackTrace('');
      setErrorLog('');
      setParsedFiles([]);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to submit bug report. Ensure Node server on port 5000 is online.');
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white tracking-tight">Submit Defect logs</h2>
        <p className="text-slate-500 dark:text-dark-400 text-xs">File bug tickets and cross-reference with historical FAISS knowledge bases.</p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-cyber-pink text-xs font-semibold flex gap-2 items-center">
          <AlertTriangle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Success result view showing RAG retrieves and duplicates (Module 1, 4, 5) */}
      {successResult && (
        <div className="glass p-6 rounded-2xl border border-emerald-500/30 dark:border-cyber-green/35 space-y-5 animate-pulse-border">
          <div className="flex items-center gap-3 border-b border-slate-200 dark:border-white/5 pb-3">
            <CheckCircle className="h-6 w-6 text-emerald-600 dark:text-cyber-green animate-bounce" />
            <div>
              <h3 className="text-sm font-extrabold text-slate-800 dark:text-white">Bug Submitted Successfully!</h3>
              <p className="text-[10px] text-slate-500 dark:text-dark-400 font-mono">
                Assigned ID: <span className="text-brand-500 dark:text-cyber-neon font-black">{successResult.bugId}</span>
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Duplicate detection badge (Module 5) */}
            <div className="md:col-span-1 p-4 rounded-xl bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-white/5 space-y-1.5 flex flex-col justify-center">
              <span className="text-[10px] text-slate-400 dark:text-dark-500 font-bold uppercase tracking-wider">Duplicate Scan Result</span>
              <div className={`text-sm font-extrabold ${
                successResult.duplicateStatus === 'Potential Duplicate Bug' ? 'text-red-500 dark:text-cyber-pink' : 'text-emerald-600 dark:text-cyber-green'
              }`}>
                {successResult.duplicateStatus}
              </div>
              <p className="text-[10px] text-slate-500 dark:text-dark-400">
                {successResult.duplicateStatus === 'Potential Duplicate Bug' 
                  ? 'A similar defect already exists in the system with >90% match.' 
                  : 'This ticket matches no other active open tickets.'}
              </p>
            </div>

            {/* RAG pipeline retrieved defects list (Module 4) */}
            <div className="md:col-span-2 space-y-3">
              <span className="text-[10px] text-slate-400 dark:text-dark-400 font-bold uppercase tracking-wider flex items-center gap-1">
                <Database className="h-3.5 w-3.5 text-brand-500" /> Top 5 Similar Historical Defects (FAISS RAG)
              </span>
              
              {successResult.similarBugs.length === 0 ? (
                <div className="text-xs text-slate-400 dark:text-dark-500 italic">No historical matches in database.</div>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {successResult.similarBugs.map((bug: any, i: number) => (
                    <div key={i} className="p-3 rounded-xl bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-white/5 text-[11px] space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="font-extrabold text-slate-800 dark:text-white">{bug.project} - {bug.bug_id}</span>
                        <span className="font-mono text-brand-500 dark:text-cyber-neon">{(bug.score * 100).toFixed(0)}% Similarity</span>
                      </div>
                      <p className="text-slate-700 dark:text-dark-200"><span className="text-slate-400 dark:text-dark-500 font-semibold">Title:</span> {bug.title}</p>
                      <p className="text-slate-600 dark:text-dark-300 font-mono text-[10px]"><span className="text-slate-400 dark:text-dark-500 font-bold font-sans uppercase">Root Cause:</span> {bug.root_cause}</p>
                      <p className="text-slate-600 dark:text-dark-300 font-mono text-[10px]"><span className="text-slate-400 dark:text-dark-500 font-bold font-sans uppercase">Resolution:</span> {bug.resolution}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Submit form */}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Core fields (Left) */}
        <div className="lg:col-span-2 glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-5">
          <h3 className="text-slate-800 dark:text-white font-extrabold text-sm uppercase tracking-wider border-b border-slate-200 dark:border-white/5 pb-2">
            Defect Details
          </h3>
          
          <div className="space-y-1.5">
            <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Bug Summary / Title *</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. MemoryLeak in RewriteEngine when matching regex groups"
              className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Full Problem Description *</label>
            <textarea
              required
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide a comprehensive description of the runtime exception..."
              className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all font-mono"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold flex items-center gap-1.5">
                <Terminal className="h-4 w-4" /> Stack Trace logs
              </label>
              <textarea
                rows={4}
                value={stackTrace}
                onChange={(e) => setStackTrace(e.target.value)}
                placeholder="Paste code trace logs or compile exception lines here..."
                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-[10px] text-emerald-600 dark:text-emerald-400 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all font-mono"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold flex items-center gap-1.5">
                <FileCode className="h-4 w-4" /> Error logs
              </label>
              <textarea
                rows={4}
                value={errorLog}
                onChange={(e) => setErrorLog(e.target.value)}
                placeholder="Paste crash dumps or system error traces here..."
                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-[10px] text-emerald-600 dark:text-emerald-400 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all font-mono"
              />
            </div>
          </div>

          {/* File Upload Dropzone */}
          <div className="space-y-2">
            <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Parser file uploads (.txt, .log, .pdf, .docx, .csv)</label>
            <div className="border-2 border-dashed border-slate-200 dark:border-white/5 rounded-2xl p-6 text-center hover:border-brand-500 cursor-pointer relative bg-slate-50/50 dark:bg-dark-900/20">
              <input
                type="file"
                onChange={handleFileUpload}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              <div className="flex flex-col items-center justify-center gap-2">
                <UploadCloud className="h-8 w-8 text-brand-500" />
                <span className="text-xs text-slate-700 dark:text-dark-200 font-semibold">
                  {fileLoading ? 'Extracting document text...' : 'Click to select file or drag it here'}
                </span>
                <span className="text-[10px] text-slate-400 dark:text-dark-500 font-mono">Autoreads and appends text blocks</span>
              </div>
            </div>

            {/* List of uploaded parsed files */}
            {parsedFiles.length > 0 && (
              <div className="space-y-2">
                {parsedFiles.map((pf, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-100 dark:bg-dark-900 border border-slate-200 dark:border-white/5 flex justify-between items-center text-[10px]">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-brand-500" />
                      <div>
                        <div className="text-slate-800 dark:text-white font-semibold">{pf.filename}</div>
                        <div className="text-[9px] text-slate-400 dark:text-dark-500 truncate max-w-sm">{pf.filePath}</div>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-cyber-green/15 dark:text-cyber-green uppercase font-bold">Extracted</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Project & Metadata (Right) */}
        <div className="space-y-6">
          <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-white/5 space-y-4">
            <h3 className="text-slate-800 dark:text-white font-extrabold text-sm uppercase tracking-wider border-b border-slate-200 dark:border-white/5 pb-2">
              Metadata Context
            </h3>

            <div className="space-y-1.5">
              <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Project Name</label>
              <input
                type="text"
                required
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Reporter Name *</label>
              <input
                type="text"
                required
                value={reporterName}
                onChange={(e) => setReporterName(e.target.value)}
                placeholder="Jane Developer"
                className="w-full px-3 py-2 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Failing Module</label>
              <select
                value={moduleName}
                onChange={(e) => setModuleName(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none"
              >
                <option value="Backend">Backend Core API</option>
                <option value="Frontend">Frontend UI Layout</option>
                <option value="Database">Database Query/Pool</option>
                <option value="Auth">Security Middleware</option>
                <option value="Worker">Celery Background Job</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Server Environment</label>
              <select
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none"
              >
                <option value="Production">Production Server</option>
                <option value="Staging">Staging Box</option>
                <option value="Development">Local Development</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-slate-600 dark:text-dark-300 text-xs font-semibold">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-dark-900 border border-slate-200 dark:border-white/5 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitLoading || fileLoading}
            className="w-full bg-brand-500 hover:bg-brand-600 disabled:bg-brand-500/50 text-white font-bold py-3.5 px-4 rounded-xl text-xs flex items-center justify-center gap-2 shadow-glass-glow cursor-pointer transition-all uppercase tracking-wider font-mono"
          >
            {submitLoading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin text-white" />
                Ingesting defect...
              </>
            ) : (
              <>
                <Bug className="h-4 w-4 text-cyber-neon" />
                Submit to RAG Grid
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SubmitBug;
