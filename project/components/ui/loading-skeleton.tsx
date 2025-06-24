import { cn } from '@/lib/utils';

interface LoadingSkeletonProps {
  className?: string;
  count?: number;
  height?: string;
}

export function LoadingSkeleton({ className, count = 1, height }: LoadingSkeletonProps) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'animate-pulse rounded-md bg-muted',
            height ? '' : 'h-4',
            className
          )}
          style={height ? { height } : undefined}
        />
      ))}
    </div>
  );
}