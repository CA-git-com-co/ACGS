/**
 * Performance-Optimized Component Library
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * High-performance, reusable components for no-code platform
 * with constitutional compliance and sub-5ms rendering targets.
 */

import React, { memo, useMemo, useCallback, lazy, Suspense } from 'react';
import { useConstitutionalValidation } from '@/hooks/useConstitutionalValidation';
import { CONFIG } from '@/config';

// Lazy load heavy components for better performance
const ChartComponent = lazy(() => import('./components/ChartComponent'));
const WorkflowComponent = lazy(() => import('./components/WorkflowComponent'));
const DataTableComponent = lazy(() => import('./components/DataTableComponent'));

// Types
interface ComponentLibraryProps {
  onComponentSelect?: (component: NoCodeComponent) => void;
  filter?: string;
  category?: ComponentCategory;
  performanceMode?: 'standard' | 'optimized' | 'ultra';
}

interface NoCodeComponent {
  id: string;
  name: string;
  type: ComponentType;
  category: ComponentCategory;
  icon: string;
  description: string;
  tags: string[];
  constitutionalHash: string;
  performanceProfile: PerformanceProfile;
  configuration: ComponentConfiguration;
  renderComponent: React.ComponentType<any>;
  previewComponent: React.ComponentType<any>;
  validationRules: ValidationRule[];
  dependencies: string[];
  version: string;
  lastUpdated: string;
  popularity: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedRenderTime: number;
}

type ComponentType = 'form' | 'chart' | 'table' | 'workflow' | 'api' | 'layout' | 'input' | 'display' | 'navigation';
type ComponentCategory = 'Data Input' | 'Data Display' | 'Visualization' | 'Automation' | 'Integration' | 'Layout' | 'Navigation';

interface PerformanceProfile {
  expectedLatency: number;
  memoryUsage: number;
  cacheability: boolean;
  resourceUsage: 'low' | 'medium' | 'high';
  scalabilityScore: number;
  renderOptimizations: string[];
}

interface ComponentConfiguration {
  defaultProps: Record<string, any>;
  requiredProps: string[];
  optionalProps: string[];
  eventHandlers: string[];
  styling: {
    customizable: boolean;
    themes: string[];
    responsive: boolean;
  };
  dataBinding: {
    supports: boolean;
    types: string[];
    realTime: boolean;
  };
}

interface ValidationRule {
  id: string;
  type: 'required' | 'format' | 'range' | 'custom' | 'performance';
  message: string;
  condition: string;
  severity: 'error' | 'warning' | 'info';
}

