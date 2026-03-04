'use client';

import { useEffect, useState } from 'react';
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
        <h1 className="text-3xl font-bold text-gray-900">AI Call Logs</h1>
        <p className="text-gray-500 mt-1">Every AI call logged: prompt version, tokens, latency, raw I/O</p>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {['', 'category', 'proposal', 'proposal_impact'].map((m) => (
          <button key={m}
            className={`text-sm px-4 py-2 rounded-lg transition-colors ${
              moduleFilter === m ? 'bg-brand-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            onClick={() => setModuleFilter(m)}
          >
            {m || 'All'}
          </button>
        ))}
      </div>

      {/* Logs Table */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600" /></div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No AI calls logged yet. Use the Categorizer or Proposal Generator first.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-3 pr-4">ID</th>
                  <th className="pb-3 pr-4">Module</th>
                  <th className="pb-3 pr-4">Model</th>
                  <th className="pb-3 pr-4">Prompt</th>
                  <th className="pb-3 pr-4">Tokens (In/Out)</th>
                  <th className="pb-3 pr-4">Latency</th>
                  <th className="pb-3 pr-4">Status</th>
                  <th className="pb-3">Time</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <>
                    <tr key={log.id}
                      className="border-b last:border-0 hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
                    >
                      <td className="py-3 pr-4 font-mono text-gray-600">{log.id}</td>
                      <td className="py-3 pr-4"><span className="badge-blue">{log.module}</span></td>
                      <td className="py-3 pr-4 font-mono text-xs text-gray-600">{log.model}</td>
                      <td className="py-3 pr-4 font-mono text-xs">{log.prompt_version}</td>
                      <td className="py-3 pr-4 font-mono text-xs">{log.input_tokens}/{log.output_tokens}</td>
                      <td className="py-3 pr-4 font-mono text-xs">{log.latency_ms}ms</td>
                      <td className="py-3 pr-4">
                        {log.parsed_success ? <span className="badge-green">OK</span> : <span className="badge-red">FAIL</span>}
                      </td>
                      <td className="py-3 text-xs text-gray-500">{log.created_at}</td>
                    </tr>
                    {expandedId === log.id && (
                      <tr key={`${log.id}-expanded`}>
                        <td colSpan={8} className="p-4 bg-gray-50">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <div className="text-xs font-semibold text-gray-500 mb-1">RAW INPUT (PROMPT)</div>
                              <pre className="text-xs bg-white p-3 rounded border overflow-x-auto max-h-60">
                                {JSON.stringify(log.raw_input, null, 2)}
                              </pre>
                            </div>
                            <div>
                              <div className="text-xs font-semibold text-gray-500 mb-1">RAW OUTPUT (AI RESPONSE)</div>
                              <pre className="text-xs bg-white p-3 rounded border overflow-x-auto max-h-60">
                                {JSON.stringify(log.raw_output, null, 2)}
                              </pre>
                            </div>
                          </div>
                          {log.error && (
                            <div className="mt-3 p-2 bg-red-50 rounded text-red-700 text-xs">Error: {log.error}</div>
                          )}
                          <div className="mt-2 text-xs text-gray-400">
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
        <div className="mt-4 pt-3 border-t text-sm text-gray-500">Total: {total} log entries</div>
      </div>
    </div>
  );
}
