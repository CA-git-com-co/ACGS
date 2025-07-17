/**
 * Task Card Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React from 'react';
import styled from 'styled-components';
import { format } from 'date-fns';
import { 
  Calendar, 
  Clock, 
  User, 
  FileText, 
  Image, 
  Video, 
  Mic, 
  AlertCircle,
  CheckCircle,
  Play,
  Flag
} from 'lucide-react';

const CardContainer = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s;
  position: relative;
  
  &:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
`;

const Title = styled.h3`
  color: #2d3748;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  flex: 1;
`;

const StatusBadge = styled.span`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  
  ${props => {
    switch (props.status) {
      case 'pending':
        return 'background: #fef5e7; color: #d69e2e;';
      case 'in_progress':
        return 'background: #e6f3ff; color: #3182ce;';
      case 'completed':
        return 'background: #f0fff4; color: #38a169;';
      case 'escalated':
        return 'background: #fed7d7; color: #e53e3e;';
      default:
        return 'background: #edf2f7; color: #4a5568;';
    }
  }}
`;

const PriorityBadge = styled.div`
  position: absolute;
  top: 15px;
  right: 15px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  
  ${props => {
    switch (props.priority) {
      case 'critical':
        return 'background: #e53e3e;';
      case 'urgent':
        return 'background: #dd6b20;';
      case 'high':
        return 'background: #d69e2e;';
      case 'medium':
        return 'background: #3182ce;';
      case 'low':
        return 'background: #38a169;';
      default:
        return 'background: #718096;';
    }
  }}
`;

const Description = styled.p`
  color: #718096;
  font-size: 0.9rem;
  margin: 0 0 15px 0;
  line-height: 1.4;
`;

const MetaInfo = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
  color: #718096;
  font-size: 0.85rem;
`;

const ContentTypeIcon = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
  color: #4a5568;
  font-size: 0.9rem;
  font-weight: 500;
`;

const ConstitutionalRequirements = styled.div`
  background: #f7fafc;
  border-left: 4px solid #667eea;
  padding: 10px;
  margin: 15px 0;
  border-radius: 0 4px 4px 0;
`;

const RequirementTitle = styled.div`
  font-weight: 600;
  color: #2d3748;
  font-size: 0.9rem;
  margin-bottom: 5px;
`;

const RequirementList = styled.ul`
  margin: 0;
  padding-left: 20px;
  font-size: 0.85rem;
  color: #4a5568;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;
`;

const Button = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
  
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background: #667eea;
          color: white;
          &:hover { background: #5a6fd8; }
        `;
      case 'secondary':
        return `
          background: #edf2f7;
          color: #4a5568;
          &:hover { background: #e2e8f0; }
        `;
      case 'danger':
        return `
          background: #fed7d7;
          color: #e53e3e;
          &:hover { background: #fbb6ce; }
        `;
      default:
        return `
          background: #edf2f7;
          color: #4a5568;
          &:hover { background: #e2e8f0; }
        `;
    }
  }}
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const getContentTypeIcon = (type) => {
  switch (type) {
    case 'text':
      return <FileText size={16} />;
    case 'image':
      return <Image size={16} />;
    case 'video':
      return <Video size={16} />;
    case 'audio':
      return <Mic size={16} />;
    case 'document':
      return <FileText size={16} />;
    case 'conversation':
      return <User size={16} />;
    default:
      return <FileText size={16} />;
  }
};

const formatDueDate = (dueDate) => {
  if (!dueDate) return 'No due date';
  
  const date = new Date(dueDate);
  const now = new Date();
  const diffInHours = (date - now) / (1000 * 60 * 60);
  
  if (diffInHours < 0) {
    return `Overdue by ${Math.abs(Math.floor(diffInHours))}h`;
  } else if (diffInHours < 24) {
    return `Due in ${Math.floor(diffInHours)}h`;
  } else {
    return `Due ${format(date, 'MMM dd, yyyy')}`;
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case 'pending':
      return '#d69e2e';
    case 'in_progress':
      return '#3182ce';
    case 'completed':
      return '#38a169';
    case 'escalated':
      return '#e53e3e';
    default:
      return '#718096';
  }
};

export const TaskCard = ({ task, onAssign, onReview, isAssigning }) => {
  const isOverdue = task.due_date && new Date(task.due_date) < new Date();
  const canReview = task.status === 'in_progress' && task.assigned_to === 'current_user'; // TODO: Get actual user ID
  const canAssign = task.status === 'pending';

  return (
    <CardContainer>
      <PriorityBadge priority={task.priority} />
      
      <CardHeader>
        <Title>{task.title}</Title>
        <StatusBadge status={task.status}>
          {task.status.replace('_', ' ')}
        </StatusBadge>
      </CardHeader>

      {task.description && (
        <Description>{task.description}</Description>
      )}

      <MetaInfo>
        <MetaItem>
          <ContentTypeIcon>
            {getContentTypeIcon(task.content_type)}
            {task.content_type}
          </ContentTypeIcon>
        </MetaItem>
        
        <MetaItem>
          <Calendar size={14} />
          Created {format(new Date(task.created_at), 'MMM dd, yyyy')}
        </MetaItem>
        
        <MetaItem>
          <Clock size={14} />
          <span style={{ color: isOverdue ? '#e53e3e' : '#718096' }}>
            {formatDueDate(task.due_date)}
          </span>
        </MetaItem>
        
        {task.assigned_to && (
          <MetaItem>
            <User size={14} />
            Assigned to {task.assigned_to}
          </MetaItem>
        )}
      </MetaInfo>

      {task.constitutional_requirements && Object.keys(task.constitutional_requirements).length > 0 && (
        <ConstitutionalRequirements>
          <RequirementTitle>Constitutional Requirements:</RequirementTitle>
          <RequirementList>
            {Object.entries(task.constitutional_requirements).map(([key, value]) => (
              <li key={key}>{key}: {value}</li>
            ))}
          </RequirementList>
        </ConstitutionalRequirements>
      )}

      <ActionButtons>
        {canAssign && (
          <Button
            variant="primary"
            onClick={() => onAssign(task.id, 'current_user')}
            disabled={isAssigning}
          >
            <User size={16} />
            {isAssigning ? 'Assigning...' : 'Take Task'}
          </Button>
        )}
        
        {canReview && (
          <Button
            variant="primary"
            onClick={() => onReview(task.id)}
          >
            <Play size={16} />
            Start Review
          </Button>
        )}
        
        {task.priority === 'urgent' || task.priority === 'critical' && (
          <Button variant="danger">
            <Flag size={16} />
            Escalate
          </Button>
        )}
        
        <Button variant="secondary">
          <FileText size={16} />
          View Details
        </Button>
      </ActionButtons>
    </CardContainer>
  );
};