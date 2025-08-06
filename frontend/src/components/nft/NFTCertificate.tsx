'use client';

import { useState, useEffect } from 'react';
import { Award, ExternalLink, Copy, Check } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { truncateAddress, formatDate } from '@/lib/utils';
import type { AuditResult } from '@/types/audit';

export function NFTCertificate(): JSX.Element {
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [nftId, setNftId] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const handleAuditComplete = (event: CustomEvent) => {
      const result = event.detail as AuditResult;
      setAuditResult(result);
      
      // Simulate NFT minting for passed audits
      if (result.passed) {
        // Generate a mock NFT ID
        const mockNftId = `0.0.${Math.floor(Math.random() * 999999) + 100000}`;
        setNftId(mockNftId);
      } else {
        setNftId(null);
      }
    };

    window.addEventListener('auditComplete', handleAuditComplete as EventListener);
    return () => {
      window.removeEventListener('auditComplete', handleAuditComplete as EventListener);
    };
  }, []);

  const copyToClipboard = async (text: string): Promise<void> => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const viewOnHashscan = (): void => {
    if (nftId) {
      const network = process.env.NEXT_PUBLIC_HEDERA_NETWORK || 'testnet';
      window.open(`https://hashscan.io/${network}/token/${nftId}`, '_blank');
    }
  };

  const hasNFT = auditResult?.passed && nftId;

  return (
    <Card
      title="NFT Audit Certificate"
      icon={<Award className="h-5 w-5" />}
    >
      <div className="space-y-4">
        {/* NFT Certificate Display */}
        <div className="relative overflow-hidden rounded-lg">
          {hasNFT ? (
            <div className="bg-gradient-to-br from-primary-500 to-secondary-500 p-6 text-center text-white">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
              <Award className="mx-auto mb-2 h-12 w-12" />
              <h4 className="text-lg font-bold">Security Audit Certificate</h4>
              <p className="text-sm opacity-90">#{nftId}</p>
              <div className="mt-2">
                <Badge variant="low" className="bg-white/20 text-white">
                  VERIFIED
                </Badge>
              </div>
            </div>
          ) : (
            <div className="flex h-32 items-center justify-center rounded-lg border-2 border-dashed border-dark-600 bg-dark-900/30">
              <div className="text-center text-dark-500">
                <Award className="mx-auto mb-2 h-8 w-8" />
                <p className="text-sm">No certificate available</p>
                <p className="text-xs">Pass audit to mint NFT</p>
              </div>
            </div>
          )}
        </div>

        {/* Certificate Details */}
        {hasNFT && auditResult && (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-dark-400">Contract:</span>
              <span className="font-mono text-white">
                {truncateAddress(auditResult.contract_metadata.name, 8, 4)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Score:</span>
              <span className="font-semibold text-primary-400">
                {auditResult.audit_score}/100
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Issued:</span>
              <span className="text-white">
                {formatDate(auditResult.timestamp)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-dark-400">NFT ID:</span>
              <div className="flex items-center space-x-1">
                <span className="font-mono text-white">{truncateAddress(nftId, 6, 4)}</span>
                <button
                  onClick={() => copyToClipboard(nftId)}
                  className="text-dark-400 hover:text-white"
                >
                  {copied ? (
                    <Check className="h-3 w-3 text-green-400" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-2">
          {hasNFT ? (
            <>
              <Button
                variant="primary"
                size="sm"
                onClick={viewOnHashscan}
                className="flex-1"
              >
                <ExternalLink className="h-4 w-4" />
                View on Hashscan
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(nftId)}
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-400" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </>
          ) : (
            <Button
              variant="outline"
              size="sm"
              disabled
              className="flex-1"
            >
              <Award className="h-4 w-4" />
              Certificate Unavailable
            </Button>
          )}
        </div>

        {/* Certificate Requirements */}
        {!hasNFT && (
          <div className="rounded-lg bg-dark-900/50 p-3">
            <h5 className="mb-2 text-sm font-medium text-dark-300">
              Certificate Requirements
            </h5>
            <ul className="space-y-1 text-xs text-dark-400">
              <li className="flex items-center space-x-2">
                <div className={`h-2 w-2 rounded-full ${auditResult ? 'bg-green-400' : 'bg-dark-600'}`} />
                <span>Complete security audit</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className={`h-2 w-2 rounded-full ${auditResult?.passed ? 'bg-green-400' : 'bg-dark-600'}`} />
                <span>Pass audit with score ≥ 80</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className={`h-2 w-2 rounded-full ${hasNFT ? 'bg-green-400' : 'bg-dark-600'}`} />
                <span>Mint NFT certificate</span>
              </li>
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
}
