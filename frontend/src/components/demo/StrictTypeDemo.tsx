/**
 * Demonstration of Strict TypeScript and ESLint Rules
 * This component showcases all the strict typing and linting rules in action
 */

'use client';

import { useCallback, useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react';

import { cn } from '@/lib/utils';
import type { BadgeProps } from '@/types/ui';

// Strict interface definitions with readonly properties
interface StrictDemoProps {
  readonly title: string;
  readonly items: readonly DemoItem[];
  readonly onItemClick?: (item: DemoItem) => void;
  readonly className?: string;
}

interface DemoItem {
  readonly id: string;
  readonly name: string;
  readonly type: 'success' | 'warning' | 'error' | 'info';
  readonly description: string;
  readonly metadata?: readonly {
    readonly key: string;
    readonly value: string | number | boolean;
  }[];
}

// Strict type guards
function isDemoItemType(value: string): value is DemoItem['type'] {
  return ['success', 'warning', 'error', 'info'].includes(value);
}

function isValidDemoItem(item: unknown): item is DemoItem {
  return (
    typeof item === 'object' &&
    item !== null &&
    'id' in item &&
    'name' in item &&
    'type' in item &&
    'description' in item &&
    typeof (item as DemoItem).id === 'string' &&
    typeof (item as DemoItem).name === 'string' &&
    isDemoItemType((item as DemoItem).type) &&
    typeof (item as DemoItem).description === 'string'
  );
}

// Strict utility functions with proper return types
function getIconForType(type: DemoItem['type']): JSX.Element {
  switch (type) {
    case 'success': {
      return <CheckCircle className="h-4 w-4 text-green-400" />;
    }
    case 'warning': {
      return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
    }
    case 'error': {
      return <XCircle className="h-4 w-4 text-red-400" />;
    }
    case 'info': {
      return <Info className="h-4 w-4 text-blue-400" />;
    }
    default: {
      // This should never happen due to strict typing, but TypeScript requires it
      const _exhaustiveCheck: never = type;
      return _exhaustiveCheck;
    }
  }
}

function getBadgeVariant(type: DemoItem['type']): BadgeProps['variant'] {
  switch (type) {
    case 'success': {
      return 'low'; // Using 'low' as success variant
    }
    case 'warning': {
      return 'medium';
    }
    case 'error': {
      return 'critical';
    }
    case 'info': {
      return 'info';
    }
    default: {
      const _exhaustiveCheck: never = type;
      return _exhaustiveCheck;
    }
  }
}

// Main component with strict typing
export function StrictTypeDemo({ 
  title, 
  items, 
  onItemClick, 
  className 
}: StrictDemoProps): JSX.Element {
  const [selectedItem, setSelectedItem] = useState<DemoItem | null>(null);
  const [filter, setFilter] = useState<DemoItem['type'] | 'all'>('all');

  // Memoized filtered items with strict typing
  const filteredItems = useMemo((): readonly DemoItem[] => {
    if (filter === 'all') {
      return items;
    }
    return items.filter((item): item is DemoItem => item.type === filter);
  }, [items, filter]);

  // Strict event handlers
  const handleItemClick = useCallback((item: DemoItem): void => {
    setSelectedItem(item);
    onItemClick?.(item);
  }, [onItemClick]);

  const handleFilterChange = useCallback((newFilter: DemoItem['type'] | 'all'): void => {
    setFilter(newFilter);
    setSelectedItem(null);
  }, []);

  // Strict validation
  const validItems = useMemo((): readonly DemoItem[] => {
    return items.filter(isValidDemoItem);
  }, [items]);

  // Statistics with strict typing
  const statistics = useMemo(() => {
    const stats = {
      total: validItems.length,
      success: 0,
      warning: 0,
      error: 0,
      info: 0,
    } as const;

    for (const item of validItems) {
      switch (item.type) {
        case 'success': {
          stats.success += 1;
          break;
        }
        case 'warning': {
          stats.warning += 1;
          break;
        }
        case 'error': {
          stats.error += 1;
          break;
        }
        case 'info': {
          stats.info += 1;
          break;
        }
        default: {
          const _exhaustiveCheck: never = item.type;
          return _exhaustiveCheck;
        }
      }
    }

    return stats;
  }, [validItems]);

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="border-b border-dark-700 pb-4">
        <h2 className="text-xl font-semibold text-white">{title}</h2>
        <p className="mt-1 text-sm text-dark-400">
          Demonstrating strict TypeScript and ESLint rules
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        <div className="rounded-lg bg-dark-800/50 p-3 text-center">
          <div className="text-lg font-bold text-white">{statistics.total}</div>
          <div className="text-xs text-dark-400">Total</div>
        </div>
        <div className="rounded-lg bg-dark-800/50 p-3 text-center">
          <div className="text-lg font-bold text-green-400">{statistics.success}</div>
          <div className="text-xs text-dark-400">Success</div>
        </div>
        <div className="rounded-lg bg-dark-800/50 p-3 text-center">
          <div className="text-lg font-bold text-yellow-400">{statistics.warning}</div>
          <div className="text-xs text-dark-400">Warning</div>
        </div>
        <div className="rounded-lg bg-dark-800/50 p-3 text-center">
          <div className="text-lg font-bold text-red-400">{statistics.error}</div>
          <div className="text-xs text-dark-400">Error</div>
        </div>
        <div className="rounded-lg bg-dark-800/50 p-3 text-center">
          <div className="text-lg font-bold text-blue-400">{statistics.info}</div>
          <div className="text-xs text-dark-400">Info</div>
        </div>
      </div>

      {/* Filter Controls */}
      <div className="flex flex-wrap gap-2">
        {(['all', 'success', 'warning', 'error', 'info'] as const).map((filterType) => (
          <button
            key={filterType}
            type="button"
            onClick={(): void => handleFilterChange(filterType)}
            className={cn(
              'rounded-lg px-3 py-1 text-sm font-medium transition-colors',
              filter === filterType
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-dark-300 hover:bg-dark-600 hover:text-white'
            )}
          >
            {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
          </button>
        ))}
      </div>

      {/* Items List */}
      <div className="space-y-2">
        {filteredItems.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-dark-600 p-6 text-center">
            <p className="text-dark-400">No items match the current filter</p>
          </div>
        ) : (
          filteredItems.map((item) => (
            <div
              key={item.id}
              className={cn(
                'cursor-pointer rounded-lg border p-4 transition-all',
                selectedItem?.id === item.id
                  ? 'border-primary-500 bg-primary-500/10'
                  : 'border-dark-700 bg-dark-800/30 hover:border-dark-600 hover:bg-dark-800/50'
              )}
              onClick={(): void => handleItemClick(item)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getIconForType(item.type)}
                  <div>
                    <h3 className="font-medium text-white">{item.name}</h3>
                    <p className="mt-1 text-sm text-dark-300">{item.description}</p>
                  </div>
                </div>
                <span
                  className={cn(
                    'rounded-full px-2 py-1 text-xs font-medium',
                    `badge-${getBadgeVariant(item.type)}`
                  )}
                >
                  {item.type.toUpperCase()}
                </span>
              </div>

              {/* Metadata */}
              {item.metadata && item.metadata.length > 0 && (
                <div className="mt-3 border-t border-dark-700 pt-3">
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {item.metadata.map((meta) => (
                      <div key={meta.key} className="flex justify-between">
                        <span className="text-dark-400">{meta.key}:</span>
                        <span className="font-mono text-dark-200">
                          {String(meta.value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Selected Item Details */}
      {selectedItem && (
        <div className="rounded-lg border border-primary-500/30 bg-primary-500/5 p-4">
          <h3 className="font-medium text-primary-300">Selected Item</h3>
          <div className="mt-2 space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-dark-400">ID:</span>
              <span className="font-mono text-white">{selectedItem.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Type:</span>
              <span className="text-white">{selectedItem.type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Name:</span>
              <span className="text-white">{selectedItem.name}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
