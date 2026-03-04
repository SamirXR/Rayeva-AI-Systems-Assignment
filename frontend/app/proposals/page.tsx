'use client';

import { useState } from 'react';
import { FileText, Download, Package, Receipt, Globe, Sparkles, CheckCircle } from 'lucide-react';
import { api } from '@/lib/api';

function generateProposalPDF(result: any) {
  const w = window.open('', '_blank');
  if (!w) return;
  const productRows = (result.product_mix || []).map((p: any) =>
    `<tr>
      <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb">${p.product_name}<br/><span style="font-size:11px;color:#6b7280">${p.category} · ${p.selection_reasoning}</span></td>
      <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:center">${p.recommended_quantity}</td>
      <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:right;font-family:monospace">₹${p.unit_price_estimate}</td>
      <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:right;font-family:monospace;font-weight:600">₹${p.subtotal?.toLocaleString()}</td>
    </tr>`
  ).join('');
  const impactPoints = (result.impact?.key_impact_points || []).map((p: string) => `<li style="margin-bottom:4px">✓ ${p}</li>`).join('');
  const cb = result.cost_breakdown || {};
  const html = `<!DOCTYPE html><html><head><title>Proposal #${result.proposal_id}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#fff;color:#111;padding:40px}
.container{max-width:800px;margin:0 auto}
h1{font-size:20px;font-weight:600;margin-bottom:4px}
.sub{color:#6b7280;font-size:12px;margin-bottom:24px}
h2{font-size:14px;font-weight:600;margin:24px 0 12px;text-transform:uppercase;letter-spacing:1px;color:#374151}
.strategy{background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin-bottom:20px}
.strategy .title{font-size:13px;font-weight:600;margin-bottom:6px}
.strategy p{font-size:13px;color:#4b5563}
table{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:20px}
thead{background:#f3f4f6}
th{text-align:left;padding:8px 12px;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;color:#6b7280;border-bottom:2px solid #e5e7eb}
.cost-row{display:flex;justify-content:space-between;padding:6px 0;font-size:13px}
.cost-row.total{border-top:2px solid #e5e7eb;padding-top:10px;margin-top:6px;font-weight:700;font-size:15px}
.impact{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin-top:20px}
.impact h3{color:#166534;font-size:15px;margin-bottom:8px}
.impact p{font-size:13px;color:#4b5563;margin-bottom:12px}
.impact ul{list-style:none;font-size:12px;color:#4b5563}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}
.stat{text-align:center;background:#fff;border:1px solid #bbf7d0;border-radius:6px;padding:8px}
.stat .val{font-size:16px;font-weight:700;color:#166534}
.stat .lbl{font-size:10px;color:#6b7280}
.meta{margin-top:24px;padding-top:16px;border-top:1px solid #e5e7eb;font-size:11px;color:#9ca3af;line-height:1.8}
</style></head><body>
<div class="container">
<h1>B2B Proposal #${result.proposal_id}</h1>
<p class="sub">Rayeva AI · Budget utilization: ${result.budget_utilization_percent}%</p>
<div class="strategy"><div class="title">Strategy</div><p>${result.strategy_summary}</p></div>
<h2>Product Mix</h2>
<table><thead><tr><th>Product</th><th style="text-align:center">Qty</th><th style="text-align:right">Unit Price</th><th style="text-align:right">Subtotal</th></tr></thead><tbody>${productRows}</tbody></table>
<h2>Cost Breakdown</h2>
<div class="cost-row"><span>Subtotal</span><span style="font-family:monospace">₹${cb.subtotal?.toLocaleString()}</span></div>
${cb.discount_percent > 0 ? `<div class="cost-row" style="color:#16a34a"><span>Volume Discount (${cb.discount_percent}%)</span><span style="font-family:monospace">-₹${cb.discount_amount?.toLocaleString()}</span></div>` : ''}
<div class="cost-row"><span>GST (${cb.gst_percent}%)</span><span style="font-family:monospace">₹${cb.gst_amount?.toLocaleString()}</span></div>
<div class="cost-row"><span>Shipping (est.)</span><span style="font-family:monospace">₹${cb.shipping_estimate?.toLocaleString()}</span></div>
<div class="cost-row total"><span>Grand Total</span><span style="font-family:monospace">₹${cb.grand_total?.toLocaleString()}</span></div>
<div class="impact">
<h3>${result.impact?.headline || 'Impact Positioning'}</h3>
<p>${result.impact?.impact_summary || ''}</p>
<div class="stats">
<div class="stat"><div class="val">${result.impact?.plastic_saved_kg || 0}kg</div><div class="lbl">Plastic Saved</div></div>
<div class="stat"><div class="val">${result.impact?.carbon_avoided_kg || 0}kg</div><div class="lbl">CO₂ Avoided</div></div>
<div class="stat"><div class="val">${result.impact?.trees_equivalent || 0}</div><div class="lbl">Trees Equiv.</div></div>
<div class="stat"><div class="val">${result.impact?.local_artisans_supported || 0}</div><div class="lbl">Artisans</div></div>
</div>
<ul>${impactPoints}</ul>
</div>
<div class="meta">Model: ${result.ai_model} · Prompt: ${result.prompt_version} · Latency: ${result.total_latency_ms}ms</div>
</div>
<script>window.onload=()=>{window.print()}</script>
</body></html>`;
  w.document.write(html);
  w.document.close();
}

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
        <h1 className="text-2xl font-semibold text-fg tracking-tight">B2B Proposal Generator</h1>
        <p className="text-fg-secondary text-sm mt-1">Module 2 — AI-powered sustainable product proposals with cost breakdown</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Input Form */}
        <div className="lg:col-span-2 card">
          <h2 className="font-medium text-fg text-sm mb-4 flex items-center gap-2">
            <FileText size={14} className="text-fg-secondary" />
            Client Requirements
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-1.5">Client Name</label>
              <input className="input" placeholder="e.g., TechCorp India" value={form.client_name}
                onChange={(e) => setForm({ ...form, client_name: e.target.value })} required />
            </div>
            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-1.5">Budget (INR)</label>
              <input type="number" className="input" placeholder="e.g., 50000" value={form.budget}
                onChange={(e) => setForm({ ...form, budget: e.target.value })} required />
            </div>
            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-1.5">Occasion (optional)</label>
              <input className="input" placeholder="e.g., Diwali corporate gifting" value={form.occasion}
                onChange={(e) => setForm({ ...form, occasion: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-fg-secondary mb-1.5">Min Qty</label>
                <input type="number" className="input" value={form.quantity_min}
                  onChange={(e) => setForm({ ...form, quantity_min: parseInt(e.target.value) })} />
              </div>
              <div>
                <label className="block text-xs font-medium text-fg-secondary mb-1.5">Max Qty</label>
                <input type="number" className="input" value={form.quantity_max}
                  onChange={(e) => setForm({ ...form, quantity_max: parseInt(e.target.value) })} />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-2">Category Preferences</label>
              <div className="flex flex-wrap gap-1.5">
                {categories.map((c) => (
                  <button key={c} type="button"
                    className={form.category_preferences.includes(c) ? 'chip chip-active' : 'chip'}
                    onClick={() => toggleItem(form.category_preferences, c, 'category_preferences')}
                  >{c}</button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-2">Sustainability Goals</label>
              <div className="flex flex-wrap gap-1.5">
                {goals.map((g) => (
                  <button key={g} type="button"
                    className={form.sustainability_goals.includes(g) ? 'chip chip-active' : 'chip'}
                    onClick={() => toggleItem(form.sustainability_goals, g, 'sustainability_goals')}
                  >{g}</button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-1.5">Special Requirements</label>
              <textarea className="input min-h-[60px]" placeholder="Any specific needs..."
                value={form.special_requirements}
                onChange={(e) => setForm({ ...form, special_requirements: e.target.value })} />
            </div>

            <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2" disabled={loading}>
              {loading ? (
                <><span className="spinner w-4 h-4" /> Generating Proposal...</>
              ) : (
                <><Sparkles size={15} /> Generate Proposal</>
              )}
            </button>
          </form>
          {error && (
            <div className="mt-4 p-3 rounded-lg text-sm badge-red border">{error}</div>
          )}
        </div>

        {/* Results */}
        <div className="lg:col-span-3 space-y-6">
          {!result && !loading && (
            <div className="card flex items-center justify-center py-20 text-fg-muted text-sm">
              Fill in client requirements and generate a proposal
            </div>
          )}
          {loading && (
            <div className="card flex items-center justify-center py-20">
              <div className="text-center">
                <div className="spinner w-8 h-8 mx-auto mb-3" />
                <p className="text-fg-secondary text-sm">AI is crafting the proposal (2 AI calls)...</p>
                <p className="text-fg-muted text-xs mt-1">Step 1: Product selection → Step 2: Impact analysis</p>
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
          <h3 className="font-medium text-fg text-sm flex items-center gap-2">
            <FileText size={14} className="text-fg-secondary" />
            Proposal #{result.proposal_id}
          </h3>
          <div className="flex items-center gap-2">
            <span className="badge-green">{result.budget_utilization_percent}% budget</span>
            <button onClick={() => generateProposalPDF(result)}
              className="chip flex items-center gap-1.5">
              <Download size={12} /> Export PDF
            </button>
          </div>
        </div>
        <p className="text-fg-secondary text-sm">{result.strategy_summary}</p>
      </div>

      {/* Product Mix */}
      <div className="card">
        <h3 className="font-medium text-fg text-sm mb-4 flex items-center gap-2">
          <Package size={14} className="text-fg-secondary" />
          Recommended Product Mix
        </h3>
        <div className="divide-y divide-surface-300">
          {result.product_mix?.map((p: any, i: number) => (
            <div key={i} className="py-3 first:pt-0 last:pb-0">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-medium text-fg text-sm">{p.product_name}</div>
                  <div className="text-xs text-fg-muted mt-0.5">{p.category} · {p.selection_reasoning}</div>
                  <div className="flex gap-1 mt-1.5">
                    {p.sustainability_tags?.map((t: string) => (
                      <span key={t} className="badge-green">{t}</span>
                    ))}
                  </div>
                </div>
                <div className="text-right text-sm">
                  <div className="font-mono text-fg font-medium">₹{p.subtotal?.toLocaleString()}</div>
                  <div className="text-fg-muted text-xs">{p.recommended_quantity}× ₹{p.unit_price_estimate}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="card">
        <h3 className="font-medium text-fg text-sm mb-4 flex items-center gap-2">
          <Receipt size={14} className="text-fg-secondary" />
          Cost Breakdown
          <span className="text-[10px] text-fg-muted font-normal">(server-validated)</span>
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-fg-secondary">Subtotal</span><span className="font-mono text-fg">₹{result.cost_breakdown?.subtotal?.toLocaleString()}</span></div>
          {result.cost_breakdown?.discount_percent > 0 && (
            <div className="flex justify-between text-success">
              <span>Volume Discount ({result.cost_breakdown.discount_percent}%)</span>
              <span className="font-mono">-₹{result.cost_breakdown.discount_amount?.toLocaleString()}</span>
            </div>
          )}
          <div className="flex justify-between"><span className="text-fg-secondary">GST ({result.cost_breakdown?.gst_percent}%)</span><span className="font-mono text-fg">₹{result.cost_breakdown?.gst_amount?.toLocaleString()}</span></div>
          <div className="flex justify-between"><span className="text-fg-secondary">Shipping (est.)</span><span className="font-mono text-fg">₹{result.cost_breakdown?.shipping_estimate?.toLocaleString()}</span></div>
          <div className="flex justify-between pt-2 border-t border-surface-300 font-semibold">
            <span className="text-fg">Grand Total</span>
            <span className="font-mono text-fg text-lg">₹{result.cost_breakdown?.grand_total?.toLocaleString()}</span>
          </div>
        </div>
        <div className="mt-3 text-xs text-fg-muted italic">All math computed server-side — AI suggests products, Python validates costs.</div>
      </div>

      {/* Impact */}
      <div className="card border-success/20">
        <h3 className="font-medium text-fg text-sm mb-3 flex items-center gap-2">
          <Globe size={14} className="text-success" />
          Impact Positioning
        </h3>
        <div className="text-base font-semibold text-fg mb-2">{result.impact?.headline}</div>
        <p className="text-fg-secondary text-sm mb-4">{result.impact?.impact_summary}</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <ImpactStat label="Plastic Saved" value={`${result.impact?.plastic_saved_kg}kg`} />
          <ImpactStat label="CO₂ Avoided" value={`${result.impact?.carbon_avoided_kg}kg`} />
          <ImpactStat label="Trees Equiv." value={result.impact?.trees_equivalent} />
          <ImpactStat label="Artisans" value={result.impact?.local_artisans_supported} />
        </div>
        {result.impact?.key_impact_points && (
          <ul className="mt-4 space-y-1.5 text-sm text-fg-secondary">
            {result.impact.key_impact_points.map((p: string, i: number) => (
              <li key={i} className="flex items-start gap-2">
                <CheckCircle size={13} className="text-success mt-0.5 shrink-0" />
                {p}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Metadata */}
      <div className="text-xs text-fg-muted text-center font-mono">
        Model: {result.ai_model} · Prompt: {result.prompt_version} · Total latency: {result.total_latency_ms}ms
      </div>
    </>
  );
}

function ImpactStat({ label, value }: { label: string; value: any }) {
  return (
    <div className="rounded-lg p-3 text-center border border-success/20" style={{ background: 'var(--badge-success-bg)' }}>
      <div className="text-xl font-bold text-success">{value}</div>
      <div className="text-xs text-fg-muted">{label}</div>
    </div>
  );
}
