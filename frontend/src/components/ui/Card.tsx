import { cn } from '@/lib/utils';
import type { CardProps } from '@/types/ui';

export function Card({ title, icon, actions, children, className }: CardProps): JSX.Element {
  return (
    <div className={cn('card', className)}>
      {(title || icon || actions) && (
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {icon && <div className="text-primary-400">{icon}</div>}
            <h3 className="text-lg font-semibold text-white">{title}</h3>
          </div>
          {actions && <div className="flex items-center space-x-2">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
