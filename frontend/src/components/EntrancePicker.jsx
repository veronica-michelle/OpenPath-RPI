// Accessibility status per entrance is real survey data from the backend
// (`accessible: true | false | null`), not a cosmetic flag — surfacing it
// here is the whole point of letting someone choose an entrance at all.
// `null` means unverified, never "assume accessible" (see DATASET.md): it
// gets a quiet, distinct treatment, not silence and not a false positive.

function AccessibleIcon() {
  return (
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
  );
}

function InaccessibleIcon() {
  return (
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
      <path d="M3 3l18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function UnverifiedIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6" />
      <text x="12" y="16.5" textAnchor="middle" fontSize="12.5" fontWeight="700" fill="currentColor">
        ?
      </text>
    </svg>
  );
}

function accessibilityMeta(entrance) {
  if (entrance.accessible === true) {
    return { icon: <AccessibleIcon />, chipClass: 'is-accessible', statusText: 'wheelchair accessible' };
  }
  if (entrance.accessible === false) {
    return { icon: <InaccessibleIcon />, chipClass: 'is-inaccessible', statusText: 'not wheelchair accessible' };
  }
  return { icon: <UnverifiedIcon />, chipClass: 'is-unverified', statusText: 'accessibility not verified' };
}

// Only renders when the building actually has more than one tagged
// entrance — forcing a choice when there's only one real door would be
// asking the user to confirm a fact, not make a decision.
export default function EntrancePicker({ label, entrances, selectedId, onChange }) {
  if (!entrances || entrances.length < 2) return null;

  return (
    <div className="entrance-picker" data-no-pan>
      <span className="entrance-picker-label">{label}</span>
      <div className="entrance-picker-options">
        {entrances.map((entrance) => {
          const { icon, chipClass, statusText } = accessibilityMeta(entrance);
          const isActive = entrance.id === selectedId;
          return (
            <button
              key={entrance.id}
              type="button"
              className={`entrance-chip ${chipClass}${isActive ? ' is-active' : ''}`}
              onClick={() => onChange(entrance.id)}
              aria-pressed={isActive}
              aria-label={`${entrance.label} entrance, ${statusText}`}
            >
              {icon}
              {entrance.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
