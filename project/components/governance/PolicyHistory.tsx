import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { History, Edit, Check, X, Clock } from 'lucide-react';

interface PolicyHistoryProps {
  policyId: string;
}

export async function PolicyHistory({ policyId }: PolicyHistoryProps) {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 200));
  
  const historyItems = [
    {
      id: '1',
      action: 'Policy Updated',
      description: 'Updated implementation timeline and added new compliance requirements',
      user: 'Sarah Johnson',
      timestamp: '2025-01-15 14:30',
      version: '2.1',
      type: 'update',
    },
    {
      id: '2',
      action: 'Review Completed',
      description: 'Legal review completed with recommendations incorporated',
      user: 'Legal Committee',
      timestamp: '2025-01-10 16:20',
      version: '2.0',
      type: 'review',
    },
    {
      id: '3',
      action: 'Policy Approved',
      description: 'Policy approved by Constitutional Council',
      user: 'Constitutional Council',
      timestamp: '2025-01-05 11:45',
      version: '2.0',
      type: 'approval',
    },
    {
      id: '4',
      action: 'Amendment Proposed',
      description: 'Proposed changes to data subject rights section',
      user: 'Michael Chen',
      timestamp: '2024-12-28 09:15',
      version: '1.5',
      type: 'amendment',
    },
    {
      id: '5',
      action: 'Policy Created',
      description: 'Initial policy draft created',
      user: 'Privacy Committee',
      timestamp: '2024-12-01 10:00',
      version: '1.0',
      type: 'creation',
    },
  ];

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'update':
        return <Edit className="h-4 w-4 text-blue-600" />;
      case 'review':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'approval':
        return <Check className="h-4 w-4 text-green-600" />;
      case 'amendment':
        return <Edit className="h-4 w-4 text-purple-600" />;
      case 'creation':
        return <History className="h-4 w-4 text-gray-600" />;
      default:
        return <History className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActionColor = (type: string) => {
    switch (type) {
      case 'update':
        return 'bg-blue-100 text-blue-800';
      case 'review':
        return 'bg-yellow-100 text-yellow-800';
      case 'approval':
        return 'bg-green-100 text-green-800';
      case 'amendment':
        return 'bg-purple-100 text-purple-800';
      case 'creation':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5" />
          Policy History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {historyItems.map((item, index) => (
            <div key={item.id} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                  {getActionIcon(item.type)}
                </div>
                {index < historyItems.length - 1 && (
                  <div className="w-px h-6 bg-border mt-2" />
                )}
              </div>
              <div className="flex-1 space-y-2 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{item.action}</span>
                    <Badge variant="outline" className={getActionColor(item.type)}>
                      v{item.version}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-foreground">{item.timestamp}</span>
                </div>
                <p className="text-sm text-muted-foreground">{item.description}</p>
                <div className="flex items-center gap-2">
                  <Avatar className="h-6 w-6">
                    <AvatarFallback className="text-xs">
                      {item.user.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-xs text-muted-foreground">{item.user}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}