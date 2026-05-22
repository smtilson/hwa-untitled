const DEFAULT_HEAT = 0;
const DEFAULT_SHARDS = 5;

const trackersContainer = document.getElementById('trackers');
const resetBtn = document.getElementById('reset');

const heatTracker = createTracker({
  label: 'Heat',
  value: DEFAULT_HEAT,
});

const shardsTracker = createTracker({
  label: 'Shards',
  value: DEFAULT_SHARDS,
});

trackersContainer.append(heatTracker.element, shardsTracker.element);

resetBtn.addEventListener('click', () => {
  heatTracker.setValue(DEFAULT_HEAT);
  shardsTracker.setValue(DEFAULT_SHARDS);
});
