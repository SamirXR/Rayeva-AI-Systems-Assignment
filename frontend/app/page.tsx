'use client';

import { useEffect, useState } from 'react';
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
    return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600" /></div>;
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Rayeva AI — Sustainable Commerce Platform Metrics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Products Categorized"
          value={products?.total ?? 0}
          icon="📦"
        />
        <StatCard
          label="Proposals Generated"
          value={proposals?.total ?? 0}
          icon="📋"
        />
        <StatCard
          label="AI Calls Made"
          value={metrics?.total_calls ?? 0}
          icon="🤖"
        />
        <StatCard
          label="Avg Latency"
          value={`${metrics?.avg_latency_ms?.toFixed(0) ?? 0}ms`}
          icon="⚡"
        />
      </div>

      {/* Token Usage & Success Rate */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-4">Token Usage</h3>
          <div className="space-y-3">
            <TokenBar label="Input Tokens" value={metrics?.total_tokens?.input ?? 0} color="bg-blue-500" />
            <TokenBar label="Output Tokens" value={metrics?.total_tokens?.output ?? 0} color="bg-green-500" />
            <TokenBar label="Thinking Tokens" value={metrics?.total_tokens?.thinking ?? 0} color="bg-purple-500" />
          </div>
          <div className="mt-4 pt-3 border-t text-sm text-gray-500">
            Total: {(metrics?.total_tokens?.total ?? 0).toLocaleString()} tokens
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-4">AI Call Success Rate</h3>
          <div className="flex items-center justify-center py-6">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="3"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#22c55e"
                  strokeWidth="3"
                  strokeDasharray={`${metrics?.success_rate ?? 0}, 100`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-900">{metrics?.success_rate ?? 0}%</span>
              </div>
            </div>
          </div>
          <div className="text-center text-sm text-gray-500">
            {metrics?.successful_calls ?? 0} successful / {metrics?.failed_calls ?? 0} failed
          </div>
        </div>
      </div>

      {/* Module Breakdown */}
      {metrics?.module_breakdown && metrics.module_breakdown.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-4">Module Breakdown</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Module</th>
                <th className="pb-2">Calls</th>
                <th className="pb-2">Avg Latency</th>
              </tr>
            </thead>
            <tbody>
              {metrics.module_breakdown.map((m) => (
                <tr key={m.module} className="border-b last:border-0">
                  <td className="py-2 font-medium">{m.module}</td>
                  <td className="py-2">{m.calls}</td>
                  <td className="py-2">{m.avg_latency_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: string | number; icon: string }) {
  return (
    <div className="card flex items-center gap-4">
      <span className="text-3xl">{icon}</span>
      <div>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="text-sm text-gray-500">{label}</div>
      </div>
    </div>
  );
}

function TokenBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-mono text-gray-800">{value.toLocaleString()}</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all`}
          style={{ width: `${Math.min((value / Math.max(value, 1)) * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}
