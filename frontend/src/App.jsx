import { useEffect, useMemo, useState } from 'react';
import { BUILDINGS } from './data/board.js';
import { findRoute } from './utils/routing.js';
import useGeolocation from './hooks/useGeolocation.js';
import BoardMap from './components/BoardMap.jsx';
import ControlPanel from './components/ControlPanel.jsx';
import RouteSummary from './components/RouteSummary.jsx';
import './App.css';

export default function App() {
  const [startId, setStartId] = useState(null);
  const [endId, setEndId] = useState(null);
  const [startEntranceId, setStartEntranceId] = useState(null);
  const [endEntranceId, setEndEntranceId] = useState(null);
  const [avoidStairs, setAvoidStairs] = useState(false);
  const [navigating, setNavigating] = useState(false);
  const [liveTracking, setLiveTracking] = useState(false);
  const { position: userPosition, status: locationStatus, start: startLocation } = useGeolocation();

  const start = BUILDINGS.find((b) => b.id === startId) ?? null;
  const end = BUILDINGS.find((b) => b.id === endId) ?? null;
  const sameBuilding = Boolean(startId && endId && startId === endId);

  // Default to the first real entrance whenever the building changes —
  // routing to an actual door is more accurate than the building's
  // centroid, so there's always a sensible choice pre-selected rather than
  // defaulting to "no entrance picked."
  const handleStartChange = (b) => {
    setStartId(b?.id ?? null);
    setStartEntranceId(b?.entrances?.[0]?.id ?? null);
  };
  const handleEndChange = (b) => {
    setEndId(b?.id ?? null);
    setEndEntranceId(b?.entrances?.[0]?.id ?? null);
  };

  const startEntrance = start?.entrances?.find((e) => e.id === startEntranceId) ?? null;
  const endEntrance = end?.entrances?.find((e) => e.id === endEntranceId) ?? null;

  const route = useMemo(() => {
    if (!startId || !endId || sameBuilding) return null;
    return findRoute(startId, endId, !avoidStairs, startEntrance, endEntrance);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startId, endId, avoidStairs, sameBuilding, startEntranceId, endEntranceId]);

  // A route change (new stops, stairs toggled) mid-navigation would pull
  // the camera out from under a route that no longer exists — leave nav
  // mode instead of following a route that just vanished underneath it.
  useEffect(() => {
    if (!route) {
      setNavigating(false);
      setLiveTracking(false);
    }
  }, [route]);

  const noRouteWarning = Boolean(startId && endId && !sameBuilding && !route);

  return (
    <div className="app-shell">
      <BoardMap
        route={route}
        startId={startId}
        endId={endId}
        navigating={navigating}
        liveTracking={liveTracking}
        destinationName={end?.name}
        userPosition={userPosition}
        locationStatus={locationStatus}
        onRequestLocation={startLocation}
      />
      <RouteSummary
        route={route}
        destinationName={end?.name}
        navigating={navigating}
        liveTracking={liveTracking}
        onStart={() => setNavigating(true)}
        onStartLive={() => {
          startLocation();
          setLiveTracking(true);
        }}
        onEnd={() => {
          setNavigating(false);
          setLiveTracking(false);
        }}
      />
      {!navigating && !liveTracking && (
        <ControlPanel
          buildings={BUILDINGS}
          start={start}
          end={end}
          onStartChange={handleStartChange}
          onEndChange={handleEndChange}
          startEntranceId={startEntranceId}
          onStartEntranceChange={setStartEntranceId}
          endEntranceId={endEntranceId}
          onEndEntranceChange={setEndEntranceId}
          avoidStairs={avoidStairs}
          onAvoidStairsChange={setAvoidStairs}
          sameBuildingWarning={sameBuilding}
          noRouteWarning={noRouteWarning}
          userPosition={userPosition}
          locationStatus={locationStatus}
          onNeedLocation={startLocation}
        />
      )}
    </div>
  );
}