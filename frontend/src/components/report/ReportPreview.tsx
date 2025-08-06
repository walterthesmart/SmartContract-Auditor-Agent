'use client';

import { useState, useEffect } from 'react';
import { FileText, Download, Eye, Loader2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { auditService } from '@/services/api';
import type { AuditResult } from '@/types/audit';

export function ReportPreview() {
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportUrl, setReportUrl] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const handleAuditComplete = (event: CustomEvent) => {
      setAuditResult(event.detail);
      setReportUrl(null); // Reset report URL when new audit completes
    };

    window.addEventListener('auditComplete', handleAuditComplete as EventListener);
    return () => {
      window.removeEventListener('auditComplete', handleAuditComplete as EventListener);
    };
  }, []);

  const generateReport = async () => {
    if (!auditResult) return;

    setIsGenerating(true);
    setProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await auditService.generateReport({
        audit_data: auditResult,
        include_recommendations: true,
        format: 'pdf',
      });

      clearInterval(progressInterval);
      setProgress(100);
      setReportUrl(response.view_url);

      if (typeof window !== 'undefined' && (window as any).showAlert) {
        (window as any).showAlert({
          type: 'success',
          title: 'Report Generated',
          message: 'PDF audit report has been generated successfully.',
        });
      }

    } catch (error) {
      console.error('Report generation failed:', error);
      setProgress(0);
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadReport = () => {
    if (reportUrl) {
      window.open(reportUrl, '_blank');
    }
  };

  const previewReport = () => {
    if (reportUrl) {
      window.open(reportUrl, '_blank');
    }
  };

  return (
    <Card
      title="Audit Report"
      icon={<FileText className="h-5 w-5" />}
    >
      <div className="space-y-4">
        {/* Report Preview Area */}
        <div className="flex h-32 items-center justify-center rounded-lg border-2 border-dashed border-dark-600 bg-dark-900/30">
          {isGenerating ? (
            <div className="text-center">
              <Loader2 className="mx-auto mb-2 h-8 w-8 animate-spin text-primary-400" />
              <p className="text-sm text-dark-300">Generating report...</p>
            </div>
          ) : reportUrl ? (
            <div className="text-center">
              <FileText className="mx-auto mb-2 h-8 w-8 text-primary-400" />
              <p className="text-sm text-dark-300">PDF Report Ready</p>
            </div>
          ) : (
            <div className="text-center">
              <FileText className="mx-auto mb-2 h-8 w-8 text-dark-500" />
              <p className="text-sm text-dark-500">No report generated</p>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {isGenerating && (
          <ProgressBar
            value={progress}
            label="Generating PDF report"
            showPercentage
          />
        )}

        {/* Report Actions */}
        <div className="flex space-x-2">
          <Button
            variant="primary"
            size="sm"
            onClick={generateReport}
            disabled={!auditResult || isGenerating}
            loading={isGenerating}
            className="flex-1"
          >
            <FileText className="h-4 w-4" />
            Generate Report
          </Button>
          
          {reportUrl && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={previewReport}
              >
                <Eye className="h-4 w-4" />
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={downloadReport}
              >
                <Download className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>

        {/* Report Info */}
        {auditResult && (
          <div className="space-y-2 text-xs text-dark-400">
            <div className="flex justify-between">
              <span>Contract:</span>
              <span className="font-mono">{auditResult.contract_metadata.name}</span>
            </div>
            <div className="flex justify-between">
              <span>Language:</span>
              <span className="capitalize">{auditResult.contract_metadata.language}</span>
            </div>
            <div className="flex justify-between">
              <span>Issues Found:</span>
              <span>{auditResult.vulnerabilities.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Audit Score:</span>
              <span className="font-semibold">{auditResult.audit_score}/100</span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
