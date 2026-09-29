import { formatDistance } from '../utils/metrics.js';

export default function RouteSummary({
  route,
  destinationName,
  navigating,
  liveTracking,
  onStart,
  onStartLive,
  onEnd,
}) {
  if (!route) return null;

  const minutes = route.minutes;
  const gain = Math.round(route.elevationGainFt);
  const active = navigating || liveTracking;

  return (
    <section className="route-summary" aria-label="Route summary" data-no-pan>
      {active ? (
        <div className="route-summary-time">
          {liveTracking ? 'Tracking to' : 'Navigating to'} {destinationName}
        </div>
      ) : (
        <div className="route-summary-time">Estimated Time: {minutes} mins</div>
      )}
      <div className="route-summary-row">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 2v20M2 12h20" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" transform="rotate(45 12 12)" />
        </svg>
        Distance: {formatDistance(route.distanceFt)}
      </div>
      <div className="route-summary-row">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M4 18 10 8l4 6 3-4 3 8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Elevation: {gain} ft ({route.steepness})
      </div>

      {active ? (
        <button type="button" className="route-summary-btn route-summary-btn-end" onClick={onEnd} data-no-pan>
          End
        </button>
      ) : (
        <div className="route-summary-btn-row">
          <button type="button" className="route-summary-btn route-summary-btn-start" onClick={onStart} data-no-pan>
            Preview
          </button>
          <button type="button" className="route-summary-btn route-summary-btn-live" onClick={onStartLive} data-no-pan>
            Start
          </button>
        </div>
      )}
    </section>
  );
}