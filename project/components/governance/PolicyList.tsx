import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye, Edit, MoreHorizontal } from 'lucide-react';
import Link from 'next/link';

interface PolicyFilters {
  status?: string;
  domain?: string;
  search?: string;
}

interface PolicyListProps {
  filters: PolicyFilters;
}

export async function PolicyList({ filters }: PolicyListProps) {
  // Simulate data fetching with filters
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Mock policy data
  const policies = [
    {
      id: '1',
      title: 'Data Privacy Protection Act',
      description: 'Comprehensive framework for protecting citizen data privacy and establishing rights for data subjects.',
      status: 'ACTIVE',
      domain: 'PRIVACY',
      lastModified: '2025-01-15',
      author: 'Privacy Committee',
    },
    {
      id: '2',
      title: 'Renewable Energy Transition Policy',
      description: 'Strategic policy for transitioning to renewable energy sources by 2030.',
      status: 'DRAFT',
      domain: 'ENVIRONMENT',
      lastModified: '2025-01-14',
      author: 'Environmental Council',
    },
    {
      id: '3',
      title: 'Digital Identity Framework',
      description: 'Establishing secure digital identity standards for all citizens.',
      status: 'REVIEW',
      domain: 'DIGITAL',
      lastModified: '2025-01-13',
      author: 'Digital Affairs Ministry',
    },
    {
      id: '4',
      title: 'Healthcare Access Reform',
      description: 'Improving healthcare accessibility and quality across all regions.',
      status: 'ACTIVE',
      domain: 'HEALTHCARE',
      lastModified: '2025-01-12',
      author: 'Health Committee',
    },
    {
      id: '5',
      title: 'Educational Technology Integration',
      description: 'Guidelines for integrating technology in educational institutions.',
      status: 'PENDING',
      domain: 'EDUCATION',
      lastModified: '2025-01-11',
      author: 'Education Board',
    },
    {
      id: '6',
      title: 'Transport Infrastructure Development',
      description: 'Long-term plan for sustainable transport infrastructure.',
      status: 'ACTIVE',
      domain: 'TRANSPORT',
      lastModified: '2025-01-10',
      author: 'Infrastructure Committee',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-100 text-green-800';
      case 'DRAFT':
        return 'bg-gray-100 text-gray-800';
      case 'REVIEW':
        return 'bg-yellow-100 text-yellow-800';
      case 'PENDING':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDomainColor = (domain: string) => {
    switch (domain) {
      case 'PRIVACY':
        return 'bg-blue-100 text-blue-800';
      case 'ENVIRONMENT':
        return 'bg-green-100 text-green-800';
      case 'DIGITAL':
        return 'bg-purple-100 text-purple-800';
      case 'HEALTHCARE':
        return 'bg-red-100 text-red-800';
      case 'EDUCATION':
        return 'bg-indigo-100 text-indigo-800';
      case 'TRANSPORT':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      {policies.map((policy) => (
        <Card key={policy.id} className="hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="space-y-2 flex-1">
                <CardTitle className="text-xl">{policy.title}</CardTitle>
                <p className="text-muted-foreground">{policy.description}</p>
                <div className="flex items-center gap-2">
                  <Badge className={getStatusColor(policy.status)}>
                    {policy.status}
                  </Badge>
                  <Badge variant="outline" className={getDomainColor(policy.domain)}>
                    {policy.domain}
                  </Badge>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Link href={`/governance/policies/${policy.id}`}>
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-2" />
                    View
                  </Button>
                </Link>
                <Button variant="outline" size="sm">
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>Author: {policy.author}</span>
              <span>Last modified: {policy.lastModified}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}