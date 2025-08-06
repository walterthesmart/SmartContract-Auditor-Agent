'use client';

import { useState, useEffect } from 'react';
import { Shield, RefreshCw, Download, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { VulnerabilityList } from './VulnerabilityList';
import { getAuditStatus } from '@/lib/utils';
import type { AuditResult } from '@/types/audit';

export function AuditDashboard(): JSX.Element {
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const handleAuditComplete = (event: CustomEvent) => {
      setAuditResult(event.detail);
    };

    window.addEventListener('auditComplete', handleAuditComplete as EventListener);
    return () => {
      window.removeEventListener('auditComplete', handleAuditComplete as EventListener);
    };
  }, []);

  const handleRefresh = async (): Promise<void> => {
    setIsRefreshing(true);
    // Simulate refresh delay
    setTimeout(() => {
      setIsRefreshing(false);
    }, 1000);
  };

  const handleExport = (): void => {
    if (!auditResult) return;

    const exportData = {
      timestamp: new Date().toISOString(),
      contract: auditResult.contract_metadata,
      score: auditResult.audit_score,
      vulnerabilities: auditResult.vulnerabilities,
      summary: auditResult.summary,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-results-${auditResult.contract_metadata.name}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const actions = (
    <div className="flex items-center space-x-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={handleRefresh}
        loading={isRefreshing}
      >
        <RefreshCw className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleExport}
        disabled={!auditResult}
      >
        <Download className="h-4 w-4" />
      </Button>
    </div>
  );

  const auditStatus = auditResult ? getAuditStatus(auditResult.audit_score) : null;

  return (
    <Card
      title="Audit Dashboard"
      icon={<Shield className="h-5 w-5" />}
      actions={actions}
    >
      {/* Audit Summary */}
      <div className="mb-6 rounded-lg bg-dark-900/50 p-4">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-primary-400">
              {auditResult?.audit_score ?? '--'}
            </div>
            <div className="text-xs uppercase tracking-wide text-dark-400">
              Score
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-400">
              {auditResult?.vulnerabilities.length ?? '--'}
            </div>
            <div className="text-xs uppercase tracking-wide text-dark-400">
              Issues
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-secondary-400">
              {auditStatus?.label ?? 'Ready'}
            </div>
            <div className="text-xs uppercase tracking-wide text-dark-400">
              Status
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {auditResult && (
          <div className="mt-4">
            <ProgressBar
              value={auditResult.audit_score}
              max={100}
              label="Security Score"
              className="mb-2"
            />
          </div>
        )}

        {/* Status Indicator */}
        <div className="mt-4 flex items-center justify-center">
          {auditResult ? (
            <div className={`flex items-center space-x-2 ${auditStatus?.color}`}>
              {auditStatus?.status === 'passed' && <CheckCircle className="h-5 w-5" />}
              {auditStatus?.status === 'warning' && <AlertTriangle className="h-5 w-5" />}
              {auditStatus?.status === 'failed' && <AlertTriangle className="h-5 w-5" />}
              <span className="font-medium">{auditStatus?.label}</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-dark-400">
              <Clock className="h-5 w-5" />
              <span>Ready to audit</span>
            </div>
          )}
        </div>
      </div>

      {/* Vulnerability Summary */}
      {auditResult && auditResult.vulnerabilities.length > 0 && (
        <div className="mb-4">
          <h4 className="mb-2 text-sm font-medium text-dark-300">Issue Breakdown</h4>
          <div className="flex flex-wrap gap-2">
            {auditResult.summary.critical_count > 0 && (
              <Badge variant="critical">
                {auditResult.summary.critical_count} Critical
              </Badge>
            )}
            {auditResult.summary.high_count > 0 && (
              <Badge variant="high">
                {auditResult.summary.high_count} High
              </Badge>
            )}
            {auditResult.summary.medium_count > 0 && (
              <Badge variant="medium">
                {auditResult.summary.medium_count} Medium
              </Badge>
            )}
            {auditResult.summary.low_count > 0 && (
              <Badge variant="low">
                {auditResult.summary.low_count} Low
              </Badge>
            )}
            {auditResult.summary.info_count > 0 && (
              <Badge variant="info">
                {auditResult.summary.info_count} Info
              </Badge>
            )}
          </div>
        </div>
      )}

      {/* Vulnerability List */}
      <VulnerabilityList vulnerabilities={auditResult?.vulnerabilities || []} />
    </Card>
  );
}
