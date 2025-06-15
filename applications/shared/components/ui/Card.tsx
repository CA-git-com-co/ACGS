'use client'

import * as React from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { cn } from '@/lib/utils'
import { GripVertical } from 'lucide-react'

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  draggable?: boolean
  dragId?: string
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, draggable = false, dragId, children, ...props }, ref) => {
    const {
      attributes,
      listeners,
      setNodeRef,
      transform,
      transition,
      isDragging,
    } = useSortable({
      id: dragId || 'card',
      disabled: !draggable,
    })

    const style = {
      transform: CSS.Transform.toString(transform),
      transition,
    }

    const cardRef = draggable ? setNodeRef : ref

    return (
      <div
        ref={cardRef}
        style={style}
        className={cn(
          'rounded-lg border border-gray-200 bg-base-white shadow-card',
          'transition-all duration-200 ease-out hover:shadow-card-hover hover:-translate-y-0.5',
          'dark:border-gray-700 dark:bg-gray-800',
          isDragging && 'opacity-50 rotate-3 scale-105',
          className
        )}
        {...props}
        {...(draggable ? attributes : {})}
      >
        {draggable && (
          <div
            {...listeners}
            className="absolute top-2 right-2 cursor-grab p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-gray-100 dark:hover:bg-gray-700 transition-opacity"
            aria-label="Drag to reorder"
          >
            <GripVertical className="h-4 w-4 text-gray-400" />
          </div>
        )}
        {children}
      </div>
    )
  }
)
Card.displayName = 'Card'

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6 pb-4', className)}
    {...props}
  />
))
CardHeader.displayName = 'CardHeader'

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-subheading font-semibold leading-none tracking-tight', className)}
    {...props}
  />
))
CardTitle.displayName = 'CardTitle'

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-body text-gray-500 dark:text-gray-400', className)}
    {...props}
  />
))
CardDescription.displayName = 'CardDescription'

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
))
CardContent.displayName = 'CardContent'

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
))
CardFooter.displayName = 'CardFooter'

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
}