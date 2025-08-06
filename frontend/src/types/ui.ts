export interface AlertProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
  dismissible?: boolean;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

export interface FileUploadState {
  file: File | null;
  isUploading: boolean;
  progress: number;
  error?: string;
}

export interface EditorState {
  code: string;
  language: 'solidity' | 'vyper';
  isModified: boolean;
  vulnerabilityMarkers: VulnerabilityMarker[];
}

export interface VulnerabilityMarker {
  id: string;
  line: number;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  message: string;
}

export interface NavigationItem {
  id: string;
  label: string;
  icon?: string;
  href?: string;
  active?: boolean;
}

export interface CardProps {
  title: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export interface BadgeProps {
  variant: 'critical' | 'high' | 'medium' | 'low' | 'info';
  children: React.ReactNode;
  className?: string;
}

export interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  className?: string;
}
