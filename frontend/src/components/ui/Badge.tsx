import { cn } from '@/lib/utils';
import type { BadgeProps } from '@/types/ui';

export function Badge({ variant, children, className }: BadgeProps): JSX.Element {
  const variantClasses = {
    critical: 'badge-critical',
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
    info: 'badge-info',
  };

  return (
    <span className={cn('badge', variantClasses[variant], className)}>
      {children}
    </span>
  );
}
