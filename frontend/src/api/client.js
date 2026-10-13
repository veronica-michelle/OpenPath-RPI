async function request(path, options) {
  let response;
  try {
    response = await fetch(path, {
      headers: { Accept: 'application/json', ...(options?.body ? { 'Content-Type': 'application/json' } : {}) },
      ...options,
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Could not reach the campus API. Start Django on port 8000 or run Docker Compose from the repository root.');
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = response.status === 502 || response.status === 503
      ? 'The campus API is not running. Start Django on port 8000 or run Docker Compose from the repository root.'
      : payload.detail ?? `The server returned ${response.status}.`;
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return payload;
}

export function fetchMap(signal) {
  return request('/api/map/', { signal });
}

export function fetchRoute({ startId, destinationId, startEntranceId, destinationEntranceId, avoidStairs }, signal) {
  return request('/api/route/', {
    method: 'POST',
    signal,
    body: JSON.stringify({
      start_id: startId,
      destination_id: destinationId,
      start_entrance_id: startEntranceId ?? '',
      destination_entrance_id: destinationEntranceId ?? '',
      avoid_stairs: avoidStairs,
    }),
  });
}
