'use client';

import { useEffect, useState } from 'react';
import { ScrollText, ChevronDown, ChevronRight } from 'lucide-react';
import { api } from '@/lib/api';

export default function LogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [moduleFilter, setModuleFilter] = useState('');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = moduleFilter ? `module=${moduleFilter}` : '';
      const data = await api.getLogs(params);
      setLogs(data.logs || []);
      setTotal(data.total || 0);
    } catch {
      setLogs([]);
    }
    setLoading(false);
  };

  useEffect(() => { fetchLogs(); }, [moduleFilter]);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-fg tracking-tight">AI Call Logs</h1>
        <p className="text-fg-secondary text-sm mt-1">Every AI call logged: prompt version, tokens, latency, raw I/O</p>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {['', 'category', 'proposal', 'proposal_impact'].map((m) => (
          <button key={m}
            className={moduleFilter === m ? 'chip chip-active' : 'chip'}
            onClick={() => setModuleFilter(m)}
          >
            {m || 'All'}
          </button>
        ))}
      </div>

      {/* Logs Table */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-12"><div className="spinner w-8 h-8" /></div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12 text-fg-muted text-sm">No AI calls logged yet. Use the Categorizer or Proposal Generator first.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-fg-muted text-[11px] uppercase tracking-wider border-b border-surface-300">
                  <th className="pb-3 pr-4 font-medium">ID</th>
                  <th className="pb-3 pr-4 font-medium">Module</th>
                  <th className="pb-3 pr-4 font-medium">Model</th>
                  <th className="pb-3 pr-4 font-medium">Prompt</th>
                  <th className="pb-3 pr-4 font-medium">Tokens</th>
                  <th className="pb-3 pr-4 font-medium">Latency</th>
                  <th className="pb-3 pr-4 font-medium">Status</th>
                  <th className="pb-3 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <>
                    <tr key={log.id}
                      className="border-b border-surface-300 last:border-0 hover:bg-surface-200 cursor-pointer transition-colors"
                      onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
                    >
                      <td className="py-3 pr-4 font-mono text-fg-secondary text-xs">
                        <span className="flex items-center gap-1.5">
                          {expandedId === log.id ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                          {log.id}
                        </span>
                      </td>
                      <td className="py-3 pr-4"><span className="badge-blue">{log.module}</span></td>
                      <td className="py-3 pr-4 font-mono text-xs text-fg-secondary">{log.model}</td>
                      <td className="py-3 pr-4 font-mono text-xs text-fg-secondary">{log.prompt_version}</td>
                      <td className="py-3 pr-4 font-mono text-xs text-fg-secondary">{log.input_tokens}/{log.output_tokens}</td>
                      <td className="py-3 pr-4 font-mono text-xs text-fg-secondary">{log.latency_ms}ms</td>
                      <td className="py-3 pr-4">
                        {log.parsed_success ? <span className="badge-green">OK</span> : <span className="badge-red">FAIL</span>}
                      </td>
                      <td className="py-3 text-xs text-fg-muted">{log.created_at}</td>
                    </tr>
                    {expandedId === log.id && (
                      <tr key={`${log.id}-expanded`}>
                        <td colSpan={8} className="p-4 bg-surface-200">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <div className="text-[10px] font-medium text-fg-muted uppercase tracking-wider mb-1.5">Raw Input (Prompt)</div>
                              <pre className="text-xs p-3 rounded-md border overflow-x-auto max-h-60 font-mono" style={{ background: 'var(--code-bg)', borderColor: 'var(--code-border)', color: 'var(--fg)' }}>
                                {JSON.stringify(log.raw_input, null, 2)}
                              </pre>
                            </div>
                            <div>
                              <div className="text-[10px] font-medium text-fg-muted uppercase tracking-wider mb-1.5">Raw Output (AI Response)</div>
                              <pre className="text-xs p-3 rounded-md border overflow-x-auto max-h-60 font-mono" style={{ background: 'var(--code-bg)', borderColor: 'var(--code-border)', color: 'var(--fg)' }}>
                                {JSON.stringify(log.raw_output, null, 2)}
                              </pre>
                            </div>
                          </div>
                          {log.error && (
                            <div className="mt-3 p-2 rounded-md text-xs badge-red border">{log.error}</div>
                          )}
                          <div className="mt-2 text-xs text-fg-muted font-mono">
                            Correlation: {log.correlation_id} · Thinking tokens: {log.thinking_tokens}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="mt-4 pt-3 border-t border-surface-300 text-sm text-fg-muted">Total: {total} log entries</div>
      </div>
    </div>
  );
}
