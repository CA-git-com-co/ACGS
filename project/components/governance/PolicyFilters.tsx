'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Search, Filter } from 'lucide-react';

export function PolicyFilters() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([]);
  const [selectedDomains, setSelectedDomains] = useState<string[]>([]);

  const statuses = [
    { id: 'ACTIVE', label: 'Active' },
    { id: 'DRAFT', label: 'Draft' },
    { id: 'REVIEW', label: 'Under Review' },
    { id: 'PENDING', label: 'Pending' },
    { id: 'ARCHIVED', label: 'Archived' },
  ];

  const domains = [
    { id: 'PRIVACY', label: 'Privacy' },
    { id: 'ENVIRONMENT', label: 'Environment' },
    { id: 'DIGITAL', label: 'Digital' },
    { id: 'HEALTHCARE', label: 'Healthcare' },
    { id: 'EDUCATION', label: 'Education' },
    { id: 'TRANSPORT', label: 'Transport' },
  ];

  const handleStatusChange = (statusId: string, checked: boolean) => {
    if (checked) {
      setSelectedStatuses([...selectedStatuses, statusId]);
    } else {
      setSelectedStatuses(selectedStatuses.filter(id => id !== statusId));
    }
  };

  const handleDomainChange = (domainId: string, checked: boolean) => {
    if (checked) {
      setSelectedDomains([...selectedDomains, domainId]);
    } else {
      setSelectedDomains(selectedDomains.filter(id => id !== domainId));
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedStatuses([]);
    setSelectedDomains([]);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Filter className="h-5 w-5" />
          Filters
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Search */}
        <div className="space-y-2">
          <Label htmlFor="search">Search Policies</Label>
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              id="search"
              placeholder="Search by title or description..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        {/* Status Filter */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">Status</Label>
          <div className="space-y-2">
            {statuses.map(status => (
              <div key={status.id} className="flex items-center space-x-2">
                <Checkbox
                  id={status.id}
                  checked={selectedStatuses.includes(status.id)}
                  onCheckedChange={checked => handleStatusChange(status.id, checked as boolean)}
                />
                <Label htmlFor={status.id} className="text-sm font-normal cursor-pointer">
                  {status.label}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Domain Filter */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">Domain</Label>
          <div className="space-y-2">
            {domains.map(domain => (
              <div key={domain.id} className="flex items-center space-x-2">
                <Checkbox
                  id={domain.id}
                  checked={selectedDomains.includes(domain.id)}
                  onCheckedChange={checked => handleDomainChange(domain.id, checked as boolean)}
                />
                <Label htmlFor={domain.id} className="text-sm font-normal cursor-pointer">
                  {domain.label}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Clear Filters */}
        <Button variant="outline" onClick={clearFilters} className="w-full">
          Clear Filters
        </Button>
      </CardContent>
    </Card>
  );
}
