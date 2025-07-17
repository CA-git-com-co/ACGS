/**
 * Review Dashboard Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-toastify';
import { 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  User, 
  FileText, 
  TrendingUp,
  Filter,
  Search
} from 'lucide-react';

import { reviewAPI } from '../utils/api';
import { TaskCard } from './TaskCard';
import { AnalyticsCard } from './AnalyticsCard';
import { FilterPanel } from './FilterPanel';

const CONSTITUTIONAL_HASH = 'cdd01ef066bc6cf2';

const DashboardContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
`;

const Header = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h1`
  color: #2d3748;
  font-size: 2rem;
  font-weight: 600;
  margin: 0;
`;

const Subtitle = styled.p`
  color: #718096;
  margin: 5px 0 0 0;
  font-size: 0.9rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
`;

const StatIcon = styled.div`
  padding: 12px;
  border-radius: 8px;
  background: ${props => props.color || '#667eea'};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const StatContent = styled.div`
  flex: 1;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: #718096;
`;

const FiltersContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
`;

const FilterButton = styled.button`
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: ${props => props.active ? '#667eea' : 'white'};
  color: ${props => props.active ? 'white' : '#4a5568'};
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;

  &:hover {
    background: ${props => props.active ? '#5a6fd8' : '#f7fafc'};
  }
`;

const TasksContainer = styled.div`
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const TasksHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const TasksTitle = styled.h2`
  color: #2d3748;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
`;

const SearchInput = styled.input`
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  width: 200px;
  font-size: 0.9rem;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const TasksList = styled.div`
  display: grid;
  gap: 15px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px;
  color: #718096;
`;

const LoadingState = styled.div`
  text-align: center;
  padding: 40px;
  color: #718096;
`;

const ConstitutionalBadge = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  background: #48bb78;
  color: white;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  z-index: 1000;
`;

export const ReviewDashboard = () => {
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const queryClient = useQueryClient();

  // Fetch reviewer workload
  const { data: workload, isLoading: workloadLoading } = useQuery(
    ['workload', 'current_user'], // TODO: Get actual user ID
    () => reviewAPI.getWorkload('current_user'),
    {
      refetchInterval: 30000 // Refresh every 30 seconds
    }
  );

  // Fetch analytics
  const { data: analytics, isLoading: analyticsLoading } = useQuery(
    'analytics',
    () => reviewAPI.getAnalytics(),
    {
      refetchInterval: 60000 // Refresh every minute
    }
  );

  // Task assignment mutation
  const assignTaskMutation = useMutation(
    ({ taskId, reviewerId }) => reviewAPI.assignTask(taskId, reviewerId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('workload');
        toast.success('Task assigned successfully');
      },
      onError: (error) => {
        toast.error(`Failed to assign task: ${error.message}`);
      }
    }
  );

  // Filter tasks based on active filter and search term
  const filteredTasks = React.useMemo(() => {
    if (!workload?.tasks) return [];
    
    let filtered = workload.tasks;
    
    // Apply status filter
    if (activeFilter !== 'all') {
      filtered = filtered.filter(task => task.status === activeFilter);
    }
    
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(task => 
        task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return filtered;
  }, [workload, activeFilter, searchTerm]);

  const handleAssignTask = (taskId, reviewerId) => {
    assignTaskMutation.mutate({ taskId, reviewerId });
  };

  const getStatColor = (type) => {
    switch (type) {
      case 'pending': return '#f6ad55';
      case 'progress': return '#667eea';
      case 'completed': return '#48bb78';
      case 'urgent': return '#f56565';
      default: return '#667eea';
    }
  };

  const getFilterCount = (status) => {
    if (!workload?.tasks) return 0;
    if (status === 'all') return workload.tasks.length;
    return workload.tasks.filter(task => task.status === status).length;
  };

  return (
    <DashboardContainer>
      <ConstitutionalBadge>
        Constitutional Hash: {CONSTITUTIONAL_HASH}
      </ConstitutionalBadge>
      
      <Header>
        <div>
          <Title>Human Review Dashboard</Title>
          <Subtitle>Manage and review content with constitutional compliance</Subtitle>
        </div>
      </Header>

      <StatsGrid>
        <StatCard>
          <StatIcon color={getStatColor('pending')}>
            <Clock size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{analytics?.pending_tasks || 0}</StatValue>
            <StatLabel>Pending Tasks</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color={getStatColor('progress')}>
            <User size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{workload?.reviewer_stats?.active_tasks || 0}</StatValue>
            <StatLabel>My Active Tasks</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color={getStatColor('completed')}>
            <CheckCircle size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{analytics?.completed_tasks || 0}</StatValue>
            <StatLabel>Completed Today</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color={getStatColor('urgent')}>
            <AlertTriangle size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{workload?.reviewer_stats?.high_priority_tasks || 0}</StatValue>
            <StatLabel>High Priority</StatLabel>
          </StatContent>
        </StatCard>
      </StatsGrid>

      <TasksContainer>
        <TasksHeader>
          <TasksTitle>Review Tasks</TasksTitle>
          <SearchInput
            type="text"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </TasksHeader>

        <FiltersContainer>
          <FilterButton
            active={activeFilter === 'all'}
            onClick={() => setActiveFilter('all')}
          >
            <FileText size={16} />
            All ({getFilterCount('all')})
          </FilterButton>
          
          <FilterButton
            active={activeFilter === 'pending'}
            onClick={() => setActiveFilter('pending')}
          >
            <Clock size={16} />
            Pending ({getFilterCount('pending')})
          </FilterButton>
          
          <FilterButton
            active={activeFilter === 'in_progress'}
            onClick={() => setActiveFilter('in_progress')}
          >
            <User size={16} />
            In Progress ({getFilterCount('in_progress')})
          </FilterButton>
          
          <FilterButton
            active={activeFilter === 'completed'}
            onClick={() => setActiveFilter('completed')}
          >
            <CheckCircle size={16} />
            Completed ({getFilterCount('completed')})
          </FilterButton>
        </FiltersContainer>

        <TasksList>
          {workloadLoading ? (
            <LoadingState>Loading tasks...</LoadingState>
          ) : filteredTasks.length === 0 ? (
            <EmptyState>
              {searchTerm ? 'No tasks match your search.' : 'No tasks available.'}
            </EmptyState>
          ) : (
            filteredTasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onAssign={handleAssignTask}
                isAssigning={assignTaskMutation.isLoading}
              />
            ))
          )}
        </TasksList>
      </TasksContainer>
    </DashboardContainer>
  );
};