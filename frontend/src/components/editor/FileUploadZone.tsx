'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import { cn, formatFileSize } from '@/lib/utils';

interface FileUploadZoneProps {
  onFileUpload: (content: string, filename: string) => void;
  acceptedTypes?: string[];
  maxSize?: number;
  className?: string;
}

interface UploadedFile {
  name: string;
  size: number;
  content: string;
  status: 'uploading' | 'success' | 'error';
  error?: string;
}

export function FileUploadZone({
  onFileUpload,
  acceptedTypes = ['.sol', '.vy', '.txt'],
  maxSize = 10 * 1024 * 1024, // 10MB
  className,
}: FileUploadZoneProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      // Handle rejected files
      rejectedFiles.forEach((rejection) => {
        const error = rejection.errors[0]?.message || 'File rejected';
        if (typeof window !== 'undefined' && (window as any).showAlert) {
          (window as any).showAlert({
            type: 'error',
            title: 'File Upload Error',
            message: `${rejection.file.name}: ${error}`,
          });
        }
      });

      // Process accepted files
      acceptedFiles.forEach((file) => {
        const fileInfo: UploadedFile = {
          name: file.name,
          size: file.size,
          content: '',
          status: 'uploading',
        };

        setUploadedFiles((prev) => [...prev, fileInfo]);

        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          
          setUploadedFiles((prev) =>
            prev.map((f) =>
              f.name === file.name
                ? { ...f, content, status: 'success' }
                : f
            )
          );

          onFileUpload(content, file.name);

          if (typeof window !== 'undefined' && (window as any).showAlert) {
            (window as any).showAlert({
              type: 'success',
              title: 'File Uploaded',
              message: `${file.name} has been loaded successfully.`,
            });
          }
        };

        reader.onerror = () => {
          setUploadedFiles((prev) =>
            prev.map((f) =>
              f.name === file.name
                ? { ...f, status: 'error', error: 'Failed to read file' }
                : f
            )
          );
        };

        reader.readAsText(file);
      });
    },
    [onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/plain': acceptedTypes,
    },
    maxFiles: 1,
    maxSize,
    multiple: false,
  });

  const removeFile = (filename: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.name !== filename));
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={cn(
          'cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition-all duration-200',
          isDragActive && !isDragReject
            ? 'border-primary-400 bg-primary-400/10 scale-105'
            : isDragReject
            ? 'border-red-400 bg-red-400/10'
            : 'border-dark-600 hover:border-primary-500 hover:bg-primary-500/5'
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-2">
          <div className={cn(
            'rounded-full p-3 transition-colors',
            isDragActive && !isDragReject
              ? 'bg-primary-500/20 text-primary-400'
              : isDragReject
              ? 'bg-red-500/20 text-red-400'
              : 'bg-dark-700 text-dark-400'
          )}>
            {isDragReject ? (
              <AlertCircle className="h-8 w-8" />
            ) : (
              <Upload className="h-8 w-8" />
            )}
          </div>
          
          <div>
            <p className="text-sm font-medium text-dark-200">
              {isDragActive && !isDragReject
                ? 'Drop the contract file here...'
                : isDragReject
                ? 'File type not supported'
                : 'Drag & drop a contract file here, or click to select'}
            </p>
            <p className="mt-1 text-xs text-dark-500">
              Supports {acceptedTypes.join(', ')} files (max {formatFileSize(maxSize)})
            </p>
          </div>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-dark-300">Uploaded Files</h4>
          {uploadedFiles.map((file) => (
            <div
              key={file.name}
              className="flex items-center justify-between rounded-lg bg-dark-800/50 p-3"
            >
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-primary-400" />
                <div>
                  <p className="text-sm font-medium text-white">{file.name}</p>
                  <p className="text-xs text-dark-400">
                    {formatFileSize(file.size)}
                    {file.status === 'uploading' && ' • Uploading...'}
                    {file.status === 'error' && ` • ${file.error}`}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {file.status === 'uploading' && (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-400 border-t-transparent" />
                )}
                {file.status === 'success' && (
                  <CheckCircle className="h-4 w-4 text-green-400" />
                )}
                {file.status === 'error' && (
                  <AlertCircle className="h-4 w-4 text-red-400" />
                )}
                
                <button
                  onClick={() => removeFile(file.name)}
                  className="text-dark-400 hover:text-red-400 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
