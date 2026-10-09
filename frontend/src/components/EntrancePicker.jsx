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
            {entrance.wheelchair && (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <circle cx="12" cy="4" r="2" fill="currentColor" />
                <path
                  d="M12 8v5l5 3M11 13H6a3 3 0 1 0 2.8 4"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              </svg>
            )}
            {entrance.label}
          </button>
        ))}
      </div>
    </div>
  );
}
