export interface Policy {
  id: string
  title: string
  description: string
  status: 'draft' | 'active' | 'archived'
  category: string
  createdAt: Date
  updatedAt: Date
  author: string
}

export interface Proposal {
  id: string
  title: string
  description: string
  proposer: string
  status: 'pending' | 'voting' | 'approved' | 'rejected'
  votingDeadline: Date
  createdAt: Date
  votes: Vote[]
}

export interface Vote {
  id: string
  proposalId: string
  userId: string
  vote: 'yes' | 'no' | 'abstain'
  comment?: string
  createdAt: Date
}

export interface DashboardCard {
  id: string
  title: string
  content: React.ReactNode
  position: number
  size: 'small' | 'medium' | 'large'
}