// Performance-optimized component preview
const ComponentPreview = memo<{ component: NoCodeComponent; isSelected: boolean }>(({ component, isSelected }) => {
  const { validateHash } = useConstitutionalValidation({
    component: 'component-preview',
    action: 'render',
  });

  const previewStyle = useMemo(() => ({
    transform: isSelected ? 'scale(1.05)' : 'scale(1)',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
    boxShadow: isSelected 
      ? '0 8px 25px rgba(0, 0, 0, 0.15)' 
      : '0 2px 10px rgba(0, 0, 0, 0.1)',
  }), [isSelected]);

  const performanceIndicator = useMemo(() => {
    const latency = component.performanceProfile.expectedLatency;
    if (latency < 2) return { color: '#10B981', text: 'Ultra Fast' };
    if (latency < 5) return { color: '#F59E0B', text: 'Fast' };
    return { color: '#EF4444', text: 'Needs Optimization' };
  }, [component.performanceProfile.expectedLatency]);

  return (
    <div 
      className="component-preview p-4 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-blue-300 transition-colors"
      style={previewStyle}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <span className="text-2xl" role="img" aria-label={component.name}>
            {component.icon}
          </span>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">{component.name}</h3>
            <p className="text-xs text-gray-600">{component.category}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span 
            className="text-xs px-2 py-1 rounded-full text-white font-medium"
            style={{ backgroundColor: performanceIndicator.color }}
          >
            {component.performanceProfile.expectedLatency}ms
          </span>
          <span className="text-xs text-gray-500">
            {component.difficulty.charAt(0).toUpperCase()}
          </span>
        </div>
      </div>
      
      <p className="text-xs text-gray-600 mb-3 line-clamp-2">{component.description}</p>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {component.tags.slice(0, 2).map(tag => (
            <span key={tag} className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
              {tag}
            </span>
          ))}
        </div>
        <div className="flex items-center space-x-1 text-xs text-gray-500">
          <span>❤️</span>
          <span>{component.popularity}</span>
        </div>
      </div>
      
      {/* Constitutional compliance indicator */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500">Constitutional Hash:</span>
          <span className="font-mono text-green-600">
            {component.constitutionalHash.substring(0, 8)}...
          </span>
        </div>
      </div>
    </div>
  );
});

ComponentPreview.displayName = 'ComponentPreview';

// Performance-optimized component library
export const ComponentLibrary: React.FC<ComponentLibraryProps> = memo(({ 
  onComponentSelect, 
  filter = '', 
  category,
  performanceMode = 'optimized' 
}) => {
  const { metrics, isConstitutionallyCompliant } = useConstitutionalValidation({
    component: 'component-library',
    action: 'browse',
    preloadCommonValidations: true,
  });

  // Component library data with performance optimizations
  const componentLibrary = useMemo<NoCodeComponent[]>(() => [
    {
      id: 'advanced-form-builder',
      name: 'Advanced Form Builder',
      type: 'form',
      category: 'Data Input',
      icon: '📝',
      description: 'Drag-and-drop form builder with advanced validation, conditional logic, and real-time validation.',
      tags: ['forms', 'validation', 'interactive', 'responsive'],
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 1.8,
        memoryUsage: 2048,
        cacheability: true,
        resourceUsage: 'low',
        scalabilityScore: 95,
        renderOptimizations: ['virtual-scrolling', 'lazy-validation', 'memoization'],
      },
      configuration: {
        defaultProps: {
          theme: 'modern',
          validation: 'client-side',
          responsive: true,
        },
        requiredProps: ['fields'],
        optionalProps: ['theme', 'validation', 'onSubmit', 'layout'],
        eventHandlers: ['onSubmit', 'onChange', 'onValidate'],
        styling: {
          customizable: true,
          themes: ['modern', 'classic', 'minimal'],
          responsive: true,
        },
        dataBinding: {
          supports: true,
          types: ['json', 'api', 'database'],
          realTime: true,
        },
      },
      renderComponent: lazy(() => import('./components/AdvancedFormBuilder')),
      previewComponent: lazy(() => import('./components/AdvancedFormBuilderPreview')),
      validationRules: [
        {
          id: 'fields-required',
          type: 'required',
          message: 'At least one field is required',
          condition: 'fields.length > 0',
          severity: 'error',
        },
        {
          id: 'performance-check',
          type: 'performance',
          message: 'Form should render in under 2ms',
          condition: 'renderTime < 2',
          severity: 'warning',
        },
      ],
      dependencies: ['react', 'react-hook-form', 'yup'],
      version: '2.1.0',
      lastUpdated: '2025-07-18',
      popularity: 98,
      difficulty: 'intermediate',
      estimatedRenderTime: 1.8,
    },
    {
      id: 'real-time-dashboard',
      name: 'Real-time Dashboard',
      type: 'chart',
      category: 'Visualization',
      icon: '📊',
      description: 'High-performance dashboard with real-time data updates, interactive charts, and customizable widgets.',
      tags: ['dashboard', 'real-time', 'charts', 'analytics'],
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 2.5,
        memoryUsage: 4096,
        cacheability: true,
        resourceUsage: 'medium',
        scalabilityScore: 88,
        renderOptimizations: ['canvas-rendering', 'data-streaming', 'incremental-updates'],
      },
      configuration: {
        defaultProps: {
          updateInterval: 1000,
          maxDataPoints: 1000,
          theme: 'dark',
        },
        requiredProps: ['dataSource'],
        optionalProps: ['updateInterval', 'theme', 'widgets', 'layout'],
        eventHandlers: ['onDataUpdate', 'onWidgetInteraction', 'onExport'],
        styling: {
          customizable: true,
          themes: ['dark', 'light', 'corporate'],
          responsive: true,
        },
        dataBinding: {
          supports: true,
          types: ['websocket', 'sse', 'polling'],
          realTime: true,
        },
      },
      renderComponent: ChartComponent,
      previewComponent: lazy(() => import('./components/DashboardPreview')),
      validationRules: [
        {
          id: 'data-source-required',
          type: 'required',
          message: 'Data source is required',
          condition: 'dataSource !== null',
          severity: 'error',
        },
        {
          id: 'update-interval-range',
          type: 'range',
          message: 'Update interval should be between 100ms and 60s',
          condition: 'updateInterval >= 100 && updateInterval <= 60000',
          severity: 'warning',
        },
      ],
      dependencies: ['react', 'recharts', 'socket.io-client'],
      version: '3.0.2',
      lastUpdated: '2025-07-18',
      popularity: 95,
      difficulty: 'advanced',
      estimatedRenderTime: 2.5,
    },
    {
      id: 'smart-data-table',
      name: 'Smart Data Table',
      type: 'table',
      category: 'Data Display',
      icon: '📋',
      description: 'High-performance data table with virtual scrolling, advanced filtering, sorting, and export capabilities.',
      tags: ['table', 'data', 'filtering', 'sorting', 'export'],
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 1.5,
        memoryUsage: 3072,
        cacheability: true,
        resourceUsage: 'low',
        scalabilityScore: 92,
        renderOptimizations: ['virtual-scrolling', 'row-virtualization', 'column-virtualization'],
      },
      configuration: {
        defaultProps: {
          pageSize: 100,
          virtualScrolling: true,
          sortable: true,
          filterable: true,
        },
        requiredProps: ['columns', 'data'],
        optionalProps: ['pageSize', 'sortable', 'filterable', 'exportable'],
        eventHandlers: ['onSort', 'onFilter', 'onRowSelect', 'onExport'],
        styling: {
          customizable: true,
          themes: ['standard', 'compact', 'comfortable'],
          responsive: true,
        },
        dataBinding: {
          supports: true,
          types: ['json', 'csv', 'api'],
          realTime: true,
        },
      },
      renderComponent: DataTableComponent,
      previewComponent: lazy(() => import('./components/DataTablePreview')),
      validationRules: [
        {
          id: 'columns-required',
          type: 'required',
          message: 'At least one column is required',
          condition: 'columns.length > 0',
          severity: 'error',
        },
        {
          id: 'page-size-range',
          type: 'range',
          message: 'Page size should be between 10 and 1000',
          condition: 'pageSize >= 10 && pageSize <= 1000',
          severity: 'warning',
        },
      ],
      dependencies: ['react', 'react-table', 'react-window'],
      version: '4.2.1',
      lastUpdated: '2025-07-18',
      popularity: 89,
      difficulty: 'intermediate',
      estimatedRenderTime: 1.5,
    },
    {
      id: 'visual-workflow-designer',
      name: 'Visual Workflow Designer',
      type: 'workflow',
      category: 'Automation',
      icon: '🔄',
      description: 'Intuitive workflow designer with drag-and-drop nodes, conditional logic, and real-time execution monitoring.',
      tags: ['workflow', 'automation', 'nodes', 'logic'],
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 3.2,
        memoryUsage: 5120,
        cacheability: false,
        resourceUsage: 'high',
        scalabilityScore: 75,
        renderOptimizations: ['node-pooling', 'connection-batching', 'render-on-demand'],
      },
      configuration: {
        defaultProps: {
          nodeTypes: ['start', 'end', 'condition', 'action'],
          autoLayout: true,
          realTimeExecution: true,
        },
        requiredProps: ['nodes'],
        optionalProps: ['nodeTypes', 'autoLayout', 'realTimeExecution'],
        eventHandlers: ['onNodeAdd', 'onNodeConnect', 'onExecute', 'onStatusChange'],
        styling: {
          customizable: true,
          themes: ['flow', 'technical', 'business'],
          responsive: true,
        },
        dataBinding: {
          supports: true,
          types: ['json', 'api', 'webhook'],
          realTime: true,
        },
      },
      renderComponent: WorkflowComponent,
      previewComponent: lazy(() => import('./components/WorkflowPreview')),
      validationRules: [
        {
          id: 'start-node-required',
          type: 'required',
          message: 'At least one start node is required',
          condition: 'nodes.some(n => n.type === "start")',
          severity: 'error',
        },
        {
          id: 'end-node-required',
          type: 'required',
          message: 'At least one end node is required',
          condition: 'nodes.some(n => n.type === "end")',
          severity: 'error',
        },
      ],
      dependencies: ['react', 'react-flow-renderer', 'dagre'],
      version: '1.8.0',
      lastUpdated: '2025-07-18',
      popularity: 82,
      difficulty: 'advanced',
      estimatedRenderTime: 3.2,
    },
    {
      id: 'api-integration-hub',
      name: 'API Integration Hub',
      type: 'api',
      category: 'Integration',
      icon: '🔗',
      description: 'Comprehensive API integration component with authentication, rate limiting, and real-time monitoring.',
      tags: ['api', 'integration', 'auth', 'monitoring'],
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 4.5,
        memoryUsage: 2048,
        cacheability: true,
        resourceUsage: 'medium',
        scalabilityScore: 85,
        renderOptimizations: ['request-batching', 'response-caching', 'connection-pooling'],
      },
      configuration: {
        defaultProps: {
          authentication: 'bearer',
          rateLimiting: true,
          caching: true,
        },
        requiredProps: ['endpoint', 'method'],
        optionalProps: ['authentication', 'headers', 'rateLimiting', 'caching'],
        eventHandlers: ['onRequest', 'onResponse', 'onError', 'onRateLimit'],
        styling: {
          customizable: false,
          themes: ['api'],
          responsive: true,
        },
        dataBinding: {
          supports: true,
          types: ['json', 'xml', 'form-data'],
          realTime: true,
        },
      },
      renderComponent: lazy(() => import('./components/ApiIntegrationHub')),
      previewComponent: lazy(() => import('./components/ApiIntegrationPreview')),
      validationRules: [
        {
          id: 'endpoint-required',
          type: 'required',
          message: 'API endpoint is required',
          condition: 'endpoint !== ""',
          severity: 'error',
        },
        {
          id: 'method-valid',
          type: 'format',
          message: 'HTTP method must be valid',
          condition: '["GET", "POST", "PUT", "DELETE", "PATCH"].includes(method)',
          severity: 'error',
        },
      ],
      dependencies: ['react', 'axios', 'react-query'],
      version: '2.3.0',
      lastUpdated: '2025-07-18',
      popularity: 91,
      difficulty: 'intermediate',
      estimatedRenderTime: 4.5,
    },
  ], []);

  // Filtered components with performance optimization
  const filteredComponents = useMemo(() => {
    let filtered = componentLibrary;
    
    if (filter) {
      const searchTerm = filter.toLowerCase();
      filtered = filtered.filter(component => 
        component.name.toLowerCase().includes(searchTerm) ||
        component.description.toLowerCase().includes(searchTerm) ||
        component.tags.some(tag => tag.toLowerCase().includes(searchTerm))
      );
    }
    
    if (category) {
      filtered = filtered.filter(component => component.category === category);
    }
    
    // Sort by performance and popularity
    return filtered.sort((a, b) => {
      if (performanceMode === 'ultra') {
        return a.performanceProfile.expectedLatency - b.performanceProfile.expectedLatency;
      }
      return b.popularity - a.popularity;
    });
  }, [componentLibrary, filter, category, performanceMode]);

  // Component selection handler
  const handleComponentSelect = useCallback((component: NoCodeComponent) => {
    const startTime = performance.now();
    
    // Validate constitutional compliance
    if (component.constitutionalHash !== CONFIG.constitutional.hash) {
      console.error('Constitutional compliance violation');
      return;
    }
    
    onComponentSelect?.(component);
    
    // Performance tracking
    const duration = performance.now() - startTime;
    if (duration > 1) {
      console.warn(`Component selection took ${duration.toFixed(2)}ms`);
    }
  }, [onComponentSelect]);

  // Categories for filtering
  const categories = useMemo(() => {
    const categorySet = new Set(componentLibrary.map(c => c.category));
    return Array.from(categorySet).sort();
  }, [componentLibrary]);

  // Performance statistics
  const performanceStats = useMemo(() => {
    const components = filteredComponents;
    const avgLatency = components.reduce((sum, c) => sum + c.performanceProfile.expectedLatency, 0) / components.length;
    const fastComponents = components.filter(c => c.performanceProfile.expectedLatency < 2).length;
    const optimizedComponents = components.filter(c => c.performanceProfile.renderOptimizations.length > 0).length;
    
    return {
      totalComponents: components.length,
      averageLatency: avgLatency.toFixed(1),
      fastComponents,
      optimizedComponents,
      constitutionalCompliance: components.every(c => c.constitutionalHash === CONFIG.constitutional.hash) ? 100 : 0,
    };
  }, [filteredComponents]);

  return (
    <div className="component-library h-full flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Component Library</h2>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 text-xs rounded ${isConstitutionallyCompliant ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {isConstitutionallyCompliant ? '✅ Compliant' : '❌ Non-compliant'}
            </span>
            <span className="text-xs text-gray-500">
              {filteredComponents.length} components
            </span>
          </div>
        </div>
        
        {/* Performance Stats */}
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div className="text-center">
            <div className="text-sm font-medium text-gray-900">{performanceStats.totalComponents}</div>
            <div className="text-xs text-gray-600">Total</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-medium text-green-600">{performanceStats.averageLatency}ms</div>
            <div className="text-xs text-gray-600">Avg Latency</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-medium text-blue-600">{performanceStats.fastComponents}</div>
            <div className="text-xs text-gray-600">Fast (&lt;2ms)</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-medium text-purple-600">{performanceStats.constitutionalCompliance}%</div>
            <div className="text-xs text-gray-600">Compliant</div>
          </div>
        </div>
        
        {/* Category Filter */}
        <div className="flex items-center space-x-2 overflow-x-auto">
          <button
            onClick={() => onComponentSelect?.(null as any)}
            className={`px-3 py-1 text-xs rounded-full whitespace-nowrap ${
              !category ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => onComponentSelect?.(null as any)}
              className={`px-3 py-1 text-xs rounded-full whitespace-nowrap ${
                category === cat ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>
      
      {/* Components Grid */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {filteredComponents.map((component, index) => (
            <div key={component.id} onClick={() => handleComponentSelect(component)}>
              <Suspense fallback={
                <div className="h-32 bg-gray-100 rounded-lg animate-pulse flex items-center justify-center">
                  <div className="text-gray-400 text-sm">Loading...</div>
                </div>
              }>
                <ComponentPreview 
                  component={component} 
                  isSelected={false}
                />
              </Suspense>
            </div>
          ))}
        </div>
        
        {filteredComponents.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg mb-2">🔍</div>
            <div className="text-gray-500 text-sm">
              No components found matching your criteria
            </div>
          </div>
        )}
      </div>
      
      {/* Performance Footer */}
      <div className="flex-shrink-0 p-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <div className="flex items-center space-x-4">
            <span>Render Time: {metrics.averageLatency.toFixed(1)}ms</span>
            <span>Cache Hit: {metrics.cacheHitRate.toFixed(1)}%</span>
            <span>Mode: {performanceMode}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Constitutional Hash:</span>
            <span className="font-mono text-green-600">
              {CONFIG.constitutional.hash.substring(0, 8)}...
            </span>
          </div>
        </div>
      </div>
    </div>
  );
});

ComponentLibrary.displayName = 'ComponentLibrary';

export default ComponentLibrary;
