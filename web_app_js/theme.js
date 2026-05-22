/**
 * Theme toggle: switches between light and dark via a `data-theme`
 * attribute on the <html> element. Persists to localStorage.
 * Falls back to the user's system preference when no choice is stored.
 */
(function () {
  const STORAGE_KEY = 'hwa-theme';
  const root = document.documentElement;

  function systemPrefersDark() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function getStoredTheme() {
    return localStorage.getItem(STORAGE_KEY);
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
      btn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }
  }

  // Initialize on load
  const initial = getStoredTheme() || (systemPrefersDark() ? 'dark' : 'light');
  applyTheme(initial);

  function toggleTheme() {
    const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }

  // Wire up the button once DOM is ready
  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(root.getAttribute('data-theme') || initial);
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', toggleTheme);
  });
})();
