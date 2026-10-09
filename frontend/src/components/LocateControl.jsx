export default function LocateControl({ onLocate, status }) {
  const locating = status === 'locating';
  const label = locating ? 'Finding your location' : 'Show my location';

  return (
    <button
      type="button"
      className={`locate-btn${locating ? ' is-locating' : ''}${status === 'denied' ? ' is-denied' : ''}`}
      onClick={onLocate}
      aria-label={label}
      title={label}
      disabled={locating}
    >
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
        <path d="M12 2v3m0 14v3M2 12h3m14 0h3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    </button>
  );
}
