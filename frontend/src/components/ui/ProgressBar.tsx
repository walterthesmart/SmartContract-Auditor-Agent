import { cn } from '@/lib/utils';
import type { ProgressBarProps } from '@/types/ui';

export function ProgressBar({ 
  value, 
  max = 100, 
  label, 
  showPercentage = true, 
  className 
}: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={cn('space-y-2', className)}>
      {(label || showPercentage) && (
        <div className="flex justify-between text-sm">
          {label && <span className="text-dark-300">{label}</span>}
          {showPercentage && (
            <span className="text-dark-400">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div className="h-2 w-full overflow-hidden rounded-full bg-dark-700">
        <div
          className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
