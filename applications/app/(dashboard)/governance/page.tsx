import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Plus, Clock, CheckCircle, XCircle, Users } from 'lucide-react';

// Mock data for proposals
const proposals = [
  {
    id: '1',
    title: 'Implement New Security Protocols',
    description: 'Proposal to enhance security measures across all systems',
    proposer: 'Security Team',
    status: 'voting' as const,
    votingDeadline: new Date('2024-02-15'),
    createdAt: new Date('2024-01-25'),
    votes: {
      yes: 12,
      no: 3,
      abstain: 1,
    },
  },
  {
    id: '2',
    title: 'Update Remote Work Policy',
    description: 'Revisions to remote work guidelines based on team feedback',
    proposer: 'HR Department',
    status: 'pending' as const,
    votingDeadline: new Date('2024-02-20'),
    createdAt: new Date('2024-01-28'),
    votes: {
      yes: 0,
      no: 0,
      abstain: 0,
    },
  },
  {
    id: '3',
    title: 'Budget Allocation for Q2',
    description: 'Proposed budget distribution for the second quarter',
    proposer: 'Finance Team',
    status: 'approved' as const,
    votingDeadline: new Date('2024-01-30'),
    createdAt: new Date('2024-01-15'),
    votes: {
      yes: 18,
      no: 2,
      abstain: 3,
    },
  },
];

const statusConfig = {
  pending: {
    icon: Clock,
    color: 'text-status-warning',
    bgColor: 'bg-status-warning/10',
    label: 'Pending Review',
  },
  voting: {
    icon: Users,
    color: 'text-accent-primary',
    bgColor: 'bg-accent-primary/10',
    label: 'Active Voting',
  },
  approved: {
    icon: CheckCircle,
    color: 'text-status-success',
    bgColor: 'bg-status-success/10',
    label: 'Approved',
  },
  rejected: {
    icon: XCircle,
    color: 'text-status-error',
    bgColor: 'bg-status-error/10',
    label: 'Rejected',
  },
};

export default function GovernancePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-large-heading font-bold text-gray-900 dark:text-gray-100">
            Governance
          </h1>
          <p className="text-body text-gray-500 dark:text-gray-400 mt-1">
            Manage proposals and voting processes
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Proposal
        </Button>
      </div>

      <div className="space-y-4">
        {proposals.map((proposal) => {
          const config = statusConfig[proposal.status];
          const StatusIcon = config.icon;
          const totalVotes = proposal.votes.yes + proposal.votes.no + proposal.votes.abstain;
          const approvalRate = totalVotes > 0 ? (proposal.votes.yes / totalVotes) * 100 : 0;

          return (
            <Card key={proposal.id} className="group">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="mb-2">{proposal.title}</CardTitle>
                    <p className="text-body text-gray-600 dark:text-gray-300">
                      {proposal.description}
                    </p>
                  </div>
                  <div
                    className={`flex items-center gap-2 px-3 py-1 rounded-full ${config.bgColor}`}
                  >
                    <StatusIcon className={`h-4 w-4 ${config.color}`} />
                    <span className={`text-caption font-medium ${config.color}`}>
                      {config.label}
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <p className="text-caption font-medium text-gray-500 dark:text-gray-400">
                      Proposal Details
                    </p>
                    <div className="space-y-1 text-body">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Proposer:</span>
                        <span>{proposal.proposer}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Created:</span>
                        <span>{proposal.createdAt.toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Deadline:</span>
                        <span>{proposal.votingDeadline.toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-caption font-medium text-gray-500 dark:text-gray-400">
                      Vote Breakdown
                    </p>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-body text-gray-600 dark:text-gray-300">Yes</span>
                        <span className="text-body font-medium text-status-success">
                          {proposal.votes.yes}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-body text-gray-600 dark:text-gray-300">No</span>
                        <span className="text-body font-medium text-status-error">
                          {proposal.votes.no}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-body text-gray-600 dark:text-gray-300">Abstain</span>
                        <span className="text-body font-medium text-gray-500">
                          {proposal.votes.abstain}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-caption font-medium text-gray-500 dark:text-gray-400">
                      Progress
                    </p>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-body mb-1">
                          <span>Approval Rate</span>
                          <span className="font-medium">{approvalRate.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-status-success rounded-full h-2 transition-all duration-300"
                            style={{ width: `${approvalRate}%` }}
                          />
                        </div>
                      </div>
                      <div className="text-caption text-gray-500 dark:text-gray-400">
                        Total votes: {totalVotes}
                      </div>
                    </div>
                  </div>
                </div>

                {proposal.status === 'voting' && (
                  <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex gap-2 justify-end">
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                      <Button variant="destructive" size="sm">
                        Vote No
                      </Button>
                      <Button size="sm">Vote Yes</Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
