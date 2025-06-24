import { Suspense } from 'react';
import { PolicyList } from '@/components/governance/PolicyList';
import { PolicyFilters } from '@/components/governance/PolicyFilters';
import { PolicyHeader } from '@/components/governance/PolicyHeader';
import { LoadingSkeleton } from '@/components/ui/loading-skeleton';

export default function PoliciesPage({
  searchParams,
}: {
  searchParams: { status?: string; domain?: string; search?: string };
}) {
  return (
    <div className="space-y-6">
      <PolicyHeader />
      
      <div className="flex gap-6">
        <aside className="w-64 space-y-4">
          <PolicyFilters />
        </aside>
        
        <main className="flex-1">
          <Suspense fallback={<LoadingSkeleton count={6} className="h-24" />}>
            <PolicyList filters={searchParams} />
          </Suspense>
        </main>
      </div>
    </div>
  );
}