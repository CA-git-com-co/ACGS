import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Edit, Archive, Share, Download, Clock, User } from 'lucide-react';

interface PolicyDetailProps {
  id: string;
}

export async function PolicyDetail({ id }: PolicyDetailProps) {
  // Simulate data fetching
  await new Promise(resolve => setTimeout(resolve, 200));
  
  // Mock policy data
  const policy = {
    id,
    title: 'Data Privacy Protection Act',
    description: 'Comprehensive framework for protecting citizen data privacy and establishing rights for data subjects.',
    content: `## Overview

This policy establishes a comprehensive framework for protecting the privacy of personal data belonging to citizens. It defines the rights of data subjects, obligations of data controllers, and enforcement mechanisms to ensure compliance.

## Key Principles

1. **Lawfulness, Fairness, and Transparency**: Personal data shall be processed lawfully, fairly, and in a transparent manner.

2. **Purpose Limitation**: Personal data shall be collected for specified, explicit, and legitimate purposes.

3. **Data Minimization**: Personal data shall be adequate, relevant, and limited to what is necessary.

4. **Accuracy**: Personal data shall be accurate and kept up to date.

5. **Storage Limitation**: Personal data shall be kept in a form that permits identification for no longer than necessary.

## Data Subject Rights

- Right to be informed
- Right of access
- Right to rectification
- Right to erasure
- Right to restrict processing
- Right to data portability
- Right to object
- Rights related to automated decision-making

## Implementation Timeline

The policy shall be implemented in three phases:

1. **Phase 1 (Months 1-6)**: Legal framework establishment
2. **Phase 2 (Months 7-12)**: Systems implementation and staff training
3. **Phase 3 (Months 13-18)**: Full compliance and monitoring

## Compliance and Enforcement

Violations of this policy may result in:
- Administrative fines
- Criminal penalties
- Civil liability
- Regulatory sanctions`,
    status: 'ACTIVE',
    domain: 'PRIVACY',
    author: 'Privacy Committee',
    created: '2024-12-01',
    lastModified: '2025-01-15',
    version: '2.1',
    approvedBy: 'Constitutional Council',
    effectiveDate: '2025-02-01',
  };

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-4">
              <div>
                <CardTitle className="text-2xl mb-2">{policy.title}</CardTitle>
                <p className="text-muted-foreground">{policy.description}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge className={getStatusColor(policy.status)}>
                  {policy.status}
                </Badge>
                <Badge variant="outline">
                  {policy.domain}
                </Badge>
                <Badge variant="outline">
                  Version {policy.version}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Share className="h-4 w-4 mr-2" />
                Share
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button variant="outline" size="sm">
                <Archive className="h-4 w-4 mr-2" />
                Archive
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Metadata */}
      <Card>
        <CardHeader>
          <CardTitle>Policy Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Author:</span>
                <span>{policy.author}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Created:</span>
                <span>{policy.created}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Last Modified:</span>
                <span>{policy.lastModified}</span>
              </div>
            </div>
            <div className="space-y-2">
              <div>
                <span className="font-medium">Approved By:</span>
                <span className="ml-2">{policy.approvedBy}</span>
              </div>
              <div>
                <span className="font-medium">Effective Date:</span>
                <span className="ml-2">{policy.effectiveDate}</span>
              </div>
              <div>
                <span className="font-medium">Version:</span>
                <span className="ml-2">{policy.version}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content */}
      <Card>
        <CardHeader>
          <CardTitle>Policy Content</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose max-w-none">
            <div dangerouslySetInnerHTML={{ __html: policy.content.replace(/\n/g, '<br />').replace(/##\s/g, '<h2>').replace(/<br \/><br \/>/g, '</h2><br />') }} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}