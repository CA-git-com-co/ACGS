'use client';

import * as React from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './button';
import { useToast } from '@/contexts/toast-context';

export interface ToastProps {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  actions?: Array<{
    label: string;
    action: 'dismiss' | 'navigate' | 'execute';
    target?: string;
    style?: 'primary' | 'secondary' | 'destructive';
  }>;
  onClose: () => void;
}

export function Toast({ id, title, message, type, actions, onClose }: ToastProps) {
  const typeStyles = {
    success: 'bg-success-50 border-success-200 text-success-900',
    error: 'bg-error-50 border-error-200 text-error-900',
    warning: 'bg-warning-50 border-warning-200 text-warning-900',
    info: 'bg-blue-50 border-blue-200 text-blue-900',
  };

  const typeIcons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  return (
    <div
      className={cn(
        'relative w-full max-w-sm rounded-lg border p-4 shadow-lg animate-in slide-in-from-top-full',
        typeStyles[type]
      )}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <span className="text-lg">{typeIcons[type]}</span>
        </div>
        <div className="ml-3 w-0 flex-1">
          <p className="text-sm font-medium">{title}</p>
          <p className="mt-1 text-sm opacity-90">{message}</p>
          {actions && actions.length > 0 && (
            <div className="mt-3 flex space-x-2">
              {actions.map((action, index) => (
                <Button
                  key={index}
                  size="sm"
                  variant={action.style === 'primary' ? 'default' : (action.style as any) || 'secondary'}
                  onClick={() => {
                    if (action.action === 'dismiss') {
                      onClose();
                    } else if (action.action === 'navigate' && action.target) {
                      window.location.href = action.target;
                    } else if (action.action === 'execute' && action.target) {
                      // Execute custom action
                      (window as any)[action.target]?.();
                    }
                  }}
                >
                  {action.label}
                </Button>
              ))}
            </div>
          )}
        </div>
        <div className="ml-4 flex-shrink-0 flex">
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-6 w-6 rounded-full"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </Button>
        </div>
      </div>
    </div>
  );
}

export function Toaster() {
  const { messages, removeToast } = useToast();

  return (
    <div className="fixed top-0 right-0 z-50 flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]">
      {messages.map((message) => (
        <Toast
          key={message.id}
          id={message.id}
          title={message.title}
          message={message.message}
          type={message.type}
          actions={message.actions}
          onClose={() => removeToast(message.id)}
        />
      ))}
    </div>
  );
}