import { useState } from 'react';

export default function ThemeToggle({ theme, onToggle }) {
  const [expanded, setExpanded] = useState(false);
  const dark = theme === 'dark';
  return (
    <button
      type="button"
      className={`theme-toggle${expanded ? ' is-expanded' : ''}`}
      onClick={() => expanded ? onToggle() : setExpanded(true)}
      aria-label={expanded ? `Dark mode: ${dark ? 'on' : 'off'}. Click to toggle.` : 'Show dark mode control'}
      aria-expanded={expanded}
      aria-pressed={expanded ? dark : undefined}
      data-no-pan
    >
      <span aria-hidden="true">{dark ? '☾' : '☀'}</span>
      {expanded && <span>Dark mode: {dark ? 'on' : 'off'}</span>}
    </button>
  );
}
