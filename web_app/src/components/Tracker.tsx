import { cn } from '../services/utils';

interface TrackerProps {
  label: string;
  value: number;
  onIncrement: () => void;
  onDecrement: () => void;
  className?: string;
}

export default function Tracker({
  label,
  value,
  onIncrement,
  onDecrement,
  className,
}: TrackerProps) {
  return (
    <div className={cn('flex flex-col items-center gap-2 w-80', className)}>
      {/* blech: VALUE BOX dimensions (w-72, h-20) and colors (border-gray-400, bg-white, dark:bg-gray-800, dark:border-gray-600) */}
      <div className="rounded-md border border-gray-400 bg-white dark:bg-gray-800 dark:border-gray-600 w-40 h-20 flex items-center justify-center gap-3 text-center">
        {/* blech: LABEL & VALUE TEXT size (text-lg) and color (text-gray-900, dark:text-white) */}
        <span className="text-lg text-gray-900 dark:text-white">{label}</span>
        <span className="text-lg text-gray-900 dark:text-white">{value}</span>
      </div>
      <div className="flex gap-2">
        {/* blech: DECREMENT BUTTON dimensions (w-14, h-6) and colors (border-gray-400, bg-white, dark:bg-gray-800, dark:border-gray-600, hover:bg-gray-100, dark:hover:bg-gray-700) */}
        <button
          onClick={onDecrement}
          className="rounded-md border border-gray-400 bg-white dark:bg-gray-800 dark:border-gray-600 w-14 h-6 flex items-center justify-center text-sm text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label={`Decrease ${label}`}
        >
          -
        </button>
        {/* blech: INCREMENT BUTTON dimensions (w-14, h-6) and colors (border-gray-400, bg-white, dark:bg-gray-800, dark:border-gray-600, hover:bg-gray-100, dark:hover:bg-gray-700) */}
        <button
          onClick={onIncrement}
          className="rounded-md border border-gray-400 bg-white dark:bg-gray-800 dark:border-gray-600 w-14 h-6 flex items-center justify-center text-sm text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label={`Increase ${label}`}
        >
          +
        </button>
      </div>
    </div>
  );
}
