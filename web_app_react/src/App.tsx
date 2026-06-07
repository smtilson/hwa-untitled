import { useState } from 'react';
import SinglePlayer from './pages/SinglePlayer';
import TwoPlayer from './pages/TwoPlayer';
import ThemeToggle from './components/ThemeToggle';
import { useTheme } from './services/useTheme';

type View = 'single' | 'two';

function App() {
  const [view, setView] = useState<View>('single');
  const { theme, toggle } = useTheme();

  const otherView: View = view === 'single' ? 'two' : 'single';
  const navLabel = view === 'single' ? 'Two players' : 'Single player';
  const title = view === 'single' ? 'HWA Tracker' : 'HWA Tracker - Two Players';

  return (
    /* blech: PAGE BACKGROUND colors (bg-gray-100, dark:bg-gray-900) and padding (py-8 sm:py-8, px-3 sm:px-4) */
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-4 px-3 sm:py-8 sm:px-4">
      <div className={view === 'two' ? 'max-w-4xl mx-auto' : 'max-w-md mx-auto'}>
        <header className="text-center mb-8 flex flex-col items-center">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            {title}
          </h1>
          <nav className="mt-3 text-sm">
            <button
              type="button"
              onClick={() => setView(otherView)}
              className="underline text-gray-900 dark:text-white bg-transparent border-0 cursor-pointer p-0"
            >
              {navLabel}
            </button>
          </nav>
          <ThemeToggle theme={theme} onToggle={toggle} />
        </header>

        {view === 'single' ? <SinglePlayer /> : <TwoPlayer />}
      </div>
    </div>
  );
}

export default App;
