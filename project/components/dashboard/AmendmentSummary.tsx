import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Gavel, Clock } from 'lucide-react';

export async function AmendmentSummary() {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 150));

  const amendmentStats = {
    inProgress: 7,
    pending: 3,
    completed: 24,
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Amendments in Progress</CardTitle>
        <Gavel className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{amendmentStats.inProgress}</div>
        <p className="text-xs text-muted-foreground">
          <span className="inline-flex items-center text-orange-600">
            <Clock className="mr-1 h-3 w-3" />
            {amendmentStats.pending} pending review
          </span>
        </p>
      </CardContent>
    </Card>
  );
}
