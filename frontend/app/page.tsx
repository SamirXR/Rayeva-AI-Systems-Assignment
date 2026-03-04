'use client';

import { useEffect, useState } from 'react';
import { Package, FileText, Cpu, Zap, TrendingUp, Activity } from 'lucide-react';
import { api } from '@/lib/api';

interface Metrics {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  success_rate: number;
  avg_latency_ms: number;
  total_tokens: {
    input: number;
    output: number;
    thinking: number;
    total: number;
  };
  module_breakdown: { module: string; calls: number; avg_latency_ms: number }[];
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [products, setProducts] = useState<any>(null);
  const [proposals, setProposals] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getMetrics().catch(() => null),
      api.getProducts().catch(() => null),
      api.getProposals().catch(() => null),
    ]).then(([m, p, pr]) => {
      setMetrics(m);
      setProducts(p);
      setProposals(pr);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="spinner w-6 h-6" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-fg tracking-tight">Dashboard</h1>
        <p className="text-fg-secondary text-sm mt-1">Rayeva AI — Sustainable Commerce Platform Metrics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Products Categorized" value={products?.total ?? 0} icon={<Package size={20} />} />
        <StatCard label="Proposals Generated" value={proposals?.total ?? 0} icon={<FileText size={20} />} />
        <StatCard label="AI Calls Made" value={metrics?.total_calls ?? 0} icon={<Cpu size={20} />} />
        <StatCard label="Avg Latency" value={`${metrics?.avg_latency_ms?.toFixed(0) ?? 0}ms`} icon={<Zap size={20} />} />
      </div>

      {/* Token Usage & Success Rate */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="card">
          <h3 className="font-medium text-fg text-sm mb-4 flex items-center gap-2">
            <Activity size={14} className="text-fg-secondary" />
            Token Usage
          </h3>
          <div className="space-y-3">
            <TokenBar label="Input Tokens" value={metrics?.total_tokens?.input ?? 0} color="bg-info" />
            <TokenBar label="Output Tokens" value={metrics?.total_tokens?.output ?? 0} color="bg-success" />
            <TokenBar label="Thinking Tokens" value={metrics?.total_tokens?.thinking ?? 0} color="bg-purple-500" />
          </div>
          <div className="mt-4 pt-3 border-t border-surface-300 text-xs text-fg-muted font-mono">
            Total: {(metrics?.total_tokens?.total ?? 0).toLocaleString()} tokens
          </div>
        </div>

        <div className="card">
          <h3 className="font-medium text-fg text-sm mb-4 flex items-center gap-2">
            <TrendingUp size={14} className="text-fg-secondary" />
            AI Call Success Rate
          </h3>
          <div className="flex items-center justify-center py-6">
            <div className="relative w-28 h-28">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="var(--surface-300)"
                  strokeWidth="3"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="var(--success)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeDasharray={`${metrics?.success_rate ?? 0}, 100`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-semibold text-fg font-mono">{metrics?.success_rate ?? 0}%</span>
              </div>
            </div>
          </div>
          <div className="text-center text-xs text-fg-muted">
            {metrics?.successful_calls ?? 0} successful / {metrics?.failed_calls ?? 0} failed
          </div>
        </div>
      </div>

      {/* Module Breakdown */}
      {metrics?.module_breakdown && metrics.module_breakdown.length > 0 && (
        <div className="card">
          <h3 className="font-medium text-fg text-sm mb-4">Module Breakdown</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-fg-muted border-b border-surface-300 text-xs uppercase tracking-wider">
                <th className="pb-2">Module</th>
                <th className="pb-2">Calls</th>
                <th className="pb-2">Avg Latency</th>
              </tr>
            </thead>
            <tbody>
              {metrics.module_breakdown.map((m) => (
                <tr key={m.module} className="border-b border-surface-300 last:border-0">
                  <td className="py-2.5 font-medium text-fg">{m.module}</td>
                  <td className="py-2.5 font-mono text-fg-secondary">{m.calls}</td>
                  <td className="py-2.5 font-mono text-fg-secondary">{m.avg_latency_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="card flex items-center gap-4">
      <div className="w-10 h-10 rounded-lg bg-surface-300 flex items-center justify-center text-fg-secondary">
        {icon}
      </div>
      <div>
        <div className="text-xl font-semibold text-fg font-mono">{value}</div>
        <div className="text-xs text-fg-muted">{label}</div>
      </div>
    </div>
  );
}

function TokenBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-fg-secondary">{label}</span>
        <span className="font-mono text-fg">{value.toLocaleString()}</span>
      </div>
      <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--progress-track)' }}>
        <div
          className={`h-full ${color} rounded-full transition-all`}
          style={{ width: `${Math.min((value / Math.max(value, 1)) * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}
