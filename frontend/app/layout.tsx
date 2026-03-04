import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Rayeva AI — Sustainable Commerce',
  description: 'AI-powered modules for sustainable commerce: Auto-categorization, B2B proposals, impact reporting.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <nav className="bg-white border-b border-gray-200 px-6 py-3">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <a href="/" className="flex items-center gap-2">
                <span className="text-2xl">🌿</span>
                <span className="font-bold text-lg text-brand-800">Rayeva AI</span>
              </a>
              <div className="flex gap-6 text-sm font-medium text-gray-600">
                <a href="/" className="hover:text-brand-700 transition-colors">Dashboard</a>
                <a href="/categorize" className="hover:text-brand-700 transition-colors">Categorize</a>
                <a href="/proposals" className="hover:text-brand-700 transition-colors">Proposals</a>
                <a href="/logs" className="hover:text-brand-700 transition-colors">AI Logs</a>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto px-6 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
