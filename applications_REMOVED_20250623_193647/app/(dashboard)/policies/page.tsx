import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Plus } from 'lucide-react';

// Mock data for policies
const policies = [
  {
    id: '1',
    title: 'Data Privacy Policy',
    description: 'Guidelines for handling personal and sensitive data',
    status: 'active' as const,
    category: 'Privacy',
    createdAt: new Date('2024-01-15'),
    author: 'Admin',
  },
  {
    id: '2',
    title: 'Code Review Standards',
    description: 'Required standards and procedures for code reviews',
    status: 'draft' as const,
    category: 'Development',
    createdAt: new Date('2024-01-20'),
    author: 'Tech Lead',
  },
  {
    id: '3',
    title: 'Remote Work Guidelines',
    description: 'Policies and expectations for remote team members',
    status: 'active' as const,
    category: 'HR',
    createdAt: new Date('2024-01-10'),
    author: 'HR Manager',
  },
];

const statusColors = {
  active: 'bg-status-success text-white',
  draft: 'bg-status-warning text-white',
  archived: 'bg-gray-500 text-white',
};

export default function PoliciesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-large-heading font-bold text-gray-900 dark:text-gray-100">
            Policies
          </h1>
          <p className="text-body text-gray-500 dark:text-gray-400 mt-1">
            Manage organizational policies and guidelines
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Policy
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {policies.map((policy) => (
          <Card key={policy.id} className="group">
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="line-clamp-2">{policy.title}</CardTitle>
                <span
                  className={`px-2 py-1 rounded text-caption font-medium ${
                    statusColors[policy.status]
                  }`}
                >
                  {policy.status}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-body text-gray-600 dark:text-gray-300 mb-4 line-clamp-3">
                {policy.description}
              </p>
              <div className="space-y-2 text-caption text-gray-500 dark:text-gray-400">
                <div className="flex justify-between">
                  <span>Category:</span>
                  <span>{policy.category}</span>
                </div>
                <div className="flex justify-between">
                  <span>Author:</span>
                  <span>{policy.author}</span>
                </div>
                <div className="flex justify-between">
                  <span>Created:</span>
                  <span>{policy.createdAt.toLocaleDateString()}</span>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    View
                  </Button>
                  <Button variant="ghost" size="sm" className="flex-1">
                    Edit
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
