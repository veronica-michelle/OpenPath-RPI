import { useCallback, useEffect, useRef, useState } from 'react';

const WATCH_OPTIONS = {
  enableHighAccuracy: true,
  maximumAge: 4000,
  timeout: 12000,
};

// Live GPS watch for the mobile walking case. Starts only when `start()`
// is called (locate button / opening the start field) so we don't pop a
// permission prompt the instant the desktop map loads.
export default function useGeolocation() {
  const [position, setPosition] = useState(null);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('idle');
  const watchId = useRef(null);

  const start = useCallback(() => {
    if (typeof navigator === 'undefined' || !navigator.geolocation) {
      setStatus('unsupported');
      setError('Location is not available in this browser.');
      return;
    }
    if (watchId.current != null) return;

    setStatus((s) => (s === 'ready' ? s : 'locating'));
    watchId.current = navigator.geolocation.watchPosition(
      (pos) => {
        setPosition({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
          heading: Number.isFinite(pos.coords.heading) ? pos.coords.heading : null,
        });
        setError(null);
        setStatus('ready');
      },
      (err) => {
        setStatus(err.code === 1 ? 'denied' : 'error');
        setError(err.message);
      },
      WATCH_OPTIONS,
    );
  }, []);

  useEffect(
    () => () => {
      if (watchId.current != null && navigator.geolocation) {
        navigator.geolocation.clearWatch(watchId.current);
        watchId.current = null;
      }
    },
    [],
  );

  return { position, error, status, start };
}
