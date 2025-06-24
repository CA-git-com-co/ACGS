'use client';

import * as React from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { ThemeToggle } from '@/components/layout/ThemeToggle';
import { CommandBar } from '@/components/layout/CommandBar';
import { useLocalStorage } from '@/hooks/useLocalStorage';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useLocalStorage('sidebar-collapsed', false);

  return (
    <div className="flex h-screen bg-base-light dark:bg-base-dark">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 border-b border-gray-200 dark:border-gray-700 bg-base-white dark:bg-gray-800 flex items-center justify-between px-6">
          <div>
            <p className="text-body text-gray-500 dark:text-gray-400">
              Press{' '}
              <kbd className="px-2 py-1 text-caption bg-gray-100 dark:bg-gray-700 rounded border">
                ⌘K
              </kbd>{' '}
              to open command palette
            </p>
          </div>
          <ThemeToggle />
        </header>

        <div className="flex-1 overflow-auto p-6">{children}</div>
      </main>

      <CommandBar />
    </div>
  );
}
