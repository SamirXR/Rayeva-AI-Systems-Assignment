const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

// Default 3 minutes — AI reasoning models can take 60-90s per step
const DEFAULT_TIMEOUT_MS = 180_000;

export async function apiFetch<T>(path: string, options?: RequestInit & { timeoutMs?: number }): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, ...fetchOptions } = options || {};
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...fetchOptions?.headers },
      signal: controller.signal,
      ...fetchOptions,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || 'API request failed');
    }
    return res.json();
  } catch (err: any) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out — the AI model is taking longer than expected. Please try again.');
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  // Module 1
  categorize: (data: { name: string; description: string; price?: number }) =>
    apiFetch<any>('/api/v1/categorize', { method: 'POST', body: JSON.stringify(data) }),

  batchCategorize: (products: { name: string; description: string }[]) =>
    apiFetch<any>('/api/v1/categorize/batch', { method: 'POST', body: JSON.stringify({ products }) }),

  getCategories: () => apiFetch<any>('/api/v1/categories'),

  getProducts: (params?: string) => apiFetch<any>(`/api/v1/products${params ? `?${params}` : ''}`),

  getProduct: (id: number) => apiFetch<any>(`/api/v1/products/${id}`),

  // Module 2
  generateProposal: (data: any) =>
    apiFetch<any>('/api/v1/proposals/generate', { method: 'POST', body: JSON.stringify(data) }),

  getProposal: (id: number) => apiFetch<any>(`/api/v1/proposals/${id}`),

  getProposals: () => apiFetch<any>('/api/v1/proposals'),

  // Logs & Metrics
  getLogs: (params?: string) => apiFetch<any>(`/api/v1/logs${params ? `?${params}` : ''}`),

  getMetrics: () => apiFetch<any>('/api/v1/metrics'),
};
