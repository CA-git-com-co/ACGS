import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Shield, CheckCircle } from 'lucide-react';

export async function ConstitutionalHealth() {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 200));
  
  const healthScore = 94;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Constitutional Health
        </CardTitle>
        <Shield className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{healthScore}%</div>
        <p className="text-xs text-muted-foreground">
          <span className="inline-flex items-center text-green-600">
            <CheckCircle className="mr-1 h-3 w-3" />
            All systems operational
          </span>
        </p>
      </CardContent>
    </Card>
  );
}