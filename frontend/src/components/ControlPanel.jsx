import EntrancePicker from './EntrancePicker.jsx';
import SearchField from './SearchField.jsx';
import StairsToggle from './StairsToggle.jsx';

export default function ControlPanel({
  buildings,
  start,
  end,
  onStartChange,
  onEndChange,
  startEntranceId,
  onStartEntranceChange,
  endEntranceId,
  onEndEntranceChange,
  avoidStairs,
  onAvoidStairsChange,
  sameBuildingWarning,
  noRouteWarning,
  userPosition,
  locationStatus,
  onNeedLocation,
}) {
  return (
    <section className="control-panel" aria-label="Route controls" data-no-pan>
      <header className="control-panel-header">
        <span className="brand-wordmark">OpenPath</span>
        <span className="brand-subtitle">Accessible RPI Routes</span>
      </header>

      <div className="control-panel-fields">
        <SearchField
          label="Starting point"
          dotClass="search-dot-start"
          buildings={buildings}
          value={start}
          onChange={onStartChange}
          excludeId={end?.id}
          placeholder="Choose starting point"
          userPosition={userPosition}
          onNeedLocation={onNeedLocation}
          showNearestShortcut
        />
        <EntrancePicker
          label="Start entrance"
          entrances={start?.entrances}
          selectedId={startEntranceId}
          onChange={onStartEntranceChange}
        />
        <SearchField
          label="Destination"
          dotClass="search-dot-end"
          buildings={buildings}
          value={end}
          onChange={onEndChange}
          excludeId={start?.id}
          placeholder="Choose destination"
          userPosition={userPosition}
          onNeedLocation={onNeedLocation}
        />
        <EntrancePicker
          label="Destination entrance"
          entrances={end?.entrances}
          selectedId={endEntranceId}
          onChange={onEndEntranceChange}
        />
      </div>

      {locationStatus === 'denied' && (
        <p className="control-panel-hint" role="status">
          Location is blocked — allow it in the browser to sort nearby entrances.
        </p>
      )}
      {locationStatus === 'unsupported' && (
        <p className="control-panel-hint" role="status">
          This browser cannot share location.
        </p>
      )}
      {locationStatus === 'locating' && (
        <p className="control-panel-hint" role="status">
          Finding your location…
        </p>
      )}
      {locationStatus === 'ready' && (
        <p className="control-panel-hint" role="status">
          Nearby entrances are listed closest first.
        </p>
      )}

      <StairsToggle checked={avoidStairs} onChange={onAvoidStairsChange} />

      {sameBuildingWarning && (
        <p className="control-panel-warning" role="alert">
          Start and end are the same building — pick two different stops.
        </p>
      )}
      {noRouteWarning && (
        <p className="control-panel-warning" role="alert">
          No accessible path found between these buildings.
        </p>
      )}
    </section>
  );
}
