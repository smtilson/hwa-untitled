const DEFAULT_HEAT = 0;
const DEFAULT_SHARDS = 5;
const NUM_PLAYERS = 2;

const playersContainer = document.getElementById('players');
const resetBtn = document.getElementById('reset');

/**
 * Build a player panel with Heat + Shards trackers.
 * @param {number} playerNumber
 * @returns {{ element: HTMLElement, reset: () => void }}
 */
function createPlayerPanel(playerNumber) {
  const panel = document.createElement('section');
  panel.className = 'player';

  const heading = document.createElement('h2');
  heading.className = 'player__heading';
  heading.textContent = `Player ${playerNumber}`;
  panel.appendChild(heading);

  const heat = createTracker({
    label: `P${playerNumber} Heat`,
    value: DEFAULT_HEAT,
  });
  const shards = createTracker({
    label: `P${playerNumber} Shards`,
    value: DEFAULT_SHARDS,
  });

  panel.append(heat.element, shards.element);

  return {
    element: panel,
    reset: () => {
      heat.setValue(DEFAULT_HEAT);
      shards.setValue(DEFAULT_SHARDS);
    },
  };
}

const panels = [];
for (let i = 1; i <= NUM_PLAYERS; i++) {
  const panel = createPlayerPanel(i);
  panels.push(panel);
  playersContainer.appendChild(panel.element);
}

resetBtn.addEventListener('click', () => {
  panels.forEach((p) => p.reset());
});
