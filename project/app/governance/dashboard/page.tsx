import { Suspense } from 'react';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth/config';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { PolicySummary } from '@/components/dashboard/PolicySummary';
import { AmendmentSummary } from '@/components/dashboard/AmendmentSummary';  
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { ConstitutionalHealth } from '@/components/dashboard/ConstitutionalHealth';
import { LoadingSkeleton } from '@/components/ui/loading-skeleton';

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    return null;
  }

  return (
    <div className="space-y-6">
      <DashboardHeader user={session.user} />
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Suspense fallback={<LoadingSkeleton className="h-32" />}>
          <PolicySummary />
        </Suspense>
        
        <Suspense fallback={<LoadingSkeleton className="h-32" />}>
          <AmendmentSummary />
        </Suspense>
        
        <Suspense fallback={<LoadingSkeleton className="h-32" />}>
          <ConstitutionalHealth />
        </Suspense>
        
        <Suspense fallback={<LoadingSkeleton className="h-32" />}>
          <RecentActivity />
        </Suspense>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Suspense fallback={<LoadingSkeleton className="h-96" />}>
          <PolicySummaryChart />
        </Suspense>
        
        <Suspense fallback={<LoadingSkeleton className="h-96" />}>
          <AmendmentProgressChart />
        </Suspense>
      </div>
    </div>
  );
}

async function PolicySummaryChart() {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 100));
  
  return (
    <div className="rounded-lg border bg-card p-6">
      <h3 className="text-lg font-semibold mb-4">Policy Activity</h3>
      <div className="h-64 flex items-center justify-center text-muted-foreground">
        Policy activity chart will be rendered here
      </div>
    </div>
  );
}

async function AmendmentProgressChart() {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 100));
  
  return (
    <div className="rounded-lg border bg-card p-6">
      <h3 className="text-lg font-semibold mb-4">Amendment Progress</h3>
      <div className="h-64 flex items-center justify-center text-muted-foreground">
        Amendment progress chart will be rendered here
      </div>
    </div>
  );
}