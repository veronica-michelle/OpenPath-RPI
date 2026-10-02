// Static north indicator — the map is always north-up (Leaflet has no
// native rotation and we deliberately didn't bolt one on), so this is
// informational only, not a control: no drag, no click action.
export default function CompassIndicator() {
  return (
    <div className="compass-indicator" aria-hidden="true">
      <svg width="26" height="26" viewBox="0 0 26 26">
        <path d="M13 3 L17 13 L13 10 L9 13 Z" fill="var(--map-accent)" />
        <path d="M13 23 L17 13 L13 16 L9 13 Z" fill="var(--map-border-strong)" />
      </svg>
      <span className="compass-indicator-label">N</span>
    </div>
  );
}
