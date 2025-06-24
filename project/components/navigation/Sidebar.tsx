'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  FileText,
  Gavel,
  Users,
  BarChart3,
  Settings,
  BookOpen,
  Scale,
  Shield,
  Activity,
  Blocks,
} from 'lucide-react';

const sidebarItems = [
  {
    title: 'Dashboard',
    href: '/governance/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Policies',
    href: '/governance/policies',
    icon: FileText,
  },
  {
    title: 'Amendments',
    href: '/governance/amendments',
    icon: Gavel,
  },
  {
    title: 'Constitutional',
    href: '/constitutional',
    icon: Scale,
    submenu: [
      {
        title: 'Principles',
        href: '/constitutional/principles',
        icon: BookOpen,
      },
      {
        title: 'Proposals',
        href: '/constitutional/proposals',
        icon: Gavel,
      },
    ],
  },
  {
    title: 'Blockchain',
    href: '/blockchain',
    icon: Blocks,
  },
  {
    title: 'Monitoring',
    href: '/monitoring',
    icon: Activity,
  },
  {
    title: 'Analytics',
    href: '/governance/analytics',
    icon: BarChart3,
  },
  {
    title: 'Public Consultation',
    href: '/governance/consultation',
    icon: Users,
  },
  {
    title: 'Settings',
    href: '/governance/settings',
    icon: Settings,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 border-r bg-background">
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
            Navigation
          </h2>
          <div className="space-y-1">
            {sidebarItems.map((item) => (
              <div key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center rounded-lg px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors',
                    pathname === item.href
                      ? 'bg-accent text-accent-foreground'
                      : 'transparent'
                  )}
                >
                  <item.icon className="mr-2 h-4 w-4" />
                  {item.title}
                </Link>
                {item.submenu && (
                  <div className="ml-6 mt-1 space-y-1">
                    {item.submenu.map((subItem) => (
                      <Link
                        key={subItem.href}
                        href={subItem.href}
                        className={cn(
                          'flex items-center rounded-lg px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors',
                          pathname === subItem.href
                            ? 'bg-accent text-accent-foreground'
                            : 'transparent'
                        )}
                      >
                        <subItem.icon className="mr-2 h-4 w-4" />
                        {subItem.title}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}