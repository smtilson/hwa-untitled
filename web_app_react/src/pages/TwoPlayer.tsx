import { useRef } from 'react';
import PlayerPanel, { type PlayerPanelHandle } from '../components/PlayerPanel';

const NUM_PLAYERS = 2;

export default function TwoPlayer() {
  const panelRefs = useRef<(PlayerPanelHandle | null)[]>([]);

  const resetAll = () => {
    panelRefs.current.forEach((panel) => panel?.reset());
  };

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      <div className="flex flex-col sm:flex-row flex-wrap justify-center items-stretch gap-8 w-full">
        {Array.from({ length: NUM_PLAYERS }, (_, i) => (
          <PlayerPanel
            key={i + 1}
            playerNumber={i + 1}
            ref={(el) => {
              panelRefs.current[i] = el;
            }}
          />
        ))}
      </div>
      <button
        onClick={resetAll}
        className="mt-4 rounded-lg border border-gray-400 bg-white dark:bg-gray-800 dark:border-gray-600 px-6 py-2 text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors shadow-sm"
      >
        Reset
      </button>
    </div>
  );
}
