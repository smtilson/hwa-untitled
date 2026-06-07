import { useImperativeHandle, useState, forwardRef } from 'react';
import Tracker from './Tracker';

export interface PlayerPanelHandle {
  reset: () => void;
}

interface PlayerPanelProps {
  playerNumber: number;
  defaultHeat?: number;
  defaultShards?: number;
}

const DEFAULT_HEAT = 0;
const DEFAULT_SHARDS = 5;

const PlayerPanel = forwardRef<PlayerPanelHandle, PlayerPanelProps>(
  ({ playerNumber, defaultHeat = DEFAULT_HEAT, defaultShards = DEFAULT_SHARDS }, ref) => {
    const [heat, setHeat] = useState(defaultHeat);
    const [shards, setShards] = useState(defaultShards);

    useImperativeHandle(ref, () => ({
      reset: () => {
        setHeat(defaultHeat);
        setShards(defaultShards);
      },
    }));

    return (
      <section className="flex flex-col items-center gap-6 p-6 rounded-lg border border-gray-400 bg-white dark:border-gray-600 dark:bg-gray-800 w-full max-w-sm">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white m-0">
          Player {playerNumber}
        </h2>
        <Tracker
          label={`P${playerNumber} Heat`}
          value={heat}
          onIncrement={() => setHeat((v) => v + 1)}
          onDecrement={() => setHeat((v) => Math.max(0, v - 1))}
        />
        <Tracker
          label={`P${playerNumber} Shards`}
          value={shards}
          onIncrement={() => setShards((v) => v + 1)}
          onDecrement={() => setShards((v) => Math.max(0, v - 1))}
        />
      </section>
    );
  }
);

PlayerPanel.displayName = 'PlayerPanel';

export default PlayerPanel;
