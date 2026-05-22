/**
 * Reusable Tracker component (vanilla JS).
 *
 * Creates a DOM element with a label/value box and +/- buttons.
 * Returns an object with the root element and a setValue method.
 *
 * @param {Object} options
 * @param {string} options.label - Display label (e.g. "Heat", "Shards")
 * @param {number} options.value - Initial value
 * @param {(newValue: number) => void} [options.onChange] - Called whenever value changes
 * @param {number} [options.min=0] - Minimum value (decrement clamps here)
 * @returns {{ element: HTMLElement, getValue: () => number, setValue: (v: number) => void }}
 */
function createTracker({ label, value, onChange, min = 0 }) {
  let current = value;

  const root = document.createElement('div');
  root.className = 'tracker';

  const box = document.createElement('div');
  box.className = 'tracker__box';

  const labelEl = document.createElement('span');
  labelEl.className = 'tracker__label';
  labelEl.textContent = label;

  const valueEl = document.createElement('span');
  valueEl.className = 'tracker__value';
  valueEl.textContent = String(current);

  box.append(labelEl, valueEl);

  const buttons = document.createElement('div');
  buttons.className = 'tracker__buttons';

  const decBtn = document.createElement('button');
  decBtn.type = 'button';
  decBtn.className = 'tracker__btn';
  decBtn.textContent = '-';
  decBtn.setAttribute('aria-label', `Decrease ${label}`);

  const incBtn = document.createElement('button');
  incBtn.type = 'button';
  incBtn.className = 'tracker__btn';
  incBtn.textContent = '+';
  incBtn.setAttribute('aria-label', `Increase ${label}`);

  buttons.append(decBtn, incBtn);
  root.append(box, buttons);

  function setValue(next) {
    current = Math.max(min, next);
    valueEl.textContent = String(current);
    if (onChange) onChange(current);
  }

  decBtn.addEventListener('click', () => setValue(current - 1));
  incBtn.addEventListener('click', () => setValue(current + 1));

  return {
    element: root,
    getValue: () => current,
    setValue,
  };
}
