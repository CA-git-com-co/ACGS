'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, FileText, Vote, Settings, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

interface NavItem {
  title: string;
  href: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/',
    icon: <Home className="h-5 w-5" />
  },
  {
    title: 'Policies',
    href: '/policies',
    icon: <FileText className="h-5 w-5" />
  },
  {
    title: 'Governance',
    href: '/governance',
    icon: <Vote className="h-5 w-5" />
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: <Settings className="h-5 w-5" />
  }
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        'flex h-full flex-col border-r border-gray-200 bg-base-white transition-all duration-200 ease-out',
        'dark:border-gray-700 dark:bg-gray-800',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex items-center justify-between p-4">
        {!collapsed && (
          <h1 className="text-heading font-bold text-gray-900 dark:text-gray-100">Governance</h1>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="ml-auto"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map(item => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-body font-medium transition-colors',
                'hover:bg-gray-100 dark:hover:bg-gray-700',
                isActive
                  ? 'bg-accent-primary text-base-white hover:bg-accent-primary-dark'
                  : 'text-gray-600 dark:text-gray-300',
                collapsed && 'justify-center'
              )}
              title={collapsed ? item.title : undefined}
            >
              {item.icon}
              {!collapsed && <span>{item.title}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-accent-primary flex items-center justify-center">
            <span className="text-caption font-medium text-base-white">U</span>
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-body font-medium text-gray-900 dark:text-gray-100 truncate">
                User Name
              </p>
              <p className="text-caption text-gray-500 dark:text-gray-400 truncate">
                user@example.com
              </p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
