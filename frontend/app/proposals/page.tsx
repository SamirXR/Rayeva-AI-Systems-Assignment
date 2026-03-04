'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

export default function ProposalsPage() {
  const [form, setForm] = useState({
    client_name: '',
    budget: '',
    category_preferences: [] as string[],
    sustainability_goals: [] as string[],
    occasion: '',
    quantity_min: 10,
    quantity_max: 100,
    special_requirements: '',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const categories = [
    'Home & Living', 'Personal Care', 'Kitchen & Dining', 'Fashion & Accessories',
    'Stationery & Office', 'Food & Beverages', 'Cleaning & Household',
  ];
  const goals = ['plastic-free', 'organic', 'fair-trade', 'zero-waste', 'vegan', 'locally-sourced'];

  const toggleItem = (list: string[], item: string, key: 'category_preferences' | 'sustainability_goals') => {
    const newList = list.includes(item) ? list.filter(i => i !== item) : [...list, item];
    setForm({ ...form, [key]: newList });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await api.generateProposal({
        ...form,
        budget: parseFloat(form.budget),
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Proposal generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">B2B Proposal Generator</h1>
        <p className="text-gray-500 mt-1">Module 2 — AI-powered sustainable product proposals with cost breakdown</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Input Form */}
        <div className="lg:col-span-2 card">
          <h2 className="font-semibold text-gray-700 mb-4">Client Requirements</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Client Name</label>
              <input className="input" placeholder="e.g., TechCorp India" value={form.client_name}
                onChange={(e) => setForm({ ...form, client_name: e.target.value })} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Budget (₹)</label>
              <input type="number" className="input" placeholder="e.g., 50000" value={form.budget}
                onChange={(e) => setForm({ ...form, budget: e.target.value })} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Occasion (optional)</label>
              <input className="input" placeholder="e.g., Diwali corporate gifting" value={form.occasion}
                onChange={(e) => setForm({ ...form, occasion: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Min Quantity</label>
                <input type="number" className="input" value={form.quantity_min}
                  onChange={(e) => setForm({ ...form, quantity_min: parseInt(e.target.value) })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Quantity</label>
                <input type="number" className="input" value={form.quantity_max}
                  onChange={(e) => setForm({ ...form, quantity_max: parseInt(e.target.value) })} />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category Preferences</label>
              <div className="flex flex-wrap gap-1.5">
                {categories.map((c) => (
                  <button key={c} type="button"
                    className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
                      form.category_preferences.includes(c)
                        ? 'bg-brand-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    onClick={() => toggleItem(form.category_preferences, c, 'category_preferences')}
                  >{c}</button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sustainability Goals</label>
              <div className="flex flex-wrap gap-1.5">
                {goals.map((g) => (
                  <button key={g} type="button"
                    className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
                      form.sustainability_goals.includes(g)
                        ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    onClick={() => toggleItem(form.sustainability_goals, g, 'sustainability_goals')}
                  >{g}</button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Special Requirements</label>
              <textarea className="input min-h-[60px]" placeholder="Any specific needs..."
                value={form.special_requirements}
                onChange={(e) => setForm({ ...form, special_requirements: e.target.value })} />
            </div>

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  Generating Proposal...
                </span>
              ) : (
                '📋 Generate Proposal'
              )}
            </button>
          </form>
          {error && <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>}
        </div>

        {/* Results */}
        <div className="lg:col-span-3 space-y-6">
          {!result && !loading && (
            <div className="card flex items-center justify-center py-20 text-gray-400">
              <p>Fill in client requirements and generate a proposal</p>
            </div>
          )}
          {loading && (
            <div className="card flex items-center justify-center py-20">
              <div className="text-center">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-600 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">AI is crafting the proposal (2 AI calls)...</p>
                <p className="text-gray-400 text-xs mt-1">Step 1: Product selection → Step 2: Impact analysis</p>
              </div>
            </div>
          )}
          {result && <ProposalDisplay result={result} />}
        </div>
      </div>
    </div>
  );
}

function ProposalDisplay({ result }: { result: any }) {
  return (
    <>
      {/* Strategy */}
      <div className="card">
        <div className="flex justify-between items-start mb-3">
          <h3 className="font-semibold text-gray-700">Proposal #{result.proposal_id}</h3>
          <span className="badge-green">{result.budget_utilization_percent}% budget used</span>
        </div>
        <p className="text-gray-600 text-sm">{result.strategy_summary}</p>
      </div>

      {/* Product Mix */}
      <div className="card">
        <h3 className="font-semibold text-gray-700 mb-4">Recommended Product Mix</h3>
        <div className="divide-y">
          {result.product_mix?.map((p: any, i: number) => (
            <div key={i} className="py-3 first:pt-0 last:pb-0">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-medium text-gray-900">{p.product_name}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{p.category} · {p.selection_reasoning}</div>
                  <div className="flex gap-1 mt-1.5">
                    {p.sustainability_tags?.map((t: string) => (
                      <span key={t} className="badge-green">{t}</span>
                    ))}
                  </div>
                </div>
                <div className="text-right text-sm">
                  <div className="font-mono text-gray-900">₹{p.subtotal?.toLocaleString()}</div>
                  <div className="text-gray-500">{p.recommended_quantity}× ₹{p.unit_price_estimate}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="card">
        <h3 className="font-semibold text-gray-700 mb-4">Cost Breakdown (Server-Validated)</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-gray-600">Subtotal</span><span className="font-mono">₹{result.cost_breakdown?.subtotal?.toLocaleString()}</span></div>
          {result.cost_breakdown?.discount_percent > 0 && (
            <div className="flex justify-between text-green-700">
              <span>Volume Discount ({result.cost_breakdown.discount_percent}%)</span>
              <span className="font-mono">-₹{result.cost_breakdown.discount_amount?.toLocaleString()}</span>
            </div>
          )}
          <div className="flex justify-between"><span className="text-gray-600">GST ({result.cost_breakdown?.gst_percent}%)</span><span className="font-mono">₹{result.cost_breakdown?.gst_amount?.toLocaleString()}</span></div>
          <div className="flex justify-between"><span className="text-gray-600">Shipping (est.)</span><span className="font-mono">₹{result.cost_breakdown?.shipping_estimate?.toLocaleString()}</span></div>
          <div className="flex justify-between pt-2 border-t font-bold">
            <span>Grand Total</span>
            <span className="font-mono text-lg">₹{result.cost_breakdown?.grand_total?.toLocaleString()}</span>
          </div>
        </div>
        <div className="mt-3 text-xs text-gray-400 italic">All math computed server-side — AI suggests products, Python validates costs.</div>
      </div>

      {/* Impact */}
      <div className="card bg-gradient-to-br from-green-50 to-white">
        <h3 className="font-semibold text-brand-800 mb-3">🌍 Impact Positioning</h3>
        <div className="text-lg font-semibold text-brand-700 mb-2">{result.impact?.headline}</div>
        <p className="text-gray-600 text-sm mb-4">{result.impact?.impact_summary}</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <ImpactStat label="Plastic Saved" value={`${result.impact?.plastic_saved_kg}kg`} />
          <ImpactStat label="CO₂ Avoided" value={`${result.impact?.carbon_avoided_kg}kg`} />
          <ImpactStat label="Trees Equiv." value={result.impact?.trees_equivalent} />
          <ImpactStat label="Artisans" value={result.impact?.local_artisans_supported} />
        </div>
        {result.impact?.key_impact_points && (
          <ul className="mt-4 space-y-1 text-sm text-gray-600">
            {result.impact.key_impact_points.map((p: string, i: number) => (
              <li key={i} className="flex items-start gap-2"><span className="text-brand-500 mt-0.5">✓</span>{p}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Metadata */}
      <div className="text-xs text-gray-400 text-center">
        Model: {result.ai_model} · Prompt: {result.prompt_version} · Total latency: {result.total_latency_ms}ms
      </div>
    </>
  );
}

function ImpactStat({ label, value }: { label: string; value: any }) {
  return (
    <div className="bg-white rounded-lg p-3 border border-green-200 text-center">
      <div className="text-xl font-bold text-brand-700">{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
