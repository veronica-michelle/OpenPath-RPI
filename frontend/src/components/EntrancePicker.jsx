// Only renders when the building actually has more than one tagged
// entrance — forcing a choice when there's only one real door would be
// asking the user to confirm a fact, not make a decision.
export default function EntrancePicker({ label, entrances, selectedId, onChange }) {
  if (!entrances || entrances.length < 2) return null;

  return (
    <div className="entrance-picker" data-no-pan>
      <span className="entrance-picker-label">{label}</span>
      <div className="entrance-picker-options">
        {entrances.map((entrance) => (
          <button
            key={entrance.id}
            type="button"
            className={`entrance-chip${entrance.id === selectedId ? ' is-active' : ''}`}
            onClick={() => onChange(entrance.id)}
            aria-pressed={entrance.id === selectedId}
          >
            {entrance.accessible === true && (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" role="img" aria-label="Marked wheelchair accessible" style={{ flexShrink: 0 }}>
                <title>Marked wheelchair accessible</title>
                <circle cx="11" cy="3" r="2" />
                <path d="M19 13v-2h-6V7a2 2 0 0 0-4 0v6a2 2 0 0 0 2 2h7v5h2v-7h-1Z" />
                <path d="M7 10.3v2.1A4 4 0 1 0 13.6 17h2.1A6 6 0 1 1 7 10.3Z" />
              </svg>
            )}
            {entrance.label || entrance.id}
          </button>
        ))}
      </div>
    </div>
  );
}
