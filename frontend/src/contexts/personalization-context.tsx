'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { UserPreferences, BehaviorPatterns, LayoutConfig, AdaptiveUIConfig, CONSTITUTIONAL_HASH } from '@/types';

interface PersonalizationContextType {
  preferences: UserPreferences;
  behaviorPatterns: BehaviorPatterns;
  layoutConfig: LayoutConfig;
  adaptiveConfig: AdaptiveUIConfig | null;
  isLoading: boolean;
  error: string | null;
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<void>;
  updateLayoutConfig: (updates: Partial<LayoutConfig>) => void;
  trackBehavior: (action: string, context?: any) => void;
  getPersonalizedContent: (contentType: string) => Promise<any>;
  resetPersonalization: () => Promise<void>;
}

const PersonalizationContext = createContext<PersonalizationContextType | undefined>(undefined);

const defaultPreferences: UserPreferences = {
  theme: 'system',
  language: 'en',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  density: 'comfortable',
  layout: 'sidebar',
  complexity: 'intermediate',
  notifications: {
    email: true,
    push: true,
    governance: true,
    compliance: true,
    system: false,
    frequency: 'immediate',
  },
  accessibility: {
    highContrast: false,
    largeText: false,
    reducedMotion: false,
    screenReader: false,
    keyboardNavigation: false,
  },
};

const defaultBehaviorPatterns: BehaviorPatterns = {
  frequentActions: [],
  timeOfDayUsage: {},
  devicePreferences: [],
  averageSessionDuration: 0,
  preferredWorkflows: [],
};

const defaultLayoutConfig: LayoutConfig = {
  theme: 'system',
  layout: 'sidebar',
  density: 'comfortable',
  complexity: 'intermediate',
  sidebar: {
    collapsed: false,
    width: 280,
    position: 'left',
  },
  header: {
    height: 64,
    sticky: true,
    breadcrumbs: true,
  },
  content: {
    maxWidth: '1200px',
    padding: '24px',
    spacing: '16px',
  },
};

