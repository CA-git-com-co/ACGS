'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import { NotificationMessage, NotificationAction, CONSTITUTIONAL_HASH } from '@/types';

interface ToastContextType {
  messages: NotificationMessage[];
  addToast: (message: Omit<NotificationMessage, 'id' | 'createdAt' | 'constitutionalCompliance'>) => void;
  removeToast: (id: string) => void;
  clearAll: () => void;
  showSuccess: (title: string, message: string, actions?: NotificationAction[]) => void;
  showError: (title: string, message: string, actions?: NotificationAction[]) => void;
  showWarning: (title: string, message: string, actions?: NotificationAction[]) => void;
  showInfo: (title: string, message: string, actions?: NotificationAction[]) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<NotificationMessage[]>([]);

  const addToast = (message: Omit<NotificationMessage, 'id' | 'createdAt' | 'constitutionalCompliance'>) => {
    const newMessage: NotificationMessage = {
      ...message,
      id: Math.random().toString(36).substring(2, 9),
      createdAt: new Date().toISOString(),
      constitutionalCompliance: {
        hash: CONSTITUTIONAL_HASH,
        compliant: true,
        score: 1.0,
        violations: [],
        lastValidated: new Date().toISOString(),
        metadata: { source: 'toast' },
      },
    };

    setMessages(prev => [...prev, newMessage]);

    // Auto-remove after duration
    if (message.duration && message.duration > 0) {
      setTimeout(() => {
        removeToast(newMessage.id);
      }, message.duration);
    }
  };

  const removeToast = (id: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== id));
  };

  const clearAll = () => {
    setMessages([]);
  };

  const showSuccess = (title: string, message: string, actions?: NotificationAction[]) => {
    addToast({
      type: 'success',
      title,
      message,
      duration: 5000,
      actions,
    });
  };

  const showError = (title: string, message: string, actions?: NotificationAction[]) => {
    addToast({
      type: 'error',
      title,
      message,
      duration: 0, // Don't auto-dismiss errors
      actions,
    });
  };

  const showWarning = (title: string, message: string, actions?: NotificationAction[]) => {
    addToast({
      type: 'warning',
      title,
      message,
      duration: 8000,
      actions,
    });
  };

  const showInfo = (title: string, message: string, actions?: NotificationAction[]) => {
    addToast({
      type: 'info',
      title,
      message,
      duration: 4000,
      actions,
    });
  };

  const value: ToastContextType = {
    messages,
    addToast,
    removeToast,
    clearAll,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}