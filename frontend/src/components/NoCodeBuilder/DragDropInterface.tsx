/**
 * No-Code Drag & Drop Interface
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Advanced drag-and-drop interface for no-code application building
 * with constitutional compliance and performance optimization.
 */

import React, { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import { useConstitutionalValidation } from '@/hooks/useConstitutionalValidation';
import { CONFIG } from '@/config';
import { motion, AnimatePresence } from 'framer-motion';

// Types
interface DraggableComponent {
  id: string;
  type: 'form' | 'chart' | 'table' | 'workflow' | 'api';
  name: string;
  icon: string;
  category: string;
  constitutionalHash: string;
  performanceProfile: {
    expectedLatency: number;
    cacheability: boolean;
    resourceUsage: 'low' | 'medium' | 'high';
  };
  configuration: Record<string, any>;
  validationRules: ValidationRule[];
}

interface ValidationRule {
  id: string;
  type: 'required' | 'format' | 'range' | 'custom';
  message: string;
  condition: string;
}

interface DropZone {
  id: string;
  name: string;
  accepts: string[];
  position: { x: number; y: number; width: number; height: number };
  isActive: boolean;
  components: DraggableComponent[];
}

interface DragDropState {
  draggedComponent: DraggableComponent | null;
  dropZones: DropZone[];
  activeDropZone: string | null;
  dragPosition: { x: number; y: number };
}

/**
 * Drag & Drop Interface Component
 */
export const DragDropInterface: React.FC = () => {
  const [dragState, setDragState] = useState<DragDropState>({
    draggedComponent: null,
    dropZones: [
      {
        id: 'main-canvas',
        name: 'Main Canvas',
        accepts: ['form', 'chart', 'table', 'workflow', 'api'],
        position: { x: 250, y: 100, width: 800, height: 600 },
        isActive: false,
        components: [],
      },
      {
        id: 'sidebar',
        name: 'Sidebar',
        accepts: ['form', 'chart'],
        position: { x: 1070, y: 100, width: 200, height: 600 },
        isActive: false,
        components: [],
      },
    ],
    activeDropZone: null,
    dragPosition: { x: 0, y: 0 },
  });

  const [selectedComponent, setSelectedComponent] = useState<DraggableComponent | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState({
    totalComponents: 0,
    averageLatency: 0,
    cacheHitRate: 0,
    constitutionalCompliance: 100,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showPerformanceDetails, setShowPerformanceDetails] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);

  const canvasRef = useRef<HTMLDivElement>(null);
  const dragPreviewRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  
  // Animation variants
  const dropZoneVariants = {
    inactive: { 
      scale: 1, 
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      borderColor: '#e5e7eb'
    },
    active: { 
      scale: 1.02, 
      boxShadow: '0 8px 25px rgba(59,130,246,0.15)',
      borderColor: '#3b82f6'
    },
    hover: { 
      scale: 1.01, 
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
    }
  };
  
  const componentVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  };

  // Constitutional validation
  const { validateHash, metrics } = useConstitutionalValidation({
    component: 'drag-drop-interface',
    action: 'component-manipulation',
    preloadCommonValidations: true,
  });

  // Categories for filtering
  const categories = useMemo(() => {
    const cats = ['all', 'Data Input', 'Visualization', 'Data Display', 'Automation', 'Integration'];
    return cats.map(cat => ({ id: cat, name: cat, count: cat === 'all' ? 5 : 1 }));
  }, []);
  
  // Component library
  const componentLibrary: DraggableComponent[] = useMemo(() => [
    {
      id: 'form-builder',
      type: 'form',
      name: 'Form Builder',
      icon: '📝',
      category: 'Data Input',
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 2,
        cacheability: true,
        resourceUsage: 'low',
      },
      configuration: {
        fields: [],
        validation: 'client-side',
        theme: 'default',
      },
      validationRules: [
        {
          id: 'required-fields',
          type: 'required',
          message: 'At least one field is required',
          condition: 'fields.length > 0',
        },
      ],
    },
    {
      id: 'data-chart',
      type: 'chart',
      name: 'Data Chart',
      icon: '📊',
      category: 'Visualization',
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 3,
        cacheability: true,
        resourceUsage: 'medium',
      },
      configuration: {
        chartType: 'bar',
        dataSource: null,
        refreshInterval: 30000,
      },
      validationRules: [
        {
          id: 'data-source-required',
          type: 'required',
          message: 'Data source is required',
          condition: 'dataSource !== null',
        },
      ],
    },
    {
      id: 'data-table',
      type: 'table',
      name: 'Data Table',
      icon: '📋',
      category: 'Data Display',
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 4,
        cacheability: true,
        resourceUsage: 'medium',
      },
      configuration: {
        columns: [],
        pagination: true,
        sorting: true,
        filtering: true,
      },
      validationRules: [
        {
          id: 'columns-required',
          type: 'required',
          message: 'At least one column is required',
          condition: 'columns.length > 0',
        },
      ],
    },
    {
      id: 'workflow-automation',
      type: 'workflow',
      name: 'Workflow',
      icon: '🔄',
      category: 'Automation',
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 5,
        cacheability: false,
        resourceUsage: 'high',
      },
      configuration: {
        triggers: [],
        actions: [],
        conditions: [],
      },
      validationRules: [
        {
          id: 'trigger-required',
          type: 'required',
          message: 'At least one trigger is required',
          condition: 'triggers.length > 0',
        },
      ],
    },
    {
      id: 'api-integration',
      type: 'api',
      name: 'API Integration',
      icon: '🔗',
      category: 'Integration',
      constitutionalHash: CONFIG.constitutional.hash,
      performanceProfile: {
        expectedLatency: 10,
        cacheability: true,
        resourceUsage: 'medium',
      },
      configuration: {
        endpoint: '',
        method: 'GET',
        headers: {},
        authentication: 'none',
      },
      validationRules: [
        {
          id: 'endpoint-required',
          type: 'required',
          message: 'API endpoint is required',
          condition: 'endpoint !== ""',
        },
      ],
    },
  ], []);
  
  // Filtered components based on search and category
  const filteredComponents = useMemo(() => {
    let filtered = componentLibrary;
    
    if (searchTerm) {
      filtered = filtered.filter(comp => 
        comp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        comp.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(comp => comp.category === selectedCategory);
    }
    
    return filtered;
  }, [componentLibrary, searchTerm, selectedCategory]);
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'f':
            e.preventDefault();
            searchInputRef.current?.focus();
            break;
          case '=':
            e.preventDefault();
            setZoomLevel(prev => Math.min(prev + 0.1, 2));
            break;
          case '-':
            e.preventDefault();
            setZoomLevel(prev => Math.max(prev - 0.1, 0.5));
            break;
        }
      }
      if (e.key === 'Escape') {
        setSelectedComponent(null);
        setSearchTerm('');
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Drag handlers
  const handleDragStart = useCallback((component: DraggableComponent, event: React.DragEvent<HTMLDivElement>) => {
    const startTime = performance.now();
    
    // Validate constitutional compliance
    if (component.constitutionalHash !== CONFIG.constitutional.hash) {
      event.preventDefault();
      alert('Constitutional compliance violation detected!');
      return;
    }

    setDragState(prev => ({
      ...prev,
      draggedComponent: component,
      dragPosition: { x: event.clientX, y: event.clientY },
    }));

    // Set drag data
    event.dataTransfer.setData('application/json', JSON.stringify(component));
    event.dataTransfer.effectAllowed = 'copy';

    // Performance tracking
    const duration = performance.now() - startTime;
    if (duration > 1) {
      console.warn(`Drag start took ${duration.toFixed(2)}ms - optimizing needed`);
    }
  }, []);

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';

    // Update drag position
    setDragState(prev => ({
      ...prev,
      dragPosition: { x: event.clientX, y: event.clientY },
    }));

    // Determine active drop zone
    const rect = canvasRef.current?.getBoundingClientRect();
    if (rect) {
      const relativeX = event.clientX - rect.left;
      const relativeY = event.clientY - rect.top;
      
      const activeZone = dragState.dropZones.find(zone => 
        relativeX >= zone.position.x &&
        relativeX <= zone.position.x + zone.position.width &&
        relativeY >= zone.position.y &&
        relativeY <= zone.position.y + zone.position.height
      );

      setDragState(prev => ({
        ...prev,
        activeDropZone: activeZone?.id || null,
      }));
    }
  }, [dragState.dropZones]);

  const handleDrop = useCallback(async (event: React.DragEvent) => {
    event.preventDefault();
    const startTime = performance.now();

    try {
      const componentData = event.dataTransfer.getData('application/json');
      const component: DraggableComponent = JSON.parse(componentData);

      // Validate constitutional compliance
      const isValid = await validateHash(component.constitutionalHash);
      if (!isValid) {
        alert('Constitutional compliance validation failed!');
        return;
      }

      if (dragState.activeDropZone) {
        // Create new component instance
        const newComponent: DraggableComponent = {
          ...component,
          id: `${component.id}-${Date.now()}`,
          configuration: { ...component.configuration },
        };

        // Add to drop zone
        setDragState(prev => ({
          ...prev,
          dropZones: prev.dropZones.map(zone => 
            zone.id === dragState.activeDropZone
              ? { ...zone, components: [...zone.components, newComponent] }
              : zone
          ),
          draggedComponent: null,
          activeDropZone: null,
        }));

        // Update performance metrics
        setPerformanceMetrics(prev => ({
          ...prev,
          totalComponents: prev.totalComponents + 1,
          averageLatency: (prev.averageLatency + component.performanceProfile.expectedLatency) / 2,
        }));

        // Log action for audit
        console.log(`Component ${component.name} added to ${dragState.activeDropZone}`);
      }
    } catch (error) {
      console.error('Drop operation failed:', error);
    } finally {
      const duration = performance.now() - startTime;
      if (duration > CONFIG.performance.latencyP99Target) {
        console.warn(`Drop operation took ${duration.toFixed(2)}ms - exceeds target`);
      }
    }
  }, [dragState.activeDropZone, validateHash]);

  const handleDragEnd = useCallback(() => {
    setDragState(prev => ({
      ...prev,
      draggedComponent: null,
      activeDropZone: null,
    }));
  }, []);

  // Component selection
  const handleComponentSelect = useCallback((component: DraggableComponent) => {
    setSelectedComponent(component);
  }, []);

  // Performance indicator
  const getPerformanceColor = (latency: number): string => {
    if (latency < CONFIG.performance.latencyP99Target) return 'text-green-600';
    if (latency < CONFIG.performance.latencyP99Target * 2) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className={`flex h-screen transition-colors duration-300 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Enhanced Component Palette */}
      <div className={`w-80 transition-colors duration-300 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r overflow-hidden flex flex-col`}>
        {/* Header with Search */}
        <div className={`p-4 border-b transition-colors duration-300 ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="flex items-center justify-between mb-4">
            <h2 className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Components</h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'}`}
              >
                {isDarkMode ? '🌙' : '☀️'}
              </button>
              <button
                onClick={() => setShowPerformanceDetails(!showPerformanceDetails)}
                className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'}`}
              >
                ⚙️
              </button>
            </div>
          </div>
          
          {/* Search Input */}
          <div className="relative mb-4">
            <span className={`absolute left-3 top-1/2 transform -translate-y-1/2 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>🔍</span>
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search components... (Ctrl+F)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={`w-full pl-10 pr-4 py-2 border rounded-lg transition-colors ${isDarkMode ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            />
          </div>
          
          {/* Category Filters */}
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-3 py-1 text-xs rounded-full transition-colors ${
                  selectedCategory === category.id
                    ? 'bg-blue-500 text-white'
                    : isDarkMode
                    ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.name} {category.id !== 'all' && `(${category.count})`}
              </button>
            ))}
          </div>
          
          {/* Constitutional Hash */}
          <div className={`mt-3 pt-3 border-t text-xs ${isDarkMode ? 'border-gray-700 text-gray-400' : 'border-gray-200 text-gray-600'}`}>
            <div className="flex items-center justify-between">
              <span>Constitutional Hash:</span>
              <span className="font-mono text-green-500">
                {CONFIG.constitutional.hash.substring(0, 8)}...
              </span>
            </div>
          </div>
        </div>
        
        {/* Component List */}
        <div className="flex-1 overflow-y-auto p-4">
          <AnimatePresence>
            <div className="space-y-3">
              {filteredComponents.map((component, index) => (
                <motion.div
                  key={component.id}
                  variants={componentVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ delay: index * 0.05 }}
                  className={`group relative p-4 rounded-xl cursor-grab transition-all duration-200 ${isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-50 hover:bg-white'} hover:shadow-lg border-2 border-transparent hover:border-blue-200`}
                  draggable
                  onDragStart={(e) => handleDragStart(component, e as any)}
                  onDragEnd={handleDragEnd}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <span className="text-3xl">{component.icon}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                        {component.name}
                      </div>
                      <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        {component.category}
                      </div>
                      
                      {/* Performance Indicators */}
                      <div className="mt-2 flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          component.performanceProfile.resourceUsage === 'low' ? 'bg-green-100 text-green-800' :
                          component.performanceProfile.resourceUsage === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {component.performanceProfile.resourceUsage.toUpperCase()}
                        </span>
                        <span className={`text-xs font-medium ${getPerformanceColor(component.performanceProfile.expectedLatency)}`}>
                          {component.performanceProfile.expectedLatency}ms
                        </span>
                        {component.performanceProfile.cacheability && (
                          <span className="text-xs text-blue-600">📦 Cached</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Hover Actions */}
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="flex space-x-1">
                      <button className={`p-1 rounded ${isDarkMode ? 'bg-gray-600 hover:bg-gray-500' : 'bg-white hover:bg-gray-50'} shadow-sm`}>
                        👁️
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </AnimatePresence>
          
          {filteredComponents.length === 0 && (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">🔍</div>
              <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                No components found matching "{searchTerm}"
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Main Canvas */}
      <div className="flex-1 relative flex flex-col" ref={canvasRef}>
        {/* Canvas Toolbar */}
        <div className={`flex items-center justify-between p-4 border-b ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex items-center space-x-4">
            <h1 className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Canvas</h1>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setZoomLevel(prev => Math.max(prev - 0.1, 0.5))}
                className={`px-3 py-1 text-sm rounded ${isDarkMode ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              >
                -
              </button>
              <span className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                {Math.round(zoomLevel * 100)}%
              </span>
              <button
                onClick={() => setZoomLevel(prev => Math.min(prev + 0.1, 2))}
                className={`px-3 py-1 text-sm rounded ${isDarkMode ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              >
                +
              </button>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              {performanceMetrics.totalComponents} components
            </div>
            <div className={`px-3 py-1 text-sm rounded-full ${
              performanceMetrics.constitutionalCompliance === 100
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {performanceMetrics.constitutionalCompliance}% Compliant
            </div>
          </div>
        </div>
        
        {/* Canvas Area */}
        <div 
          className={`flex-1 relative overflow-hidden ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}
          style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {/* Grid Background */}
          <div className="absolute inset-0 opacity-20">
            <svg width="100%" height="100%" className={isDarkMode ? 'text-gray-700' : 'text-gray-300'}>
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>
          </div>
          
          {/* Drop Zones */}
          {dragState.dropZones.map(zone => (
            <motion.div
              key={zone.id}
              className={`absolute border-2 border-dashed rounded-xl backdrop-blur-sm transition-all duration-200 ${
                dragState.activeDropZone === zone.id
                  ? isDarkMode ? 'border-blue-400 bg-blue-500/10' : 'border-blue-500 bg-blue-50'
                  : isDarkMode ? 'border-gray-600 bg-gray-800/50' : 'border-gray-300 bg-white/70'
              }`}
              style={{
                left: zone.position.x,
                top: zone.position.y,
                width: zone.position.width,
                height: zone.position.height,
              }}
              variants={dropZoneVariants}
              animate={dragState.activeDropZone === zone.id ? 'active' : 'inactive'}
              whileHover="hover"
            >
              <div className="p-6 h-full">
                <div className="flex items-center justify-between mb-4">
                  <h3 className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    {zone.name}
                  </h3>
                  <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {zone.components.length} items
                  </div>
                </div>
                
                {zone.components.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-3/4 text-center">
                    <div className="text-6xl mb-4 opacity-50">📦</div>
                    <div className={`text-lg font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Drop components here
                    </div>
                    <div className={`text-sm ${isDarkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                      Drag from the component library
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-3 h-full overflow-y-auto">
                    <AnimatePresence>
                      {zone.components.map((component, index) => (
                        <motion.div
                          key={component.id}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.8 }}
                          transition={{ delay: index * 0.1 }}
                          className={`group relative p-4 rounded-xl cursor-pointer transition-all duration-200 ${isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-white hover:bg-gray-50'} border-2 border-transparent hover:border-blue-300 shadow-sm hover:shadow-md`}
                          onClick={() => handleComponentSelect(component)}
                        >
                          <div className="flex items-start space-x-3">
                            <span className="text-2xl">{component.icon}</span>
                            <div className="flex-1 min-w-0">
                              <div className={`font-semibold truncate ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                                {component.name}
                              </div>
                              <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                {component.performanceProfile.expectedLatency}ms
                              </div>
                            </div>
                          </div>
                          
                          {/* Component Actions */}
                          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <div className="flex space-x-1">
                              <button className={`p-1 rounded ${isDarkMode ? 'bg-gray-600 hover:bg-gray-500' : 'bg-white hover:bg-gray-50'} shadow-sm`}>
                                ⚙️
                              </button>
                              <button className={`p-1 rounded ${isDarkMode ? 'bg-gray-600 hover:bg-gray-500' : 'bg-white hover:bg-gray-50'} shadow-sm`}>
                                🗑️
                              </button>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Enhanced Drag Preview */}
        <AnimatePresence>
          {dragState.draggedComponent && (
            <motion.div
              ref={dragPreviewRef}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className={`fixed pointer-events-none z-50 p-4 rounded-xl shadow-2xl border-2 border-blue-300 ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}
              style={{
                left: dragState.dragPosition.x + 15,
                top: dragState.dragPosition.y + 15,
              }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{dragState.draggedComponent.icon}</span>
                <div>
                  <div className={`font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    {dragState.draggedComponent.name}
                  </div>
                  <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {dragState.draggedComponent.performanceProfile.expectedLatency}ms
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Properties Panel */}
      <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Properties</h2>
        </div>
        
        {selectedComponent ? (
          <div className="p-4 space-y-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Component Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Name:</span>
                  <span className="font-medium">{selectedComponent.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-medium">{selectedComponent.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Category:</span>
                  <span className="font-medium">{selectedComponent.category}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Performance Profile</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Expected Latency:</span>
                  <span className={`font-medium ${getPerformanceColor(selectedComponent.performanceProfile.expectedLatency)}`}>
                    {selectedComponent.performanceProfile.expectedLatency}ms
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Cacheable:</span>
                  <span className="font-medium">
                    {selectedComponent.performanceProfile.cacheability ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Resource Usage:</span>
                  <span className="font-medium">
                    {selectedComponent.performanceProfile.resourceUsage.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Constitutional Compliance</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Hash:</span>
                  <span className="font-mono text-xs">
                    {selectedComponent.constitutionalHash.substring(0, 8)}...
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="font-medium text-green-600">✅ Compliant</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Validation Rules</h3>
              <div className="space-y-2">
                {selectedComponent.validationRules.map(rule => (
                  <div key={rule.id} className="p-2 bg-gray-50 rounded text-sm">
                    <div className="font-medium text-gray-900">{rule.type.toUpperCase()}</div>
                    <div className="text-gray-600">{rule.message}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 text-center text-gray-500">
            Select a component to view its properties
          </div>
        )}
      </div>

      {/* Performance Metrics Footer */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-6">
            <div>
              <span className="text-gray-600">Components: </span>
              <span className="font-medium">{performanceMetrics.totalComponents}</span>
            </div>
            <div>
              <span className="text-gray-600">Avg Latency: </span>
              <span className={`font-medium ${getPerformanceColor(performanceMetrics.averageLatency)}`}>
                {performanceMetrics.averageLatency.toFixed(1)}ms
              </span>
            </div>
            <div>
              <span className="text-gray-600">Cache Hit: </span>
              <span className="font-medium text-green-600">
                {metrics.cacheHitRate.toFixed(1)}%
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">Constitutional Compliance:</span>
            <span className="font-medium text-green-600">
              {performanceMetrics.constitutionalCompliance}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DragDropInterface;
