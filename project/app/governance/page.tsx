import { Suspense } from 'react';
import { PolicyCard, Spinner } from '@/lib/shared';

export default function GovernancePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Governance Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">
          Manage constitutional amendments, policy synthesis, and autonomous council operations
        </p>
      </div>

      <Suspense fallback={<Spinner />}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Policy Overview */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold mb-4">Active Policies</h2>
            <PolicyCard
              policy={{
                id: 'demo-policy',
                name: 'Democratic Participation Framework',
                description:
                  'Establishes guidelines for citizen engagement in governance processes',
                rules: [],
                validationScore: 95,
                complianceComplexity: 30,
                status: 'active' as const,
                category: 'governance',
                createdAt: new Date(),
                updatedAt: new Date(),
                author: 'system',
              }}
            />
          </div>

          {/* Welcome Message */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold mb-4">Welcome to ACGS</h2>
            <p className="text-gray-600 dark:text-gray-300">
              The Autonomous Constitutional Governance System provides a comprehensive platform for
              managing democratic processes, policy synthesis, and constitutional compliance.
            </p>
          </div>
        </div>
      </Suspense>
    </div>
  );
}
