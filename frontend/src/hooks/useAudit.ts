'use client';

import { useState, useCallback } from 'react';
import { auditService } from '@/services/api';
import type { AuditRequest, AuditResult } from '@/types/audit';

interface UseAuditReturn {
  auditResult: AuditResult | null;
  isLoading: boolean;
  error: string | null;
  runAudit: (request: AuditRequest) => Promise<void>;
  clearResult: () => void;
}

export function useAudit(): UseAuditReturn {
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAudit = useCallback(async (request: AuditRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // Show loading message
      if (typeof window !== 'undefined' && (window as unknown as { showAlert?: (alert: { type: string; message: string; duration: number }) => void }).showAlert) {
        (window as unknown as { showAlert: (alert: { type: string; message: string; duration: number }) => void }).showAlert({
          type: 'info',
          message: 'Starting security audit analysis...',
          duration: 3000,
        });
      }

      const result = await auditService.analyzeContract(request);
      setAuditResult(result);

      // Show success message
      if (typeof window !== 'undefined' && (window as unknown as { showAlert?: (alert: { type: string; title: string; message: string }) => void }).showAlert) {
        (window as unknown as { showAlert: (alert: { type: string; title: string; message: string }) => void }).showAlert({
          type: 'success',
          title: 'Audit Complete',
          message: `Found ${result.vulnerabilities.length} issues. Score: ${result.audit_score}/100`,
        });
      }

      // Trigger custom event for other components to listen
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auditComplete', { 
          detail: result 
        }));
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Audit failed';
      setError(errorMessage);
      
      // Error is already handled by the API interceptor
      console.error('Audit error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearResult = useCallback(() => {
    setAuditResult(null);
    setError(null);
  }, []);

  return {
    auditResult,
    isLoading,
    error,
    runAudit,
    clearResult,
  };
}
