import React from 'react';
import { usePrinciples } from '../../hooks/council/usePrinciples'; // Adjust path as needed

const CouncilPage: React.FC = () => {
  const { principles, isLoading, isError } = usePrinciples();

  if (isLoading) return <div className="container mx-auto p-4"><p>Loading principles...</p></div>;
  if (isError) return <div className="container mx-auto p-4"><p>Failed to load principles.</p></div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Constitutional Council</h1>
      {principles && principles.length > 0 ? (
        <ul>
          {principles.map((principle) => (
            <li key={principle.id} className="mb-2 p-2 border rounded">
              <h2 className="text-xl">{principle.title || `Principle ${principle.id}`}</h2>
              {/* Placeholder for more principle details or actions */}
            </li>
          ))}
        </ul>
      ) : (
        <p>No principles found.</p>
      )}
      {/* Further UI elements will be added here */}
    </div>
  );
};

export default CouncilPage;
