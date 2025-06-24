import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Activity, ArrowUpRight } from 'lucide-react';

export async function RecentActivity() {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 250));
  
  const activityCount = 28;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Recent Activity
        </CardTitle>
        <Activity className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{activityCount}</div>
        <p className="text-xs text-muted-foreground">
          <span className="inline-flex items-center text-blue-600">
            <ArrowUpRight className="mr-1 h-3 w-3" />
            View all activities
          </span>
        </p>
      </CardContent>
    </Card>
  );
}