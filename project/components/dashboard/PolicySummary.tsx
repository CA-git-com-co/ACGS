import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { FileText, TrendingUp } from 'lucide-react';

export async function PolicySummary() {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 100));

  const policyStats = {
    total: 142,
    active: 89,
    pending: 23,
    growth: '+12%',
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Active Policies</CardTitle>
        <FileText className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{policyStats.active}</div>
        <p className="text-xs text-muted-foreground">
          <span className="inline-flex items-center text-green-600">
            <TrendingUp className="mr-1 h-3 w-3" />
            {policyStats.growth}
          </span>{' '}
          from last month
        </p>
      </CardContent>
    </Card>
  );
}
