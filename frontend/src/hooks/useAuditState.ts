'use client';

import { useState, useCallback, useEffect, useReducer } from 'react';
import type { 
  AuditResult, 
  AuditSession, 
  AuditStatus, 
  ContractMetadata,
  AuditConfig 
} from '@/types/audit';

// State interface
interface AuditState {
  // Current audit session
  currentSession: AuditSession | null;
  
  // Audit history
  auditHistory: AuditResult[];
  
  // UI state
  isLoading: boolean;
  error: string | null;
  
  // Configuration
  config: AuditConfig;
  
  // Statistics
  stats: {
    totalAudits: number;
    passedAudits: number;
    failedAudits: number;
    averageScore: number;
  };
}

// Action types
type AuditAction =
  | { type: 'START_AUDIT'; payload: { contractCode: string; metadata: ContractMetadata } }
  | { type: 'UPDATE_PROGRESS'; payload: { progress: number; step?: string } }
  | { type: 'AUDIT_SUCCESS'; payload: AuditResult }
  | { type: 'AUDIT_ERROR'; payload: string }
  | { type: 'CLEAR_ERROR' }
  | { type: 'UPDATE_CONFIG'; payload: Partial<AuditConfig> }
  | { type: 'LOAD_HISTORY'; payload: AuditResult[] }
  | { type: 'CLEAR_HISTORY' };

// Initial state
const initialState: AuditState = {
  currentSession: null,
  auditHistory: [],
  isLoading: false,
  error: null,
  config: {
    includeGasAnalysis: true,
    includeOptimizations: true,
    severityThreshold: 'low',
  },
  stats: {
    totalAudits: 0,
    passedAudits: 0,
    failedAudits: 0,
    averageScore: 0,
  },
};

// Reducer function
function auditReducer(state: AuditState, action: AuditAction): AuditState {
  switch (action.type) {
    case 'START_AUDIT':
      return {
        ...state,
        currentSession: {
          id: `audit_${Date.now()}`,
          status: 'running',
          startTime: new Date().toISOString(),
          progress: 0,
          currentStep: 'Initializing audit...',
        },
        isLoading: true,
        error: null,
      };

    case 'UPDATE_PROGRESS':
      return {
        ...state,
        currentSession: state.currentSession
          ? {
              ...state.currentSession,
              progress: action.payload.progress,
              currentStep: action.payload.step || state.currentSession.currentStep,
            }
          : null,
      };

    case 'AUDIT_SUCCESS':
      const newHistory = [action.payload, ...state.auditHistory.slice(0, 9)]; // Keep last 10
      const newStats = calculateStats(newHistory);
      
      return {
        ...state,
        currentSession: state.currentSession
          ? {
              ...state.currentSession,
              status: 'completed',
              endTime: new Date().toISOString(),
              progress: 100,
              result: action.payload,
            }
          : null,
        auditHistory: newHistory,
        isLoading: false,
        error: null,
        stats: newStats,
      };

    case 'AUDIT_ERROR':
      return {
        ...state,
        currentSession: state.currentSession
          ? {
              ...state.currentSession,
              status: 'failed',
              endTime: new Date().toISOString(),
              error: {
                code: 'AUDIT_FAILED',
                message: action.payload,
                timestamp: new Date().toISOString(),
              },
            }
          : null,
        isLoading: false,
        error: action.payload,
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    case 'UPDATE_CONFIG':
      return {
        ...state,
        config: {
          ...state.config,
          ...action.payload,
        },
      };

    case 'LOAD_HISTORY':
      return {
        ...state,
        auditHistory: action.payload,
        stats: calculateStats(action.payload),
      };

    case 'CLEAR_HISTORY':
      return {
        ...state,
        auditHistory: [],
        stats: initialState.stats,
      };

    default:
      return state;
  }
}

// Helper function to calculate statistics
function calculateStats(history: AuditResult[]) {
  const totalAudits = history.length;
  const passedAudits = history.filter(audit => audit.passed).length;
  const failedAudits = totalAudits - passedAudits;
  const averageScore = totalAudits > 0 
    ? history.reduce((sum, audit) => sum + audit.audit_score, 0) / totalAudits 
    : 0;

  return {
    totalAudits,
    passedAudits,
    failedAudits,
    averageScore: Math.round(averageScore * 100) / 100,
  };
}

// Custom hook
export function useAuditState() {
  const [state, dispatch] = useReducer(auditReducer, initialState);

  // Load audit history from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedHistory = localStorage.getItem('audit_history');
      if (savedHistory) {
        try {
          const history = JSON.parse(savedHistory);
          dispatch({ type: 'LOAD_HISTORY', payload: history });
        } catch (error) {
          console.error('Failed to load audit history:', error);
        }
      }
    }
  }, []);

  // Save audit history to localStorage when it changes
  useEffect(() => {
    if (typeof window !== 'undefined' && state.auditHistory.length > 0) {
      localStorage.setItem('audit_history', JSON.stringify(state.auditHistory));
    }
  }, [state.auditHistory]);

  // Action creators
  const startAudit = useCallback((contractCode: string, metadata: ContractMetadata) => {
    dispatch({ type: 'START_AUDIT', payload: { contractCode, metadata } });
  }, []);

  const updateProgress = useCallback((progress: number, step?: string) => {
    dispatch({ type: 'UPDATE_PROGRESS', payload: { progress, step } });
  }, []);

  const auditSuccess = useCallback((result: AuditResult) => {
    dispatch({ type: 'AUDIT_SUCCESS', payload: result });
  }, []);

  const auditError = useCallback((error: string) => {
    dispatch({ type: 'AUDIT_ERROR', payload: error });
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  const updateConfig = useCallback((config: Partial<AuditConfig>) => {
    dispatch({ type: 'UPDATE_CONFIG', payload: config });
  }, []);

  const clearHistory = useCallback(() => {
    dispatch({ type: 'CLEAR_HISTORY' });
    if (typeof window !== 'undefined') {
      localStorage.removeItem('audit_history');
    }
  }, []);

  // Computed values
  const currentAudit = state.currentSession?.result;
  const isAuditing = state.currentSession?.status === 'running';
  const hasError = !!state.error;
  const hasHistory = state.auditHistory.length > 0;

  return {
    // State
    ...state,
    
    // Computed values
    currentAudit,
    isAuditing,
    hasError,
    hasHistory,
    
    // Actions
    startAudit,
    updateProgress,
    auditSuccess,
    auditError,
    clearError,
    updateConfig,
    clearHistory,
  };
}
