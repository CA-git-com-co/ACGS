'use client';

import * as React from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy
} from '@dnd-kit/sortable';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { DashboardCard } from '@/types/governance';

// Mock dashboard cards data
const initialCards: DashboardCard[] = [
  {
    id: '1',
    title: 'Active Policies',
    content: (
      <div className="space-y-2">
        <div className="text-large-heading font-bold text-accent-primary">24</div>
        <p className="text-caption text-gray-500">Currently in effect</p>
      </div>
    ),
    position: 0,
    size: 'small'
  },
  {
    id: '2',
    title: 'Pending Proposals',
    content: (
      <div className="space-y-2">
        <div className="text-large-heading font-bold text-status-warning">8</div>
        <p className="text-caption text-gray-500">Awaiting review</p>
      </div>
    ),
    position: 1,
    size: 'small'
  },
  {
    id: '3',
    title: 'Recent Activity',
    content: (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-body">Policy #12 Updated</span>
          <span className="text-caption text-gray-500">2h ago</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-body">New Proposal Submitted</span>
          <span className="text-caption text-gray-500">4h ago</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-body">Vote Completed</span>
          <span className="text-caption text-gray-500">1d ago</span>
        </div>
      </div>
    ),
    position: 2,
    size: 'large'
  },
  {
    id: '4',
    title: 'Voting Status',
    content: (
      <div className="space-y-2">
        <div className="text-large-heading font-bold text-status-success">94%</div>
        <p className="text-caption text-gray-500">Participation rate</p>
      </div>
    ),
    position: 3,
    size: 'small'
  }
];

export function DashboardCards() {
  const [cards, setCards] = React.useState(initialCards);
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates
    })
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setCards(items => {
        const oldIndex = items.findIndex(item => item.id === active.id);
        const newIndex = items.findIndex(item => item.id === over.id);

        return arrayMove(items, oldIndex, newIndex);
      });
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-heading font-semibold text-gray-900 dark:text-gray-100">
          Dashboard Overview
        </h2>
        <p className="text-body text-gray-500 dark:text-gray-400 mt-1">
          Drag and drop cards to customize your dashboard layout.
        </p>
      </div>

      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={cards} strategy={rectSortingStrategy}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {cards.map(card => (
              <Card
                key={card.id}
                draggable
                dragId={card.id}
                className={`group ${
                  card.size === 'large'
                    ? 'md:col-span-2'
                    : card.size === 'medium'
                      ? 'md:col-span-1'
                      : ''
                }`}
              >
                <CardHeader>
                  <CardTitle>{card.title}</CardTitle>
                </CardHeader>
                <CardContent>{card.content}</CardContent>
              </Card>
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}
