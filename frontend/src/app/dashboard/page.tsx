'use client';

import { useEffect, useState } from 'react';
import { ConstitutionalIndicator, ConstitutionalScoreBar } from '@/components/constitutional/constitutional-compliance';
import { PersonalizedDashboard } from '@/components/dashboard/personalized-dashboard';
import { Button } from '@/components/ui/button';
import { useConstitutionalContext } from '@/contexts/constitutional-context';
import { usePersonalization, useBehaviorTracking } from '@/contexts/personalization-context';
import { useToast } from '@/contexts/toast-context';
import { CONSTITUTIONAL_HASH } from '@/types';

export default function DashboardPage() {
  const { compliance, validateAction } = useConstitutionalContext();
  const { preferences, layoutConfig } = usePersonalization();
  const { trackPageView, trackAction } = useBehaviorTracking();
  const { showSuccess, showInfo } = useToast();
  const [viewMode, setViewMode] = useState<'personalized' | 'classic'>('personalized');

  useEffect(() => {
    trackPageView('/dashboard');
  }, [trackPageView]);

  const handleTestCompliance = async () => {
    trackAction('test_compliance_clicked');
    const isValid = await validateAction('test_action', { test: true });
    
    if (isValid) {
      showSuccess('Compliance Test', 'Action passed constitutional validation');
    } else {
      showInfo('Compliance Test', 'Action failed constitutional validation');
    }
  };

  const handleTestToast = () => {
    trackAction('test_toast_clicked');
    showInfo('Test Toast', 'This is a test toast notification with constitutional compliance');
  };

  // Toggle between personalized and classic dashboard
  const toggleViewMode = () => {
    const newMode = viewMode === 'personalized' ? 'classic' : 'personalized';
    setViewMode(newMode);
    trackAction('dashboard_view_toggle', { mode: newMode });
    showInfo('Dashboard View', `Switched to ${newMode} dashboard`);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-8 py-12 space-y-12">
        {/* Page Header */}
        <div className="border-b border-border/50 pb-8">
          <div className="flex items-center justify-between">
            <div className="space-y-3">
              <h1 className="text-4xl font-semibold tracking-tight text-foreground">
                ACGS-2 Dashboard
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Constitutional AI Governance System - {viewMode === 'personalized' ? 'Personalized Experience' : 'Classic View'}
              </p>
            </div>
            <Button
              onClick={toggleViewMode}
              variant="outline"
              size="lg"
              className="ml-6"
            >
              Switch to {viewMode === 'personalized' ? 'Classic' : 'Personalized'} View
            </Button>
          </div>
        </div>

        {/* Conditional Dashboard Rendering */}
        {viewMode === 'personalized' ? (
          <PersonalizedDashboard />
        ) : (
          <ClassicDashboard
            compliance={compliance}
            preferences={preferences}
            layoutConfig={layoutConfig}
            validateAction={validateAction}
            trackAction={trackAction}
            showSuccess={showSuccess}
            showInfo={showInfo}
          />
        )}
      </div>
    </div>
  );
}

// Classic Dashboard Component (existing dashboard)
interface ClassicDashboardProps {
  compliance: any;
  preferences: any;
  layoutConfig: any;
  validateAction: (action: string, data?: any) => Promise<boolean>;
  trackAction: (action: string, data?: any) => void;
  showSuccess: (title: string, message: string) => void;
  showInfo: (title: string, message: string) => void;
}

