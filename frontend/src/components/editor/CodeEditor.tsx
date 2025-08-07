'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Editor } from '@monaco-editor/react';
import { Upload, Play, FileText, Code } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { useAudit } from '@/hooks/useAudit';
import type { EditorState } from '@/types/ui';

const EXAMPLE_CONTRACT = `pragma solidity ^0.8.0;

contract ExampleContract {
    address public owner;
    mapping(address => uint256) public balances;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
    }
    
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
    }
}`;

export function CodeEditor(): JSX.Element {
  const [editorState, setEditorState] = useState<EditorState>({
    code: EXAMPLE_CONTRACT,
    language: 'solidity',
    isModified: false,
    vulnerabilityMarkers: [],
  });

  const { runAudit, isLoading } = useAudit();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setEditorState(prev => ({
          ...prev,
          code: content,
          isModified: true,
        }));
      };
      reader.readAsText(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.sol', '.vy', '.txt'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setEditorState(prev => ({
        ...prev,
        code: value,
        isModified: true,
      }));
    }
  };

  const handleLanguageChange = (language: 'solidity' | 'vyper') => {
    setEditorState(prev => ({
      ...prev,
      language,
    }));
  };

  const handleRunAudit = async () => {
    if (!editorState.code.trim()) {
      (window as unknown as { showAlert?: (alert: { type: string; message: string }) => void }).showAlert?.({
        type: 'warning',
        message: 'Please enter some contract code to audit.',
      });
      return;
    }

    try {
      await runAudit({
        contract_code: editorState.code,
        contract_metadata: {
          name: 'UserContract',
          language: editorState.language,
        },
      });
    } catch (error) {
      console.error('Audit failed:', error);
    }
  };

  const actions = (
    <div className="flex items-center space-x-2">
      <select
        value={editorState.language}
        onChange={(e) => handleLanguageChange(e.target.value as 'solidity' | 'vyper')}
        className="select"
      >
        <option value="solidity">Solidity</option>
        <option value="vyper">Vyper</option>
      </select>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <Upload className="h-4 w-4" />
        Upload
      </Button>
      <Button
        variant="primary"
        size="sm"
        onClick={handleRunAudit}
        loading={isLoading}
        disabled={!editorState.code.trim()}
      >
        <Play className="h-4 w-4" />
        Run Audit
      </Button>
    </div>
  );

  return (
    <Card
      title="Smart Contract Editor"
      icon={<Code className="h-5 w-5" />}
      actions={actions}
      className="h-fit"
    >
      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={cn(
          'mb-4 cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition-colors',
          isDragActive
            ? 'border-primary-400 bg-primary-400/10'
            : 'border-dark-600 hover:border-primary-500 hover:bg-primary-500/5'
        )}
      >
        <input {...getInputProps()} id="file-input" />
        <FileText className="mx-auto mb-2 h-8 w-8 text-dark-400" />
        <p className="text-sm text-dark-300">
          {isDragActive
            ? 'Drop the contract file here...'
            : 'Drag & drop a contract file here, or click to select'}
        </p>
        <p className="mt-1 text-xs text-dark-500">
          Supports .sol, .vy, .txt files (max 10MB)
        </p>
      </div>

      {/* Code Editor */}
      <div className="h-96 overflow-hidden rounded-lg border border-dark-600">
        <Editor
          height="100%"
          language={editorState.language === 'solidity' ? 'sol' : 'python'}
          value={editorState.code}
          onChange={handleEditorChange}
          theme="vs-dark"
          options={{
            minimap: { enabled: true, scale: 0.5 },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            insertSpaces: true,
            wordWrap: 'on',
            contextmenu: true,
            selectOnLineNumbers: true,
            glyphMargin: true,
            folding: true,
            foldingHighlight: true,
            showFoldingControls: 'always',
            // Enhanced features
            bracketPairColorization: { enabled: true },
            guides: {
              bracketPairs: true,
              indentation: true,
            },
            suggest: {
              showKeywords: true,
              showSnippets: true,
            },
            quickSuggestions: {
              other: true,
              comments: false,
              strings: false,
            },
            parameterHints: { enabled: true },
            hover: { enabled: true },
            // Vulnerability highlighting
            renderLineHighlight: 'gutter',
            renderWhitespace: 'selection',
          }}
          onMount={(editor, monaco) => {
            // Add vulnerability markers when audit completes
            const handleAuditComplete = (event: CustomEvent): void => {
              const result = event.detail;
              if (result?.vulnerabilities) {
                const markers = result.vulnerabilities.map((vuln: { location: { line: number }; severity: string; title: string }) => ({
                  startLineNumber: vuln.location.line,
                  startColumn: 1,
                  endLineNumber: vuln.location.line,
                  endColumn: 1000,
                  message: `${vuln.severity.toUpperCase()}: ${vuln.title}`,
                  severity: vuln.severity === 'critical' ? monaco.MarkerSeverity.Error :
                           vuln.severity === 'high' ? monaco.MarkerSeverity.Error :
                           vuln.severity === 'medium' ? monaco.MarkerSeverity.Warning :
                           monaco.MarkerSeverity.Info,
                }));
                const model = editor.getModel();
                if (model) {
                  monaco.editor.setModelMarkers(model, 'audit', markers);
                }
              }
            };

            window.addEventListener('auditComplete', handleAuditComplete as EventListener);
          }}
        />
      </div>

      {/* Editor Status */}
      <div className="mt-4 flex items-center justify-between text-sm text-dark-400">
        <div className="flex items-center space-x-4">
          <span>Language: {editorState.language}</span>
          <span>Lines: {editorState.code.split('\n').length}</span>
          <span>Characters: {editorState.code.length}</span>
        </div>
        {editorState.isModified && (
          <span className="text-yellow-400">• Modified</span>
        )}
      </div>
    </Card>
  );
}
