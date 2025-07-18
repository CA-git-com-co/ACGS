'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  HomeIcon, 
  CogIcon, 
  UsersIcon, 
  ClipboardDocumentListIcon,
  ChartBarIcon,
  CommandLineIcon,
  BookOpenIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useConstitutionalCompliance } from '@/hooks/useConstitutionalCompliance';

const navigationItems = [
  {
    name: 'Overview',
    href: '/dashboard',
    icon: HomeIcon,
    description: 'System overview and status'
  },
  {
    name: 'Multi-Agent',
    href: '/dashboard?tab=agents',
    icon: UsersIcon,
    description: 'Agent workflows and coordination'
  },
  {
    name: 'Knowledge',
    href: '/dashboard?tab=knowledge',
    icon: BookOpenIcon,
    description: 'Blackboard and knowledge sharing'
  },
  {
    name: 'Review Queue',
    href: '/dashboard?tab=review',
    icon: ClipboardDocumentListIcon,
    description: 'Human oversight and approvals'
  },
  {
    name: 'Performance',
    href: '/dashboard?tab=performance',
    icon: ChartBarIcon,
    description: 'Metrics and monitoring'
  },
  {
    name: 'CLI Interface',
    href: '/dashboard?tab=cli',
    icon: CommandLineIcon,
    description: 'Command-line operations'
  },
  {
    name: 'Services',
    href: '/services',
    icon: CogIcon,
    description: 'Service management'
  }
];

export function MainNavigation() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { isCompliant, complianceRate } = useConstitutionalCompliance();

  return (
    <nav className={`bg-white border-r border-gray-200 transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          {!isCollapsed && (
            <div className="flex items-center space-x-2">
              <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-lg font-semibold text-gray-900">ACGS-2</h1>
                <p className="text-xs text-gray-500">Constitutional AI</p>
              </div>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2"
          >
            {isCollapsed ? '→' : '←'}
          </Button>
        </div>

        {/* Constitutional Status */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {!isCollapsed && (
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Constitutional Status</p>
                <p className="text-xs text-gray-500">Hash: cdd01ef066bc6cf2</p>
              </div>
            )}
            <Badge variant={isCompliant ? 'default' : 'destructive'} className="text-xs">
              {isCompliant ? '✓' : '✗'} {complianceRate}%
            </Badge>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto">
          <nav className="p-2 space-y-1">
            {navigationItems.map((item) => {
              const isActive = pathname === item.href.split('?')[0];
              const Icon = item.icon;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-700'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
                  {!isCollapsed && (
                    <div className="flex-1">
                      <div className="font-medium">{item.name}</div>
                      <div className="text-xs text-gray-500">{item.description}</div>
                    </div>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          {!isCollapsed && (
            <div className="text-xs text-gray-500">
              <div className="flex items-center justify-between">
                <span>Version 2.0.0</span>
                <Badge variant="outline" className="text-xs">
                  Production
                </Badge>
              </div>
              <div className="mt-2">
                <p suppressHydrationWarning>Last updated: {new Date().toLocaleDateString()}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}