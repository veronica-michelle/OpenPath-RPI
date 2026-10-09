async function request(path, options) {
  const response = await fetch(path, {
    headers: { Accept: 'application/json', ...(options?.body ? { 'Content-Type': 'application/json' } : {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.detail ?? `The server returned ${response.status}.`);
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
