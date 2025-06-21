import { DashboardCards } from '@/components/dashboard/DashboardCards';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-large-heading font-bold text-gray-900 dark:text-gray-100">
          Welcome back
        </h1>
        <p className="text-subheading text-gray-500 dark:text-gray-400 mt-2">
          Here's what's happening with your governance system today.
        </p>
      </div>

      <DashboardCards />
    </div>
  );
}