function ClassicDashboard({
  compliance,
  preferences,
  layoutConfig,
  validateAction,
  trackAction,
  showSuccess,
  showInfo
}: ClassicDashboardProps) {
  const handleTestCompliance = async () => {
    trackAction('test_compliance_clicked');
    const isValid = await validateAction('test_action', { test: true });

    if (isValid) {
      showSuccess('Compliance Test', 'Action passed constitutional validation');
    } else {
      showInfo('Compliance Test', 'Action failed constitutional validation');
    }
  };

  const handleTestToast = () => {
    trackAction('test_toast_clicked');
    showInfo('Test Toast', 'This is a test toast notification with constitutional compliance');
  };

  return (
    <>
      {/* Constitutional Compliance Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div className="card">
          <div className="card-header">
            <div className="card-title flex items-center text-lg">
              <ConstitutionalIndicator className="mr-3" />
              Constitutional Status
            </div>
            <div className="card-description">
              Current constitutional compliance status
            </div>
          </div>
          <div className="card-content">
            <ConstitutionalScoreBar score={compliance.score} />
            <div className="mt-4 text-sm text-muted-foreground">
              <p>Hash: <code className="text-xs">{compliance.hash}</code></p>
              <p>Last Validated: {new Date(compliance.lastValidated).toLocaleString()}</p>
              <p>Violations: {compliance.violations.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title text-lg">User Preferences</div>
            <div className="card-description">
              Current personalization settings
            </div>
          </div>
          <div className="card-content">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Theme:</span>
                <span className="font-medium capitalize">{preferences.theme}</span>
              </div>
              <div className="flex justify-between">
                <span>Layout:</span>
                <span className="font-medium capitalize">{preferences.layout}</span>
              </div>
              <div className="flex justify-between">
                <span>Density:</span>
                <span className="font-medium capitalize">{preferences.density}</span>
              </div>
              <div className="flex justify-between">
                <span>Complexity:</span>
                <span className="font-medium capitalize">{preferences.complexity}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title text-lg">Layout Configuration</div>
            <div className="card-description">
              Current adaptive layout settings
            </div>
          </div>
          <div className="card-content">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Sidebar Width:</span>
                <span className="font-medium">{layoutConfig.sidebar.width}px</span>
              </div>
              <div className="flex justify-between">
                <span>Header Height:</span>
                <span className="font-medium">{layoutConfig.header.height}px</span>
              </div>
              <div className="flex justify-between">
                <span>Max Width:</span>
                <span className="font-medium">{layoutConfig.content.maxWidth}</span>
              </div>
              <div className="flex justify-between">
                <span>Collapsed:</span>
                <span className="font-medium">{layoutConfig.sidebar.collapsed ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Testing Section */}
      <div className="card">
        <div className="card-header">
          <div className="card-title text-lg">Feature Testing</div>
          <div className="card-description">
            Test the frontend features and integrations
          </div>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Button
              onClick={handleTestCompliance}
              constitutional
              size="lg"
              className="w-full"
            >
              Test Constitutional Compliance
            </Button>

            <Button
              onClick={handleTestToast}
              variant="outline"
              size="lg"
              className="w-full"
            >
              Test Toast Notifications
            </Button>

            <Button
              onClick={() => trackAction('theme_toggle')}
              variant="secondary"
              size="lg"
              className="w-full"
            >
              Toggle Theme
            </Button>

            <Button
              onClick={() => trackAction('layout_change')}
              variant="ghost"
              size="lg"
              className="w-full"
            >
              Change Layout
            </Button>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="card">
        <div className="card-header">
          <div className="card-title text-lg">System Information</div>
          <div className="card-description">
            Frontend system details and configuration
          </div>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold mb-3">Frontend Configuration</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Framework:</span>
                  <span className="font-medium">Next.js 14</span>
                </div>
                <div className="flex justify-between">
                  <span>UI Library:</span>
                  <span className="font-medium">Tailwind CSS</span>
                </div>
                <div className="flex justify-between">
                  <span>State Management:</span>
                  <span className="font-medium">Zustand + React Query</span>
                </div>
                <div className="flex justify-between">
                  <span>TypeScript:</span>
                  <span className="font-medium">Enabled</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3">API Configuration</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>API Base URL:</span>
                  <span className="font-medium">localhost:8010</span>
                </div>
                <div className="flex justify-between">
                  <span>GraphQL URL:</span>
                  <span className="font-medium">localhost:8010/graphql</span>
                </div>
                <div className="flex justify-between">
                  <span>WebSocket URL:</span>
                  <span className="font-medium">ws://localhost:8010/ws</span>
                </div>
                <div className="flex justify-between">
                  <span>Constitutional Hash:</span>
                  <span className="font-medium text-xs">{CONSTITUTIONAL_HASH}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <div className="card-title text-lg">Quick Actions</div>
          <div className="card-description">
            Common governance and management actions
          </div>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <Button variant="outline" size="default">
              📋 Policies
            </Button>
            <Button variant="outline" size="default">
              🤖 AI Agents
            </Button>
            <Button variant="outline" size="default">
              📊 Analytics
            </Button>
            <Button variant="outline" size="default">
              ⚙️ Settings
            </Button>
            <Button variant="outline" size="default">
              🔍 Search
            </Button>
            <Button variant="outline" size="default">
              👥 Users
            </Button>
            <Button variant="outline" size="default">
              🔐 Security
            </Button>
            <Button variant="outline" size="default">
              📈 Reports
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}