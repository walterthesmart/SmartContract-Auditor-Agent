'use client';

import { useState } from 'react';
import { Navbar } from '@/components/layout/Navbar';
import { CodeEditor } from '@/components/editor/CodeEditor';
import { AuditDashboard } from '@/components/audit/AuditDashboard';
import { ReportPreview } from '@/components/report/ReportPreview';
import { NFTCertificate } from '@/components/nft/NFTCertificate';
import { TutorialSection } from '@/components/tutorial/TutorialSection';
import { AlertContainer } from '@/components/ui/AlertContainer';

export default function HomePage() {
  const [activeSection, setActiveSection] = useState('dashboard');

  return (
    <div className="min-h-screen">
      <Navbar activeSection={activeSection} onSectionChange={setActiveSection} />
      <AlertContainer />
      
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            <CodeEditor />
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            <AuditDashboard />
            <ReportPreview />
            <NFTCertificate />
            <TutorialSection />
          </div>
        </div>
      </main>
    </div>
  );
}
