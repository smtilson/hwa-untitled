import type { Theme } from '../services/useTheme';

interface ThemeToggleProps {
  theme: Theme;
  onToggle: () => void;
}

export default function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  const label = theme === 'dark' ? 'Light mode' : 'Dark mode';
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      className="mt-3 px-3.5 py-1.5 text-sm rounded-md border border-gray-400 bg-white text-gray-900 hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700 transition-colors"
    >
      {label}
    </button>
  );
}
