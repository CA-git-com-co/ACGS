/**
 * Custom hook for dashboard data and AI recommendations
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api-client';
import type {
  PersonalizedDashboard,
  AIRecommendation,
  ConstitutionalCompliance,
  GovernanceInsight,
  UserPreferences
} from '@/types';

export function useDashboard(userId?: string) {
  const queryClient = useQueryClient();

  // Fetch dashboard data
  const {
    data: dashboardData,
    isLoading,
    error,
    refetch
  } = useQuery<PersonalizedDashboard>({
    queryKey: ['dashboard', userId],
    queryFn: async () => {
      const response = await apiClient.get<PersonalizedDashboard>('/api/v1/dashboard', {
        userId,
        constitutionalHash: 'cdd01ef066bc6cf2'
      });
      return response.data;
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Refresh every 30 seconds
  });

  // Fetch AI recommendations
  const {
    data: recommendations,
    isLoading: isLoadingRecommendations
  } = useQuery<AIRecommendation[]>({
    queryKey: ['recommendations', userId],
    queryFn: async () => {
      const response = await apiClient.get<AIRecommendation[]>('/api/v1/recommendations', {
        userId,
        constitutionalHash: 'cdd01ef066bc6cf2'
      });
      return response.data;
    },
    enabled: !!userId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Fetch compliance metrics
  const {
    data: complianceMetrics,
    isLoading: isLoadingCompliance
  } = useQuery<ConstitutionalCompliance>({
    queryKey: ['compliance', userId],
    queryFn: async () => {
      const response = await apiClient.get<ConstitutionalCompliance>('/api/v1/compliance/metrics', {
        userId,
        constitutionalHash: 'cdd01ef066bc6cf2'
      });
      return response.data;
    },
    enabled: !!userId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Fetch governance insights
  const {
    data: governanceInsights,
    isLoading: isLoadingInsights
  } = useQuery<GovernanceInsight[]>({
    queryKey: ['governance-insights', userId],
    queryFn: async () => {
      const response = await apiClient.get<GovernanceInsight[]>('/api/v1/governance/insights', {
        userId,
        constitutionalHash: 'cdd01ef066bc6cf2'
      });
      return response.data;
    },
    enabled: !!userId,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });

  // Update dashboard preferences
  const updatePreferences = useMutation({
    mutationFn: async (preferences: Partial<UserPreferences>) => {
      const response = await apiClient.patch<UserPreferences>('/api/v1/dashboard/preferences', {
        userId,
        preferences,
        constitutionalHash: 'cdd01ef066bc6cf2'
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard', userId] });
    }
  });

  // Execute AI recommendation
  const executeRecommendation = useMutation({
    mutationFn: async (recommendationId: string) => {
      const response = await apiClient.post('/api/v1/recommendations/execute', {
        recommendationId,
        userId,
        constitutionalHash: 'cdd01ef066bc6cf2'
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard', userId] });
      queryClient.invalidateQueries({ queryKey: ['recommendations', userId] });
    }
  });

  // Dismiss AI recommendation
  const dismissRecommendation = useMutation({
    mutationFn: async (recommendationId: string) => {
      const response = await apiClient.post('/api/v1/recommendations/dismiss', {
        recommendationId,
        userId,
        constitutionalHash: 'cdd01ef066bc6cf2'
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', userId] });
    }
  });

  // Track user interaction
  const trackInteraction = useMutation({
    mutationFn: async (interaction: {
      type: string;
      target: string;
      value?: any;
    }) => {
      const response = await apiClient.post('/api/v1/analytics/track', {
        userId,
        interaction,
        timestamp: new Date().toISOString(),
        constitutionalHash: 'cdd01ef066bc6cf2'
      });
      return response.data;
    }
  });

  return {
    // Data
    dashboardData,
    recommendations,
    complianceMetrics,
    governanceInsights,
    
    // Loading states
    isLoading: isLoading || isLoadingRecommendations || isLoadingCompliance || isLoadingInsights,
    isLoadingRecommendations,
    isLoadingCompliance,
    isLoadingInsights,
    
    // Error state
    error,
    
    // Actions
    refetch,
    updatePreferences: updatePreferences.mutate,
    executeRecommendation: executeRecommendation.mutate,
    dismissRecommendation: dismissRecommendation.mutate,
    trackInteraction: trackInteraction.mutate,
    
    // Mutation states
    isUpdatingPreferences: updatePreferences.isPending,
    isExecutingRecommendation: executeRecommendation.isPending,
    isDismissingRecommendation: dismissRecommendation.isPending,
    isTrackingInteraction: trackInteraction.isPending,
  };
}