export default function ThemeToggle({ theme, onToggle }) {
  const dark = theme === 'dark';
  return (
    <button type="button" className="theme-toggle" onClick={onToggle} aria-pressed={dark} data-no-pan>
      <span aria-hidden="true">{dark ? '☾' : '☀'}</span>
      <span>Dark mode: {dark ? 'on' : 'off'}</span>
    </button>
  );
}