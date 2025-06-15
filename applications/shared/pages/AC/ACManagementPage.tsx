import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import ACService from '../../services/ACService';
import { Principle } from '../../types/governance';
import {
  Spinner,
  CardSkeleton,
  LoadingButton,
  LoadingOverlay
} from '../../components/LoadingStates';
import { useLoadingState, useMultipleLoadingStates } from '../../hooks/useLoadingState';
import ServiceErrorBoundary from '../../components/ServiceErrorBoundary';
import AuthErrorBoundary from '../../components/AuthErrorBoundary';

interface PrincipleFormData {
  id?: string;
  name: string;
  description: string;
  content: string;
  status: 'draft' | 'approved' | 'deprecated';
}

interface PrincipleEditModalProps {
  principle: PrincipleFormData;
  onSave: (principle: PrincipleFormData) => Promise<void>;
  onClose: () => void;
  error: string;
  isLoading: boolean;
}

const PrincipleEditModal: React.FC<PrincipleEditModalProps> = ({
  principle,
  onSave,
  onClose,
  error,
  isLoading
}) => {
  const [formData, setFormData] = useState<PrincipleFormData>({ ...principle });

  useEffect(() => {
    setFormData({ ...principle });
  }, [principle]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          {formData.id ? 'Edit Principle' : 'Create New Principle'}
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Name *
            </label>
            <Input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description || ''}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
              Content *
            </label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleChange}
              rows={5}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="draft">Draft</option>
              <option value="approved">Approved</option>
              <option value="deprecated">Deprecated</option>
            </select>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isLoading}
              isLoading={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

const ACManagementPage: React.FC = () => {
  const [principles, setPrinciples] = useState<Principle[]>([]);
  const [error, setError] = useState('');
  const [editingPrinciple, setEditingPrinciple] = useState<PrincipleFormData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { currentUser } = useAuth();

  // Multiple loading states for different operations
  const {
    states: loadingStates,
    startLoading,
    stopLoading,
    setError: setLoadingError,
    isAnyLoading
  } = useMultipleLoadingStates(['fetch', 'save', 'delete'], {
    timeout: 30000,
    retryAttempts: 3,
    onTimeout: () => console.warn('AC Service operation timed out'),
    onError: (error) => console.error('AC Service error:', error)
  });

  const fetchPrinciples = useCallback(async () => {
    if (!currentUser) return;

    startLoading('fetch');
    setError('');

    try {
      const data = await ACService.getPrinciples();
      setPrinciples(data.principles || []);
      stopLoading('fetch');
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch principles.';
      setError(errorMessage);
      setLoadingError('fetch', new Error(errorMessage));
    }
  }, [currentUser, startLoading, stopLoading, setLoadingError]);

  useEffect(() => {
    fetchPrinciples();
  }, [fetchPrinciples]);

  const handleEdit = (principle: Principle) => {
    setEditingPrinciple({
      id: principle.id,
      name: principle.title,
      description: principle.content,
      content: principle.content,
      status: 'approved' // Default status, adjust based on your data structure
    });
    setIsModalOpen(true);
  };

  const handleCreateNew = () => {
    setEditingPrinciple({
      name: '',
      description: '',
      content: '',
      status: 'draft'
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this principle?')) {
      startLoading('delete');
      try {
        await ACService.deletePrinciple(id);
        await fetchPrinciples();
        stopLoading('delete');
      } catch (err: any) {
        const errorMessage = err.message || 'Failed to delete principle.';
        setError(errorMessage);
        setLoadingError('delete', new Error(errorMessage));
      }
    }
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingPrinciple(null);
    setError('');
  };

  const handleModalSave = async (updatedPrinciple: PrincipleFormData) => {
    startLoading('save');
    setError('');

    try {
      if (updatedPrinciple.id) {
        await ACService.updatePrinciple(updatedPrinciple.id, updatedPrinciple);
      } else {
        await ACService.createPrinciple(updatedPrinciple);
      }
      handleModalClose();
      await fetchPrinciples();
      stopLoading('save');
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to save principle.';
      setError(errorMessage);
      setLoadingError('save', new Error(errorMessage));
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-100';
      case 'deprecated': return 'text-red-600 bg-red-100';
      default: return 'text-yellow-600 bg-yellow-100';
    }
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="p-6">
          <p className="text-gray-600">Please login to manage AC principles.</p>
        </Card>
      </div>
    );
  }

  return (
    <AuthErrorBoundary>
      <ServiceErrorBoundary
        serviceName="AC"
        serviceUrl={process.env.REACT_APP_AC_API_URL || 'http://localhost:8001'}
      >
        <div className="min-h-screen bg-gray-50 py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Artificial Constitution Management</h1>
          <p className="mt-2 text-gray-600">
            Manage constitutional principles that form the foundation of the governance system.
          </p>
        </div>

        {/* Actions */}
        <div className="mb-6 flex justify-between items-center">
          <LoadingButton
            onClick={handleCreateNew}
            isLoading={loadingStates.save?.isLoading || false}
            disabled={isAnyLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            loadingText="Creating..."
          >
            Create New Principle
          </LoadingButton>

          {isAnyLoading && (
            <div className="flex items-center text-gray-600">
              <Spinner size="sm" className="mr-2" />
              {loadingStates.fetch?.isLoading && 'Loading principles...'}
              {loadingStates.save?.isLoading && 'Saving principle...'}
              {loadingStates.delete?.isLoading && 'Deleting principle...'}
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && !isModalOpen && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Principles List */}
        {loadingStates.fetch?.isLoading ? (
          <div className="grid gap-6">
            {Array.from({ length: 3 }).map((_, index) => (
              <CardSkeleton key={index} />
            ))}
          </div>
        ) : principles.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-gray-500">No principles found. Create your first principle to get started.</p>
          </Card>
        ) : (
          <LoadingOverlay isLoading={loadingStates.delete?.isLoading || false} blur={true}>
            <div className="grid gap-6">
              {principles.map((principle) => (
              <Card key={principle.id} className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {principle.title}
                    </h3>
                    <div className="flex items-center mt-2 space-x-4">
                      <span className="text-sm text-gray-500">ID: {principle.id}</span>
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor('approved')}`}>
                        Active
                      </span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <LoadingButton
                      onClick={() => handleEdit(principle)}
                      isLoading={false}
                      disabled={isAnyLoading}
                      className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Edit
                    </LoadingButton>
                    <LoadingButton
                      onClick={() => handleDelete(principle.id)}
                      isLoading={loadingStates.delete?.isLoading || false}
                      disabled={isAnyLoading}
                      className="px-3 py-1 text-sm bg-red-600 text-white rounded-md hover:bg-red-700"
                      loadingText="Deleting..."
                    >
                      Delete
                    </LoadingButton>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-700">Category:</p>
                    <p className="text-sm text-gray-600">{principle.category}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Content:</p>
                    <div className="bg-gray-50 rounded-md p-3 mt-1">
                      <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                        {principle.content}
                      </pre>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Priority: {principle.priority}
                  </div>
                </div>
              </Card>
              ))}
            </div>
          </LoadingOverlay>
        )}

        {/* Modal */}
        {isModalOpen && editingPrinciple && (
          <PrincipleEditModal
            principle={editingPrinciple}
            onSave={handleModalSave}
            onClose={handleModalClose}
            error={error}
            isLoading={loadingStates.save?.isLoading || false}
          />
        )}
          </div>
        </div>
      </ServiceErrorBoundary>
    </AuthErrorBoundary>
  );
};

export default ACManagementPage;
