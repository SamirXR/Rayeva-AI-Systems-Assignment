'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

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
        <h1 className="text-3xl font-bold text-gray-900">AI Product Categorizer</h1>
        <p className="text-gray-500 mt-1">Module 1 — Auto-assign categories, SEO tags, and sustainability filters</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="card">
          <h2 className="font-semibold text-gray-700 mb-4">Product Input</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                className="input min-h-[120px]"
                placeholder="Describe the product in detail — materials, use case, sustainability features..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Price (₹, optional)</label>
              <input
                type="number"
                className="input"
                placeholder="e.g., 349"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  Categorizing with AI...
                </span>
              ) : (
                '🤖 Categorize Product'
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Quick Examples */}
          <div className="mt-6 pt-4 border-t">
            <p className="text-xs text-gray-500 mb-2">Quick test examples:</p>
            <div className="flex flex-wrap gap-2">
              {[
                { n: 'Bamboo Cutlery Set', d: 'Reusable bamboo utensils — fork, knife, spoon, chopsticks. Organic cotton pouch. Plastic-free alternative to single-use cutlery.' },
                { n: 'Organic Cotton Tote', d: 'GOTS certified organic cotton bag. Block-printed by local artisans. Natural dyes. Replaces 500+ plastic bags.' },
                { n: 'Seed Paper Notebook', d: 'A5 notebook with plantable seed paper covers. 80 pages recycled paper. Soy-based ink. Plant it when done!' },
              ].map((ex) => (
                <button
                  key={ex.n}
                  className="text-xs bg-brand-50 text-brand-700 px-3 py-1 rounded-full hover:bg-brand-100 transition-colors"
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
          <h2 className="font-semibold text-gray-700 mb-4">AI Results</h2>
          {!result && !loading && (
            <div className="flex items-center justify-center py-16 text-gray-400">
              <p>Submit a product to see AI categorization results</p>
            </div>
          )}
          {loading && (
            <div className="flex items-center justify-center py-16">
              <div className="text-center">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-600 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">AI is analyzing the product...</p>
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
        <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Primary Category</div>
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold text-gray-900">{result.primary_category}</span>
          <span className="badge-green">
            {(result.primary_category_confidence * 100).toFixed(0)}% confidence
          </span>
          {result.needs_human_review && <span className="badge-amber">Needs Review</span>}
        </div>
      </div>

      {/* Sub-category */}
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Sub-category</div>
        <div className="font-medium text-gray-800">{result.sub_category}</div>
        <div className="text-xs text-gray-500 mt-1 italic">{result.sub_category_reasoning}</div>
      </div>

      {/* Sustainability Score */}
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Sustainability Score</div>
        <div className="flex items-center gap-3">
          <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-brand-500 to-brand-600 rounded-full transition-all duration-500"
              style={{ width: `${(result.sustainability_score / 10) * 100}%` }}
            />
          </div>
          <span className="font-bold text-brand-700">{result.sustainability_score}/10</span>
        </div>
      </div>

      {/* SEO Tags */}
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">SEO Tags</div>
        <div className="flex flex-wrap gap-1.5">
          {result.seo_tags?.map((tag: string) => (
            <span key={tag} className="badge-blue">{tag}</span>
          ))}
        </div>
      </div>

      {/* Sustainability Filters */}
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Sustainability Filters</div>
        <div className="flex flex-wrap gap-1.5">
          {result.sustainability_filters?.map((f: string) => (
            <span key={f} className="badge-green">{f}</span>
          ))}
        </div>
      </div>

      {/* Materials */}
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Detected Materials</div>
        <div className="flex flex-wrap gap-1.5">
          {result.detected_materials?.map((m: string) => (
            <span key={m} className="bg-gray-100 text-gray-700 px-2.5 py-0.5 rounded-full text-xs">{m}</span>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="pt-3 border-t text-xs text-gray-400 space-y-1">
        <div>Model: {result.ai_model} · Prompt: {result.prompt_version}</div>
        <div>Latency: {result.latency_ms}ms · Tokens: {result.input_tokens} in / {result.output_tokens} out</div>
        <div>Product ID: {result.product_id} (saved to database)</div>
      </div>
    </div>
  );
}
