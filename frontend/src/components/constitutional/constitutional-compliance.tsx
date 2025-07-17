'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { useConstitutionalContext } from '@/contexts/constitutional-context';
import { useToast } from '@/contexts/toast-context';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function ConstitutionalCompliance({ children }: { children: React.ReactNode }) {
  const { compliance, error, refreshCompliance } = useConstitutionalContext();
  const { showError, showWarning, showSuccess } = useToast();
  const [hasShownError, setHasShownError] = useState(false);

  useEffect(() => {
    if (error && !hasShownError) {
      showError('Constitutional Compliance Error', error);
      setHasShownError(true);
    }
  }, [error, hasShownError, showError]);

  useEffect(() => {
    if (!compliance.compliant && compliance.violations.length > 0) {
      showWarning(
        'Constitutional Compliance Violation',
        `${compliance.violations.length} violation(s) detected`
      );
    }
  }, [compliance, showWarning]);

  return (
    <div className="constitutional-compliance-wrapper">
      {/* Constitutional Compliance Status Bar */}
      <div
        className={cn(
          'border-b px-4 py-2 text-sm',
          compliance.compliant
            ? 'bg-success-50 border-success-200 text-success-800'
            : 'bg-error-50 border-error-200 text-error-800'
        )}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {compliance.compliant ? (
              <CheckCircle className="h-4 w-4 text-success-600" />
            ) : (
              <XCircle className="h-4 w-4 text-error-600" />
            )}
            <span className="font-medium">
              Constitutional Compliance: {compliance.compliant ? 'Compliant' : 'Non-Compliant'}
            </span>
            <span className="text-xs opacity-75">
              Score: {(compliance.score * 100).toFixed(1)}%
            </span>
            <span className="text-xs opacity-75">
              Hash: {compliance.hash}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            {compliance.violations.length > 0 && (
              <span className="flex items-center text-xs text-error-600">
                <AlertTriangle className="h-3 w-3 mr-1" />
                {compliance.violations.length} violation(s)
              </span>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={refreshCompliance}
              className="h-6 text-xs"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Refresh
            </Button>
          </div>
        </div>
        
        {compliance.violations.length > 0 && (
          <div className="mt-2 text-xs">
            <details className="cursor-pointer">
              <summary className="hover:underline">View Violations</summary>
              <ul className="mt-1 ml-4 space-y-1">
                {compliance.violations.map((violation, index) => (
                  <li key={index} className="list-disc">
                    {violation}
                  </li>
                ))}
              </ul>
            </details>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="constitutional-compliance-content">
        {children}
      </div>
    </div>
  );
}

export function ConstitutionalIndicator({ className }: { className?: string }) {
  const { compliance } = useConstitutionalContext();
  
  return (
    <div
      className={cn(
        'constitutional-indicator',
        compliance.compliant ? 'compliant' : 'non-compliant',
        className
      )}
    >
      {compliance.compliant ? (
        <CheckCircle className="h-3 w-3" />
      ) : (
        <XCircle className="h-3 w-3" />
      )}
      <span>Constitutional</span>
    </div>
  );
}

export function ConstitutionalScoreBar({ score, className }: { score: number; className?: string }) {
  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-success-500';
    if (score >= 0.6) return 'bg-warning-500';
    return 'bg-error-500';
  };

  return (
    <div className={cn('constitutional-score-bar', className)}>
      <div className="flex items-center justify-between text-xs mb-1">
        <span>Constitutional Score</span>
        <span>{(score * 100).toFixed(1)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={cn('h-2 rounded-full transition-all duration-300', getScoreColor(score))}
          style={{ width: `${score * 100}%` }}
        />
      </div>
    </div>
  );
}