'use client';

import { BookOpen, Play, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

const tutorialSteps = [
  {
    title: 'Upload Your Contract',
    description: 'Drag and drop your Solidity or Vyper contract file into the editor.',
    icon: '📁',
  },
  {
    title: 'Run Security Audit',
    description: 'Click "Run Audit" to analyze your contract for vulnerabilities.',
    icon: '🔍',
  },
  {
    title: 'Review Results',
    description: 'Examine the security findings and recommendations in the dashboard.',
    icon: '📊',
  },
  {
    title: 'Generate Report',
    description: 'Create a professional PDF audit report for your records.',
    icon: '📄',
  },
  {
    title: 'Mint NFT Certificate',
    description: 'Get an NFT certificate for contracts that pass the audit.',
    icon: '🏆',
  },
];

const resources = [
  {
    title: 'Smart Contract Security Best Practices',
    url: 'https://consensys.github.io/smart-contract-best-practices/',
    description: 'Comprehensive guide to secure smart contract development',
  },
  {
    title: 'Hedera Developer Documentation',
    url: 'https://docs.hedera.com/',
    description: 'Official documentation for building on Hedera',
  },
  {
    title: 'HCS-10 OpenConvAI Standard',
    url: 'https://hashgraphonline.com/docs/standards/hcs-10',
    description: 'Learn about decentralized AI agent communication',
  },
];

export function TutorialSection(): JSX.Element {
  const openResource = (url: string): void => {
    window.open(url, '_blank');
  };

  const startTutorial = (): void => {
    if (typeof window !== 'undefined' && (window as any).showAlert) {
      (window as any).showAlert({
        type: 'info',
        title: 'Tutorial Started',
        message: 'Follow the steps below to audit your first smart contract!',
      });
    }
  };

  return (
    <Card
      title="Tutorial & Resources"
      icon={<BookOpen className="h-5 w-5" />}
    >
      <div className="space-y-4">
        {/* Quick Start Button */}
        <Button
          variant="primary"
          size="sm"
          onClick={startTutorial}
          className="w-full"
        >
          <Play className="h-4 w-4" />
          Start Interactive Tutorial
        </Button>

        {/* Tutorial Steps */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-dark-300">Quick Start Guide</h4>
          <div className="space-y-2">
            {tutorialSteps.map((step, index) => (
              <div
                key={index}
                className="flex items-start space-x-3 rounded-lg bg-dark-900/30 p-3"
              >
                <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-primary-600/20 text-xs">
                  {step.icon}
                </div>
                <div className="flex-1">
                  <h5 className="text-sm font-medium text-white">{step.title}</h5>
                  <p className="text-xs text-dark-400">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Resources */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-dark-300">Learning Resources</h4>
          <div className="space-y-2">
            {resources.map((resource, index) => (
              <button
                key={index}
                onClick={() => openResource(resource.url)}
                className="w-full rounded-lg bg-dark-900/30 p-3 text-left transition-colors hover:bg-dark-800/50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h5 className="text-sm font-medium text-white">{resource.title}</h5>
                    <p className="text-xs text-dark-400">{resource.description}</p>
                  </div>
                  <ExternalLink className="h-4 w-4 flex-shrink-0 text-dark-500" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Tips */}
        <div className="rounded-lg bg-primary-900/20 p-3">
          <h4 className="mb-2 text-sm font-medium text-primary-300">💡 Pro Tips</h4>
          <ul className="space-y-1 text-xs text-primary-200/80">
            <li>• Test with small contracts first to understand the audit process</li>
            <li>• Review all vulnerability explanations and recommendations</li>
            <li>• Use the generated reports for compliance and documentation</li>
            <li>• NFT certificates provide verifiable proof of security audits</li>
          </ul>
        </div>
      </div>
    </Card>
  );
}
