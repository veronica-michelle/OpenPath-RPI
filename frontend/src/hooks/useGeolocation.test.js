// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import useGeolocation from './useGeolocation.js';

const watchPosition = vi.fn();
const clearWatch = vi.fn();

function setGeolocation(value) {
  Object.defineProperty(globalThis.navigator, 'geolocation', {
    value,
    configurable: true,
  });
}

const successCb = () => watchPosition.mock.calls[0][0];
const errorCb = () => watchPosition.mock.calls[0][1];

beforeEach(() => {
  watchPosition.mockReset();
  clearWatch.mockReset();
  watchPosition.mockReturnValue(42);
  setGeolocation({ watchPosition, clearWatch });
});

describe('useGeolocation', () => {
  it('starts idle with no position', () => {
    const { result } = renderHook(() => useGeolocation());
    expect(result.current.status).toBe('idle');
    expect(result.current.position).toBeNull();
    expect(watchPosition).not.toHaveBeenCalled();
  });

  it('reports unsupported when the browser has no geolocation', () => {
    setGeolocation(undefined);
    const { result } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    expect(result.current.status).toBe('unsupported');
    expect(result.current.error).toMatch(/not available/i);
  });

  it('shows locating after start, before a fix arrives', () => {
    const { result } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    expect(result.current.status).toBe('locating');
    expect(watchPosition).toHaveBeenCalledTimes(1);
  });

  it('only starts one watch when start is called twice', () => {
    const { result } = renderHook(() => useGeolocation());
    act(() => {
      result.current.start();
      result.current.start();
    });
    expect(watchPosition).toHaveBeenCalledTimes(1);
  });

  it('stores the position and becomes ready on a fix', () => {
    const { result } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    act(() =>
      successCb()({ coords: { latitude: 42.73, longitude: -73.68, accuracy: 12, heading: 90 } }),
    );
    expect(result.current.status).toBe('ready');
    expect(result.current.position).toEqual({ lat: 42.73, lng: -73.68, accuracy: 12, heading: 90 });
    expect(result.current.error).toBeNull();
  });

  it('sets heading to null when the device reports none', () => {
    const { result } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    act(() =>
      successCb()({ coords: { latitude: 42.73, longitude: -73.68, accuracy: 5, heading: null } }),
    );
    expect(result.current.position.heading).toBeNull();
  });

  it('sets heading to null when the heading is NaN', () => {
    const { result } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    act(() =>
      successCb()({ coords: { latitude: 42.73, longitude: -73.68, accuracy: 5, heading: NaN } }),
    );
    expect(result.current.position.heading).toBeNull();
  });

  it('reports denied when permission is refused (code 1)', () => {
    const { result } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    act(() => errorCb()({ code: 1, message: 'User denied Geolocation' }));
    expect(result.current.status).toBe('denied');
    expect(result.current.error).toBe('User denied Geolocation');
    expect(result.current.position).toBeNull();
  });

  it('reports a generic error for other failures (code 2 or 3)', () => {
    const { result } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    act(() => errorCb()({ code: 3, message: 'Timeout expired' }));
    expect(result.current.status).toBe('error');
  });

  it('recovers to ready when a fix arrives after an error', () => {
    const { result } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    act(() => errorCb()({ code: 2, message: 'Position unavailable' }));
    act(() =>
      successCb()({ coords: { latitude: 42.73, longitude: -73.68, accuracy: 8, heading: null } }),
    );
    expect(result.current.status).toBe('ready');
    expect(result.current.error).toBeNull();
  });

  it('stops watching when the component unmounts', () => {
    const { result, unmount } = renderHook(() => useGeolocation());
    act(() => result.current.start());
    unmount();
    expect(clearWatch).toHaveBeenCalledWith(42);
  });
});