import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { MessageSquare, Send } from 'lucide-react';

interface PolicyCommentsProps {
  policyId: string;
}

export async function PolicyComments({ policyId }: PolicyCommentsProps) {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 150));

  const comments = [
    {
      id: '1',
      author: 'Sarah Johnson',
      role: 'Legal Advisor',
      content:
        'The implementation timeline seems reasonable, but we should consider the impact on existing systems during Phase 2.',
      timestamp: '2025-01-15 14:30',
      avatar: '/avatar1.jpg',
    },
    {
      id: '2',
      author: 'Michael Chen',
      role: 'Technical Lead',
      content:
        'From a technical perspective, the data minimization principle will require significant changes to our current data collection practices.',
      timestamp: '2025-01-15 15:45',
      avatar: '/avatar2.jpg',
    },
    {
      id: '3',
      author: 'Emma Williams',
      role: 'Compliance Officer',
      content:
        'We need to ensure that the enforcement mechanisms are clearly defined and practical for implementation.',
      timestamp: '2025-01-16 09:15',
      avatar: '/avatar3.jpg',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Comments ({comments.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Comments List */}
        <div className="space-y-4">
          {comments.map(comment => (
            <div key={comment.id} className="flex gap-3">
              <Avatar className="h-8 w-8">
                <AvatarImage src={comment.avatar} alt={comment.author} />
                <AvatarFallback>
                  {comment.author
                    .split(' ')
                    .map(n => n[0])
                    .join('')}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{comment.author}</span>
                  <span className="text-xs text-muted-foreground">{comment.role}</span>
                  <span className="text-xs text-muted-foreground">•</span>
                  <span className="text-xs text-muted-foreground">{comment.timestamp}</span>
                </div>
                <p className="text-sm">{comment.content}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Add Comment */}
        <div className="space-y-3 border-t pt-4">
          <Textarea placeholder="Add a comment..." className="min-h-[80px]" />
          <div className="flex justify-end">
            <Button size="sm">
              <Send className="h-4 w-4 mr-2" />
              Add Comment
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
