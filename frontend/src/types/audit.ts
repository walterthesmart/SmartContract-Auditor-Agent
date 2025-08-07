export interface ContractMetadata {
  readonly name: string;
  readonly language: 'solidity' | 'vyper';
  readonly hash?: string;
}

export interface Vulnerability {
  readonly id: string;
  readonly severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  readonly title: string;
  readonly description: string;
  readonly location: {
    readonly line: number;
    readonly column?: number;
    readonly function?: string;
  };
  readonly recommendation?: string;
  readonly references?: readonly string[];
}

export interface AuditResult {
  id: string;
  contract_metadata: ContractMetadata;
  audit_score: number;
  vulnerabilities: Vulnerability[];
  passed: boolean;
  timestamp: string;
  gas_analysis?: {
    estimated_gas: number;
    optimization_suggestions: string[];
  };
  summary: {
    total_issues: number;
    critical_count: number;
    high_count: number;
    medium_count: number;
    low_count: number;
    info_count: number;
  };
}

export interface AuditRequest {
  contract_code: string;
  contract_metadata: ContractMetadata;
}

export interface ReportData {
  audit_data: AuditResult;
  include_recommendations?: boolean;
  format?: 'pdf' | 'html';
}

export interface ReportResponse {
  file_id: string;
  nft_id?: string;
  view_url: string;
}

export interface NFTMetadata {
  contract: ContractMetadata;
  score: number;
  timestamp: string;
  file_id: string;
}

export interface HCS10Connection {
  connection_id: string;
  requester_account: string;
  status: 'active' | 'pending' | 'closed';
  created_at: string;
}

export interface MoonScapeStatus {
  status: string;
  agent_name: string;
  agent_id: string;
  active_connections: number;
  registry_topic_id: string;
  network: string;
  uptime: string;
}

// Advanced type definitions for better type safety
export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type AuditStatus = 'pending' | 'running' | 'completed' | 'failed';
export type ContractLanguage = 'solidity' | 'vyper';

// Generic API response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  timestamp: string;
  success: boolean;
}

// Paginated response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// Error response
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

// Audit session state
export interface AuditSession {
  id: string;
  status: AuditStatus;
  startTime: string;
  endTime?: string;
  progress: number;
  currentStep?: string;
  result?: AuditResult;
  error?: ApiError;
}

// Enhanced vulnerability with additional metadata
export interface EnhancedVulnerability extends Vulnerability {
  category: string;
  cweId?: string;
  impact: 'low' | 'medium' | 'high' | 'critical';
  likelihood: 'low' | 'medium' | 'high';
  remediation: {
    effort: 'low' | 'medium' | 'high';
    cost: 'low' | 'medium' | 'high';
    priority: number;
  };
  tags: string[];
  relatedVulnerabilities?: string[];
}

// Gas analysis details
export interface GasAnalysis {
  estimatedGas: number;
  gasOptimizations: GasOptimization[];
  totalSavings: number;
  efficiency: number;
}

export interface GasOptimization {
  id: string;
  type: string;
  description: string;
  location: {
    line: number;
    function?: string;
  };
  currentGas: number;
  optimizedGas: number;
  savings: number;
  difficulty: 'easy' | 'medium' | 'hard';
}

// Audit configuration
export interface AuditConfig {
  includeGasAnalysis: boolean;
  includeOptimizations: boolean;
  severityThreshold: SeverityLevel;
  customRules?: string[];
  excludePatterns?: string[];
}

// Report configuration
export interface ReportConfig {
  format: 'pdf' | 'html' | 'json';
  includeSourceCode: boolean;
  includeRecommendations: boolean;
  includeGasAnalysis: boolean;
  template?: 'standard' | 'detailed' | 'executive';
  branding?: {
    logo?: string;
    companyName?: string;
    colors?: {
      primary: string;
      secondary: string;
    };
  };
}
