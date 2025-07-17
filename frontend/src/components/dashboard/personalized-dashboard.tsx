'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Activity, 
  TrendingUp, 
  Users, 
  Shield, 
  Brain, 
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { ConstitutionalIndicator, ConstitutionalScoreBar } from '@/components/constitutional/constitutional-compliance';
import { useConstitutionalContext } from '@/contexts/constitutional-context';
import { usePersonalization, useBehaviorTracking } from '@/contexts/personalization-context';
import { useToast } from '@/contexts/toast-context';
import { mockAPI, shouldUseMockAPI } from '@/lib/mock-api';
import { apiClient } from '@/services/api-client';
import { cn } from '@/lib/utils';

import type { PersonalizedDashboard, GovernanceInsight, AIRecommendation } from '@/types';

export function PersonalizedDashboard() {
  const { compliance } = useConstitutionalContext();
  const { preferences } = usePersonalization();
  const { trackPageView, trackAction } = useBehaviorTracking();
  const { showSuccess, showInfo, showError } = useToast();

  // Track page view
  useEffect(() => {
    trackPageView('/dashboard/personalized');
  }, [trackPageView]);

  // Fetch dashboard data
  const { data: dashboardData, isLoading, error, refetch } = useQuery({
    queryKey: ['personalized-dashboard'],
    queryFn: async () => {
      if (shouldUseMockAPI()) {
        return mockAPI.getDashboard();
      }
      return apiClient.get<PersonalizedDashboard>('/api/dashboard/personalized');
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // 30 seconds
  });

  const dashboard = dashboardData?.data;

  const handleQuickAction = async (actionId: string, target: string, action: string) => {
    trackAction('quick_action_clicked', { actionId, target, action });
    
    if (action === 'navigate') {
      // In a real app, this would use Next.js router
      showInfo('Navigation', `Would navigate to: ${target}`);
    } else if (action === 'execute') {
      showInfo('Action Executed', `Executing: ${target}`);
      // Simulate action execution
      setTimeout(() => {
        showSuccess('Action Complete', `Successfully executed: ${target}`);
      }, 2000);
    }
  };

  const handleInsightAction = (insight: GovernanceInsight) => {
    trackAction('insight_clicked', { insightId: insight.id, type: insight.type });
    showInfo('Insight Details', insight.description);
  };

  const handleRecommendationAction = (recommendation: AIRecommendation) => {
    trackAction('recommendation_clicked', { 
      recommendationId: recommendation.id, 
      confidence: recommendation.confidence 
    });
    
    if (recommendation.actionUrl) {
      showInfo('Recommendation Action', `Would navigate to: ${recommendation.actionUrl}`);
    } else {
      showInfo('AI Recommendation', recommendation.description);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-constitutional-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading personalized dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-error-600 mx-auto mb-4" />
          <p className="text-error-600 mb-4">Failed to load dashboard data</p>
          <Button onClick={() => refetch()} variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {dashboard.user.name}
          </h1>
          <p className="text-muted-foreground mt-1">
            Here's your personalized governance overview
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <ConstitutionalIndicator />
          <Button 
            onClick={() => refetch()}
            variant="outline"
            size="sm"
          >
            <Activity className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Constitutional Score"
          value={`${(compliance.score * 100).toFixed(1)}%`}
          icon={<Shield className="h-5 w-5" />}
          trend="+2.3%"
          color="constitutional"
        />
        <MetricCard
          title="Active Policies"
          value="127"
          icon={<BarChart3 className="h-5 w-5" />}
          trend="+5"
          color="governance"
        />
        <MetricCard
          title="AI Insights"
          value={dashboard.insights.length.toString()}
          icon={<Brain className="h-5 w-5" />}
          trend="+3"
          color="success"
        />
        <MetricCard
          title="Pending Actions"
          value="8"
          icon={<Clock className="h-5 w-5" />}
          trend="-2"
          color="warning"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-1">
          <div className="card">
            <div className="card-header">
              <div className="card-title flex items-center">
                <Zap className="h-5 w-5 mr-2" />
                Quick Actions
              </div>
              <div className="card-description">
                Frequently used governance actions
              </div>
            </div>
            <div className="card-content">
              <div className="space-y-3">
                {dashboard.quickActions.slice(0, 4).map((action) => (
                  <Button
                    key={action.id}
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => handleQuickAction(action.id, action.target, action.action)}
                  >
                    <span className="mr-3 text-lg">{action.icon}</span>
                    <div className="text-left">
                      <div className="font-medium">{action.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {action.description}
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* AI Insights & Recommendations */}
        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Governance Insights */}
            <div className="card">
              <div className="card-header">
                <div className="card-title flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Governance Insights
                </div>
                <div className="card-description">
                  AI-powered governance analysis
                </div>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  {dashboard.insights.slice(0, 2).map((insight) => (
                    <div
                      key={insight.id}
                      className="p-3 rounded-lg border cursor-pointer hover:bg-accent/50 transition-colors"
                      onClick={() => handleInsightAction(insight)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-sm">{insight.title}</h4>
                        <span className={cn(
                          'text-xs px-2 py-1 rounded-full',
                          insight.severity === 'success' && 'bg-success-100 text-success-700',
                          insight.severity === 'info' && 'bg-blue-100 text-blue-700',
                          insight.severity === 'warning' && 'bg-warning-100 text-warning-700',
                          insight.severity === 'error' && 'bg-error-100 text-error-700'
                        )}>
                          {insight.type}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {insight.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Recommendations */}
            <div className="card">
              <div className="card-header">
                <div className="card-title flex items-center">
                  <Brain className="h-5 w-5 mr-2" />
                  AI Recommendations
                </div>
                <div className="card-description">
                  Personalized optimization suggestions
                </div>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  {dashboard.recommendations.slice(0, 2).map((rec) => (
                    <div
                      key={rec.id}
                      className="p-3 rounded-lg border cursor-pointer hover:bg-accent/50 transition-colors"
                      onClick={() => handleRecommendationAction(rec)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-sm">{rec.title}</h4>
                        <div className="flex items-center space-x-1">
                          <span className="text-xs text-muted-foreground">
                            {(rec.confidence * 100).toFixed(0)}%
                          </span>
                          <CheckCircle className="h-3 w-3 text-success-600" />
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {rec.description}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className={cn(
                          'text-xs px-2 py-1 rounded-full',
                          rec.impact === 'high' && 'bg-success-100 text-success-700',
                          rec.impact === 'medium' && 'bg-warning-100 text-warning-700',
                          rec.impact === 'low' && 'bg-gray-100 text-gray-700'
                        )}>
                          {rec.impact} impact
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {rec.effort} effort
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Constitutional Compliance Status */}
      <div className="card">
        <div className="card-header">
          <div className="card-title flex items-center">
            <Shield className="h-5 w-5 mr-2" />
            Constitutional Compliance Status
          </div>
          <div className="card-description">
            Real-time constitutional compliance monitoring
          </div>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <ConstitutionalScoreBar score={compliance.score} />
            </div>
            <div className="space-y-2">
              <div className="text-sm font-medium">Compliance Principles</div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {dashboard.user.constitutionalContext.principles.slice(0, 6).map((principle) => (
                  <div key={principle} className="flex items-center space-x-1">
                    <CheckCircle className="h-3 w-3 text-success-600" />
                    <span className="capitalize">{principle.replace('-', ' ')}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-sm font-medium">System Status</div>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span>Last Validated:</span>
                  <span>{new Date(compliance.lastValidated).toLocaleTimeString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Violations:</span>
                  <span className="text-success-600">{compliance.violations.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Hash:</span>
                  <span className="font-mono text-xs">{compliance.hash.slice(0, 8)}...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Metric Card Component
interface MetricCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  trend?: string;
  color?: 'constitutional' | 'governance' | 'success' | 'warning' | 'error';
}

function MetricCard({ title, value, icon, trend, color = 'constitutional' }: MetricCardProps) {
  const colorClasses = {
    constitutional: 'text-constitutional-600 bg-constitutional-50',
    governance: 'text-governance-600 bg-governance-50',
    success: 'text-success-600 bg-success-50',
    warning: 'text-warning-600 bg-warning-50',
    error: 'text-error-600 bg-error-50'
  };

  return (
    <div className="card">
      <div className="card-content">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {trend && (
              <p className="text-xs text-muted-foreground mt-1">
                {trend} from last period
              </p>
            )}
          </div>
          <div className={cn('p-3 rounded-full', colorClasses[color])}>
            {icon}
          </div>
        </div>
      </div>
    </div>
  );
}
