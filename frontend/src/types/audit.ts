export interface ContractMetadata {
  name: string;
  language: 'solidity' | 'vyper';
  hash?: string;
}

export interface Vulnerability {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  title: string;
  description: string;
  location: {
    line: number;
    column?: number;
    function?: string;
  };
  recommendation?: string;
  references?: string[];
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
