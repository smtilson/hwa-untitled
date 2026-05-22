import { useState } from 'react';
import Tracker from './components/Tracker';

const DEFAULT_HEAT = 0;
const DEFAULT_SHARDS = 5;

function App() {
  const [heat, setHeat] = useState(DEFAULT_HEAT);
  const [shards, setShards] = useState(DEFAULT_SHARDS);

  const reset = () => {
    setHeat(DEFAULT_HEAT);
    setShards(DEFAULT_SHARDS);
  };

  return (
    /* blech: PAGE BACKGROUND colors (bg-gray-100, dark:bg-gray-900) and padding (py-8, px-4) */
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-md mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            HWA Tracker
          </h1>
        </header>

        <div className="flex flex-col items-center gap-6">
          <Tracker
            label="Heat"
            value={heat}
            onIncrement={() => setHeat((v) => v + 1)}
            onDecrement={() => setHeat((v) => Math.max(0, v - 1))}
          />
          <Tracker
            label="Shards"
            value={shards}
            onIncrement={() => setShards((v) => v + 1)}
            onDecrement={() => setShards((v) => Math.max(0, v - 1))}
          />
          {/* blech: RESET BUTTON dimensions (px-6, py-2) and colors (border-gray-400, bg-white, dark:bg-gray-800, dark:border-gray-600, hover:bg-gray-100, dark:hover:bg-gray-700) */}
          <button
            onClick={reset}
            className="mt-4 rounded-lg border border-gray-400 bg-white dark:bg-gray-800 dark:border-gray-600 px-6 py-2 text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors shadow-sm"
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
