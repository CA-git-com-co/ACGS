import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { PolicyDetail } from '@/components/governance/PolicyDetail';
import { PolicyComments } from '@/components/governance/PolicyComments';
import { PolicyHistory } from '@/components/governance/PolicyHistory';
import { LoadingSkeleton } from '@/components/ui/loading-skeleton';
import { fetchPolicy } from '@/lib/api/policy-service';

interface PolicyPageProps {
  params: { id: string };
}

export default async function PolicyPage({ params }: PolicyPageProps) {
  // Verify policy exists server-side
  try {
    await fetchPolicy(params.id);
  } catch (error) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <Suspense fallback={<LoadingSkeleton className="h-96" />}>
        <PolicyDetail id={params.id} />
      </Suspense>

      <div className="grid gap-6 lg:grid-cols-2">
        <Suspense fallback={<LoadingSkeleton className="h-64" />}>
          <PolicyComments policyId={params.id} />
        </Suspense>

        <Suspense fallback={<LoadingSkeleton className="h-64" />}>
          <PolicyHistory policyId={params.id} />
        </Suspense>
      </div>
    </div>
  );
}
