import { Button } from '@/components/ui/button';
import { Plus, Download, Upload } from 'lucide-react';

export function PolicyHeader() {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Policy Management</h1>
        <p className="text-muted-foreground">
          Create, manage, and track policies across all domains.
        </p>
      </div>
      <div className="flex items-center gap-4">
        <Button variant="outline">
          <Upload className="mr-2 h-4 w-4" />
          Import
        </Button>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export
        </Button>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Policy
        </Button>
      </div>
    </div>
  );
}