export function PersonalizationProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferences] = useState<UserPreferences>(defaultPreferences);
  const [behaviorPatterns, setBehaviorPatterns] = useState<BehaviorPatterns>(defaultBehaviorPatterns);
  const [layoutConfig, setLayoutConfig] = useState<LayoutConfig>(defaultLayoutConfig);
  const [adaptiveConfig, setAdaptiveConfig] = useState<AdaptiveUIConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updatePreferences = async (updates: Partial<UserPreferences>) => {
    setIsLoading(true);
    setError(null);

    try {
      const updatedPreferences = { ...preferences, ...updates };
      
      // Save to API
      const response = await fetch('/api/users/me/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
        },
        body: JSON.stringify(updatedPreferences),
      });

      if (!response.ok) {
        throw new Error(`Failed to update preferences: ${response.statusText}`);
      }

      const result = await response.json();
      setPreferences(result.data);
      
      // Update layout config based on preferences
      setLayoutConfig(prev => ({
        ...prev,
        theme: updatedPreferences.theme || prev.theme,
        layout: updatedPreferences.layout || prev.layout,
        density: updatedPreferences.density || prev.density,
        complexity: updatedPreferences.complexity || prev.complexity,
      }));

      // Save to localStorage for offline access
      localStorage.setItem('acgs2_preferences', JSON.stringify(result.data));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const updateLayoutConfig = (updates: Partial<LayoutConfig>) => {
    const updatedConfig = { ...layoutConfig, ...updates };
    setLayoutConfig(updatedConfig);
    localStorage.setItem('acgs2_layout_config', JSON.stringify(updatedConfig));
  };

  const trackBehavior = (action: string, context?: any) => {
    const now = new Date();
    const hourOfDay = now.getHours();
    
    // Update behavior patterns
    setBehaviorPatterns(prev => {
      const updatedPatterns = {
        ...prev,
        frequentActions: [
          ...prev.frequentActions.filter(a => a !== action),
          action,
        ].slice(-10), // Keep last 10 actions
        timeOfDayUsage: {
          ...prev.timeOfDayUsage,
          [hourOfDay]: (prev.timeOfDayUsage[hourOfDay] || 0) + 1,
        },
      };

      // Save to localStorage
      localStorage.setItem('acgs2_behavior_patterns', JSON.stringify(updatedPatterns));
      
      return updatedPatterns;
    });

    // Send to analytics API (fire and forget)
    fetch('/api/analytics/behavior', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
      },
      body: JSON.stringify({
        action,
        context,
        timestamp: now.toISOString(),
      }),
    }).catch(err => {
      console.warn('Failed to track behavior:', err);
    });
  };

  const getPersonalizedContent = async (contentType: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/personalization/${contentType}`, {
        headers: {
          'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get personalized content: ${response.statusText}`);
      }

      const result = await response.json();
      return result.data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const resetPersonalization = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Reset to defaults
      setPreferences(defaultPreferences);
      setBehaviorPatterns(defaultBehaviorPatterns);
      setLayoutConfig(defaultLayoutConfig);
      setAdaptiveConfig(null);

      // Clear localStorage
      localStorage.removeItem('acgs2_preferences');
      localStorage.removeItem('acgs2_behavior_patterns');
      localStorage.removeItem('acgs2_layout_config');

      // Reset on server
      await fetch('/api/users/me/personalization/reset', {
        method: 'POST',
        headers: {
          'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
        },
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Initialize personalization on mount
  useEffect(() => {
    const initializePersonalization = async () => {
      setIsLoading(true);

      try {
        // Load from localStorage first for immediate UI
        const savedPreferences = localStorage.getItem('acgs2_preferences');
        const savedBehaviorPatterns = localStorage.getItem('acgs2_behavior_patterns');
        const savedLayoutConfig = localStorage.getItem('acgs2_layout_config');

        if (savedPreferences) {
          setPreferences(JSON.parse(savedPreferences));
        }
        if (savedBehaviorPatterns) {
          setBehaviorPatterns(JSON.parse(savedBehaviorPatterns));
        }
        if (savedLayoutConfig) {
          setLayoutConfig(JSON.parse(savedLayoutConfig));
        }

        // Then fetch from API for latest data
        const response = await fetch('/api/users/me/personalization', {
          headers: {
            'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
          },
        });

        if (response.ok) {
          const result = await response.json();
          setPreferences(result.data.preferences);
          setBehaviorPatterns(result.data.behaviorPatterns);
          setAdaptiveConfig(result.data.adaptiveConfig);
        }
      } catch (err) {
        console.warn('Failed to initialize personalization:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initializePersonalization();
  }, []);

  // Update adaptive config when preferences or behavior patterns change
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const deviceInfo = {
        type: (window.innerWidth > 768 ? 'desktop' : window.innerWidth > 480 ? 'tablet' : 'mobile') as 'desktop' | 'tablet' | 'mobile',
        os: navigator.platform || 'Unknown',
        browser: navigator.userAgent || 'Unknown',
        screenSize: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
        touchCapable: 'ontouchstart' in window,
        darkModeSupported: window.matchMedia('(prefers-color-scheme: dark)').matches,
      };

      const contextualFactors = {
        timeOfDay: new Date().getHours().toString(),
        dayOfWeek: new Date().getDay().toString(),
        networkSpeed: (navigator as any).connection?.effectiveType || 'unknown',
        isOnline: navigator.onLine,
      };

      setAdaptiveConfig({
        userId: 'current-user', // This would come from auth context
        preferences,
        behaviorPatterns,
        deviceInfo,
        contextualFactors,
      });
    }
  }, [preferences, behaviorPatterns]);

  const value: PersonalizationContextType = {
    preferences,
    behaviorPatterns,
    layoutConfig,
    adaptiveConfig,
    isLoading,
    error,
    updatePreferences,
    updateLayoutConfig,
    trackBehavior,
    getPersonalizedContent,
    resetPersonalization,
  };

  return (
    <PersonalizationContext.Provider value={value}>
      {children}
    </PersonalizationContext.Provider>
  );
}

export function usePersonalization() {
  const context = useContext(PersonalizationContext);
  if (context === undefined) {
    throw new Error('usePersonalization must be used within a PersonalizationProvider');
  }
  return context;
}

export function useAdaptiveLayout() {
  const { layoutConfig, updateLayoutConfig, adaptiveConfig } = usePersonalization();
  
  return {
    layoutConfig,
    updateLayoutConfig,
    adaptiveConfig,
    isDesktop: adaptiveConfig?.deviceInfo.type === 'desktop',
    isTablet: adaptiveConfig?.deviceInfo.type === 'tablet',
    isMobile: adaptiveConfig?.deviceInfo.type === 'mobile',
  };
}

export function useBehaviorTracking() {
  const { trackBehavior, behaviorPatterns } = usePersonalization();
  
  return {
    trackBehavior,
    behaviorPatterns,
    trackPageView: (page: string) => trackBehavior('page_view', { page }),
    trackAction: (action: string, context?: any) => trackBehavior('user_action', { action, context }),
    trackError: (error: string, context?: any) => trackBehavior('error', { error, context }),
  };
}