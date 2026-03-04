'use client';

import { useState } from 'react';
import { Sparkles, Download, Leaf, Tag, Layers, FlaskConical } from 'lucide-react';
import { api } from '@/lib/api';

function generateCategorizePDF(result: any) {
  const w = window.open('', '_blank');
  if (!w) return;
  const html = `<!DOCTYPE html><html><head><title>Categorization — ${result.product_id}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#fff;color:#111;padding:40px}
.container{max-width:700px;margin:0 auto;border:1px solid #e5e7eb;border-radius:8px;padding:32px}
h1{font-size:18px;font-weight:600;margin-bottom:4px}
.sub{color:#6b7280;font-size:12px;margin-bottom:24px}
.section{margin-bottom:20px}
.label{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#9ca3af;margin-bottom:6px}
.value{font-size:14px}
.value.lg{font-size:18px;font-weight:600}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tag{background:#f3f4f6;border:1px solid #e5e7eb;padding:3px 10px;border-radius:20px;font-size:11px;color:#2563eb}
.tag.green{color:#16a34a;border-color:#bbf7d0;background:#dcfce7}
.tag.gray{color:#6b7280;border-color:#e5e7eb}
.bar-bg{height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden;margin-top:4px}
.bar-fill{height:100%;background:linear-gradient(90deg,#16a34a,#22c55e);border-radius:4px}
.meta{margin-top:24px;padding-top:16px;border-top:1px solid #e5e7eb;font-size:11px;color:#9ca3af;line-height:1.8}
</style></head><body>
<div class="container">
<h1>AI Product Categorization</h1>
<p class="sub">Rayeva AI — Product #${result.product_id}</p>
<div class="section"><div class="label">Primary Category</div><div class="value lg">${result.primary_category} <span style="font-size:12px;color:#16a34a;font-weight:400">${(result.primary_category_confidence * 100).toFixed(0)}%</span></div></div>
<div class="section"><div class="label">Sub-category</div><div class="value">${result.sub_category}</div><div style="font-size:12px;color:#6b7280;margin-top:2px;font-style:italic">${result.sub_category_reasoning || ''}</div></div>
<div class="section"><div class="label">Sustainability Score</div><div class="value" style="font-weight:600;color:#16a34a">${result.sustainability_score}/10</div><div class="bar-bg"><div class="bar-fill" style="width:${(result.sustainability_score / 10) * 100}%"></div></div></div>
<div class="section"><div class="label">SEO Tags</div><div class="tags">${(result.seo_tags || []).map((t: string) => `<span class="tag">${t}</span>`).join('')}</div></div>
<div class="section"><div class="label">Sustainability Filters</div><div class="tags">${(result.sustainability_filters || []).map((f: string) => `<span class="tag green">${f}</span>`).join('')}</div></div>
<div class="section"><div class="label">Detected Materials</div><div class="tags">${(result.detected_materials || []).map((m: string) => `<span class="tag gray">${m}</span>`).join('')}</div></div>
<div class="meta">Model: ${result.ai_model} · Prompt: ${result.prompt_version}<br/>Latency: ${result.latency_ms}ms · Tokens: ${result.input_tokens} in / ${result.output_tokens} out</div>
</div>
<script>window.onload=()=>{window.print()}</script>
</body></html>`;
  w.document.write(html);
  w.document.close();
}

