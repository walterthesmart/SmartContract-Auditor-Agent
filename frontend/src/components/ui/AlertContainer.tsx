'use client';

import { useState, useEffect } from 'react';
import { X, CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AlertProps } from '@/types/ui';

const alertIcons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const alertStyles = {
  success: 'border-green-500/30 bg-green-900/20 text-green-300',
  error: 'border-red-500/30 bg-red-900/20 text-red-300',
  warning: 'border-yellow-500/30 bg-yellow-900/20 text-yellow-300',
  info: 'border-blue-500/30 bg-blue-900/20 text-blue-300',
};

export function AlertContainer(): JSX.Element | null {
  const [alerts, setAlerts] = useState<AlertProps[]>([]);

  const removeAlert = (id: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  const addAlert = (alert: Omit<AlertProps, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newAlert = { ...alert, id };
    
    setAlerts(prev => [...prev, newAlert]);

    if (alert.duration !== 0) {
      setTimeout(() => {
        removeAlert(id);
      }, alert.duration || 5000);
    }
  };

  // Global alert function
  useEffect(() => {
    (window as any).showAlert = addAlert;
    return () => {
      delete (window as any).showAlert;
    };
  }, []);

  if (alerts.length === 0) {
    return null;
  }

  return (
    <div className="fixed right-4 top-20 z-50 space-y-2">
      {alerts.map((alert) => {
        const Icon = alertIcons[alert.type];
        
        return (
          <div
            key={alert.id}
            className={cn(
              'flex items-start space-x-3 rounded-lg border p-4 shadow-lg backdrop-blur-sm',
              'animate-slide-down max-w-md',
              alertStyles[alert.type]
            )}
          >
            <Icon className="mt-0.5 h-5 w-5 flex-shrink-0" />
            <div className="flex-1 space-y-1">
              {alert.title && (
                <h4 className="font-medium">{alert.title}</h4>
              )}
              <p className="text-sm opacity-90">{alert.message}</p>
            </div>
            {alert.dismissible !== false && (
              <button
                onClick={() => removeAlert(alert.id)}
                className="flex-shrink-0 rounded-md p-1 opacity-70 transition-opacity hover:opacity-100"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
