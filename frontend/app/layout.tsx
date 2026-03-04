import type { Metadata } from 'next';
import './globals.css';
import { ThemeToggle } from './theme-toggle';

export const metadata: Metadata = {
  title: 'Rayeva AI — Sustainable Commerce',
  description: 'AI-powered modules for sustainable commerce: Auto-categorization, B2B proposals, impact reporting.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // Inline script to prevent FOUC — reads preference before paint
  const themeScript = `
    (function() {
      try {
        var t = localStorage.getItem('theme');
        if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          document.documentElement.classList.add('dark');
        }
      } catch(e) {}
    })();
  `;

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <div className="min-h-screen bg-surface transition-colors duration-200">
          <nav className="bg-surface-50 border-b border-surface-300 px-6 py-3.5 transition-colors duration-200">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <a href="/" className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded bg-fg flex items-center justify-center">
                  <span className="text-surface font-bold text-sm">R</span>
                </div>
                <span className="font-semibold text-[15px] text-fg tracking-tight">RAYEVA AI</span>
              </a>
              <div className="flex items-center gap-1">
                <a href="/" className="px-3 py-1.5 rounded-md text-fg-secondary hover:text-fg hover:bg-surface-300 transition-all text-[13px] font-medium">Dashboard</a>
                <a href="/categorize" className="px-3 py-1.5 rounded-md text-fg-secondary hover:text-fg hover:bg-surface-300 transition-all text-[13px] font-medium">Categorize</a>
                <a href="/proposals" className="px-3 py-1.5 rounded-md text-fg-secondary hover:text-fg hover:bg-surface-300 transition-all text-[13px] font-medium">Proposals</a>
                <a href="/logs" className="px-3 py-1.5 rounded-md text-fg-secondary hover:text-fg hover:bg-surface-300 transition-all text-[13px] font-medium">AI Logs</a>
                <div className="ml-3 pl-3 border-l border-surface-300">
                  <ThemeToggle />
                </div>
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