export default function CategorizePage() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await api.categorize({
        name,
        description,
        price: price ? parseFloat(price) : undefined,
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Categorization failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-fg tracking-tight">AI Product Categorizer</h1>
        <p className="text-fg-secondary text-sm mt-1">Module 1 — Auto-assign categories, SEO tags, and sustainability filters</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="card">
          <h2 className="font-medium text-fg text-sm mb-4 flex items-center gap-2">
            <Layers size={14} className="text-fg-secondary" />
            Product Input
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-1.5">Product Name</label>
              <input
                type="text"
                className="input"
                placeholder="e.g., Bamboo Cutlery Travel Set"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-1.5">Description</label>
              <textarea
                className="input min-h-[120px]"
                placeholder="Describe the product in detail — materials, use case, sustainability features..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-1.5">Price (INR, optional)</label>
              <input
                type="number"
                className="input"
                placeholder="e.g., 349"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
            </div>
            <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner w-4 h-4" />
                  Categorizing...
                </>
              ) : (
                <>
                  <Sparkles size={15} />
                  Categorize Product
                </>
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-3 rounded-lg text-sm badge-red border">
              {error}
            </div>
          )}

          {/* Quick Examples */}
          <div className="mt-6 pt-4 border-t border-surface-300">
            <p className="text-xs text-fg-muted mb-2">Quick test examples:</p>
            <div className="flex flex-wrap gap-2">
              {[
                { n: 'Bamboo Cutlery Set', d: 'Reusable bamboo utensils — fork, knife, spoon, chopsticks. Organic cotton pouch. Plastic-free alternative to single-use cutlery.' },
                { n: 'Organic Cotton Tote', d: 'GOTS certified organic cotton bag. Block-printed by local artisans. Natural dyes. Replaces 500+ plastic bags.' },
                { n: 'Seed Paper Notebook', d: 'A5 notebook with plantable seed paper covers. 80 pages recycled paper. Soy-based ink. Plant it when done!' },
              ].map((ex) => (
                <button
                  key={ex.n}
                  className="chip"
                  onClick={() => { setName(ex.n); setDescription(ex.d); }}
                >
                  {ex.n}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-medium text-fg text-sm flex items-center gap-2">
              <FlaskConical size={14} className="text-fg-secondary" />
              AI Results
            </h2>
            {result && (
              <button
                onClick={() => generateCategorizePDF(result)}
                className="chip flex items-center gap-1.5"
              >
                <Download size={12} />
                Export PDF
              </button>
            )}
          </div>
          {!result && !loading && (
            <div className="flex items-center justify-center py-16 text-fg-muted text-sm">
              Submit a product to see AI categorization results
            </div>
          )}
          {loading && (
            <div className="flex items-center justify-center py-16">
              <div className="text-center">
                <div className="spinner w-8 h-8 mx-auto mb-3" />
                <p className="text-fg-secondary text-sm">AI is analyzing the product...</p>
              </div>
            </div>
          )}
          {result && <ResultDisplay result={result} />}
        </div>
      </div>
    </div>
  );
}

function ResultDisplay({ result }: { result: any }) {
  return (
    <div className="space-y-5">
      {/* Category */}
      <div>
        <div className="text-[10px] text-fg-muted uppercase tracking-widest mb-1">Primary Category</div>
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold text-fg">{result.primary_category}</span>
          <span className="badge-green">
            {(result.primary_category_confidence * 100).toFixed(0)}%
          </span>
          {result.needs_human_review && <span className="badge-amber">Needs Review</span>}
        </div>
      </div>

      {/* Sub-category */}
      <div>
        <div className="text-[10px] text-fg-muted uppercase tracking-widest mb-1">Sub-category</div>
        <div className="font-medium text-fg">{result.sub_category}</div>
        <div className="text-xs text-fg-muted mt-1 italic">{result.sub_category_reasoning}</div>
      </div>

      {/* Sustainability Score */}
      <div>
        <div className="text-[10px] text-fg-muted uppercase tracking-widest mb-1">Sustainability Score</div>
        <div className="flex items-center gap-3">
          <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: 'var(--progress-track)' }}>
            <div
              className="h-full bg-success rounded-full transition-all duration-500"
              style={{ width: `${(result.sustainability_score / 10) * 100}%` }}
            />
          </div>
          <span className="font-semibold text-success font-mono text-sm">{result.sustainability_score}/10</span>
        </div>
      </div>

      {/* SEO Tags */}
      <div>
        <div className="text-[10px] text-fg-muted uppercase tracking-widest mb-2 flex items-center gap-1.5">
          <Tag size={10} /> SEO Tags
        </div>
        <div className="flex flex-wrap gap-1.5">
          {result.seo_tags?.map((tag: string) => (
            <span key={tag} className="badge-blue">{tag}</span>
          ))}
        </div>
      </div>

      {/* Sustainability Filters */}
      <div>
        <div className="text-[10px] text-fg-muted uppercase tracking-widest mb-2 flex items-center gap-1.5">
          <Leaf size={10} /> Sustainability Filters
        </div>
        <div className="flex flex-wrap gap-1.5">
          {result.sustainability_filters?.map((f: string) => (
            <span key={f} className="badge-green">{f}</span>
          ))}
        </div>
      </div>

      {/* Materials */}
      <div>
        <div className="text-[10px] text-fg-muted uppercase tracking-widest mb-2">Detected Materials</div>
        <div className="flex flex-wrap gap-1.5">
          {result.detected_materials?.map((m: string) => (
            <span key={m} className="chip text-[11px] cursor-default">{m}</span>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="pt-3 border-t border-surface-300 text-xs text-fg-muted space-y-1 font-mono">
        <div>Model: {result.ai_model} · Prompt: {result.prompt_version}</div>
        <div>Latency: {result.latency_ms}ms · Tokens: {result.input_tokens} in / {result.output_tokens} out</div>
        <div>Product ID: {result.product_id}</div>
      </div>
    </div>
  );
}
