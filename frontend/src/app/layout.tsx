import type { Metadata } from 'next';
import { Inter, Fira_Code } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

const firaCode = Fira_Code({ 
  subsets: ['latin'],
  variable: '--font-fira-code',
});

export const metadata: Metadata = {
  title: 'HederaAuditAI - Smart Contract Security Auditor',
  description: 'AI-powered smart contract auditing tool for Hedera blockchain with HCS-10 OpenConvAI support',
  keywords: ['smart contract', 'audit', 'security', 'Hedera', 'blockchain', 'AI', 'vulnerability detection'],
  authors: [{ name: 'HederaAuditAI' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#14b8a6',
  openGraph: {
    title: 'HederaAuditAI - Smart Contract Security Auditor',
    description: 'AI-powered smart contract auditing tool for Hedera blockchain',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'HederaAuditAI - Smart Contract Security Auditor',
    description: 'AI-powered smart contract auditing tool for Hedera blockchain',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${firaCode.variable}`}>
      <body className="min-h-screen bg-hero-pattern font-sans text-white antialiased">
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1e293b',
              color: '#f1f5f9',
              border: '1px solid #334155',
            },
            success: {
              iconTheme: {
                primary: '#14b8a6',
                secondary: '#f1f5f9',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#f1f5f9',
              },
            },
          }}
        />
      </body>
    </html>
  );
}
