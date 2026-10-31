import { useEffect, useMemo, useState } from 'react';
import { fetchMap, fetchRoute } from './api/client.js';
import useGeolocation from './hooks/useGeolocation.js';
import BoardMap from './components/BoardMap.jsx';
import CompassIndicator from './components/CompassIndicator.jsx';
import ControlPanel from './components/ControlPanel.jsx';
import RouteSummary from './components/RouteSummary.jsx';

export default function App() {
  const [mapData, setMapData] = useState(null);
  const [mapError, setMapError] = useState(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [startId, setStartId] = useState(null);
  const [endId, setEndId] = useState(null);
  const [startEntranceId, setStartEntranceId] = useState(null);
  const [endEntranceId, setEndEntranceId] = useState(null);
  const [avoidStairs, setAvoidStairs] = useState(false);
  const [routeResult, setRouteResult] = useState(null);
  const [routeFailure, setRouteFailure] = useState(null);
  const [navigating, setNavigating] = useState(false);
  const [liveTracking, setLiveTracking] = useState(false);
  const { position: userPosition, status: locationStatus, start: startLocation } = useGeolocation();
  const trackingActive = liveTracking && locationStatus === 'ready' && Boolean(userPosition);

  useEffect(() => {
    const controller = new AbortController();
    fetchMap(controller.signal)
      .then((data) => {
        if (!Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
          throw new Error('The map data response is incomplete.');
        }
        if (!data.nodes.length) throw new Error('No campus map locations are available yet.');
        setMapData(data);
      })
      .catch((error) => {
        if (error.name !== 'AbortError') setMapError(error.message);
      });
    return () => controller.abort();
  }, [reloadKey]);

  const buildings = useMemo(
    () => (mapData?.nodes ?? []).filter((node) => node.type === 'location' || node.type === 'entrance'),
    [mapData],
  );
  const start = buildings.find((building) => building.id === startId) ?? null;
  const end = buildings.find((building) => building.id === endId) ?? null;
  const sameBuilding = Boolean(startId && endId && startId === endId);
  const routeKey = startId && endId && !sameBuilding && mapData
    ? JSON.stringify([startId, endId, startEntranceId, endEntranceId, avoidStairs])
    : null;
  const route = routeResult?.key === routeKey ? routeResult.value : null;
  const activeRouteFailure = routeFailure?.key === routeKey ? routeFailure : null;
  const routeLoading = Boolean(routeKey && routeResult?.key !== routeKey && !activeRouteFailure);
  const routeError = activeRouteFailure?.status === 'error' ? activeRouteFailure.message : null;
  const routeNotFound = activeRouteFailure?.status === 'not-found';

  const handleStartChange = (building) => {
    setNavigating(false);
    setLiveTracking(false);
    setStartId(building?.id ?? null);
    setStartEntranceId(building?.nearestEntranceId ?? building?.entrances?.[0]?.id ?? null);
  };
  const handleEndChange = (building) => {
    setNavigating(false);
    setLiveTracking(false);
    setEndId(building?.id ?? null);
    setEndEntranceId(building?.nearestEntranceId ?? building?.entrances?.[0]?.id ?? null);
  };

  // Clicking a pin on the map is a shortcut for the same two fields: first
  // click picks the start, the next click picks the end. Once both are set,
  // re-clicking whichever pin is already picked clears just that one field
  // (so you can swap it out) rather than discarding the other selection —
  // clicking the start pin was clearing the destination, which reads as
  // clearing the wrong field. Clicking any other, unpicked pin starts a
  // fresh pick rather than doing nothing.
  const handlePinClick = (building) => {
    if (navigating || trackingActive) return;
    if (!startId) {
      handleStartChange(building);
    } else if (!endId) {
      handleEndChange(building);
    } else if (building.id === startId) {
      handleStartChange(null);
    } else if (building.id === endId) {
      handleEndChange(null);
    } else {
      handleStartChange(building);
      handleEndChange(null);
    }
  };

  useEffect(() => {
    if (!startId || !endId || sameBuilding || !mapData) {
      return undefined;
    }

    const controller = new AbortController();
    fetchRoute({
      startId,
      destinationId: endId,
      startEntranceId,
      destinationEntranceId: endEntranceId,
      avoidStairs,
    }, controller.signal)
      .then((value) => {
        setRouteFailure(null);
        setRouteResult({ key: routeKey, value });
      })
      .catch((error) => {
        if (error.name === 'AbortError') return;
        setRouteFailure({
          key: routeKey,
          status: error.status === 404 ? 'not-found' : 'error',
          message: error.message,
        });
      });
    return () => controller.abort();
  }, [startId, endId, startEntranceId, endEntranceId, avoidStairs, sameBuilding, mapData, routeKey]);

  if (!mapData && !mapError) {
    return <div className="app-status" role="status">Loading campus map…</div>;
  }
  if (!mapData) {
    return (
      <div className="app-status" role="alert">
        <p>Campus map data could not be loaded: {mapError}</p>
        <button type="button" onClick={() => {
          setMapError(null);
          setReloadKey((key) => key + 1);
        }}>Try again</button>
      </div>
    );
  }

  const noRouteWarning = Boolean(startId && endId && !sameBuilding && routeNotFound);

  return (
    <div className="app-shell">
      <BoardMap
        route={route}
        buildings={buildings}
        graphNodes={mapData.nodes}
        graphEdges={mapData.edges}
        startId={startId}
        endId={endId}
        navigating={navigating}
        liveTracking={trackingActive}
        destinationName={end?.name}
        userPosition={userPosition}
        locationStatus={locationStatus}
        onRequestLocation={startLocation}
        onPinClick={handlePinClick}
      />
      <div className="app-overlay-layer">
        <CompassIndicator />
        {!routeLoading && route && (
          <RouteSummary
            route={route}
            destinationName={end?.name}
            navigating={navigating}
            liveTracking={trackingActive}
            locationStatus={locationStatus}
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
        )}
        {!navigating && !trackingActive && (
          <ControlPanel
            buildings={buildings}
            start={start}
            end={end}
            onStartChange={handleStartChange}
            onEndChange={handleEndChange}
            startEntranceId={startEntranceId}
            onStartEntranceChange={setStartEntranceId}
            endEntranceId={endEntranceId}
            onEndEntranceChange={setEndEntranceId}
            avoidStairs={avoidStairs}
            onAvoidStairsChange={(value) => {
              setNavigating(false);
              setLiveTracking(false);
              setAvoidStairs(value);
            }}
            sameBuildingWarning={sameBuilding}
            noRouteWarning={noRouteWarning}
            noRouteMessage={noRouteWarning ? activeRouteFailure?.message : null}
            routeLoading={routeLoading}
            routeError={routeError}
            userPosition={userPosition}
            locationStatus={locationStatus}
            onNeedLocation={startLocation}
          />
        )}
      </div>
    </div>
  );
}
