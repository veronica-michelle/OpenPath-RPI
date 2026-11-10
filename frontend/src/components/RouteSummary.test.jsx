// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import RouteSummary from './RouteSummary.jsx';

// Fixed output so the tests don't depend on how distances are formatted.
vi.mock('../utils/metrics.js', () => ({
  formatDistance: (ft) => `${ft} ft`,
}));

afterEach(cleanup);

const route = { minutes: 7, distanceFt: 500, elevationGainFt: 12.6, steepness: 'gentle' };

function setup(props = {}) {
  const handlers = { onStart: vi.fn(), onStartLive: vi.fn(), onEnd: vi.fn() };
  const utils = render(
    <RouteSummary route={route} destinationName="Lally Hall" {...handlers} {...props} />,
  );
  return { ...utils, ...handlers };
}

describe('RouteSummary with no route', () => {
  it('renders nothing', () => {
    const { container } = setup({ route: null });
    expect(container.firstChild).toBeNull();
  });
});

describe('RouteSummary before starting', () => {
  it('is a labelled region', () => {
    setup();
    expect(screen.getByRole('region', { name: 'Route summary' })).toBeTruthy();
  });

  it('shows the time, distance and elevation', () => {
    setup();
    expect(screen.getByText(/Estimated Time: 7 mins/)).toBeTruthy();
    expect(screen.getByText(/Distance: 500 ft/)).toBeTruthy();
  });

  it('rounds elevation gain to a whole number', () => {
    setup();
    expect(screen.getByText(/Elevation: 13 ft \(gentle\)/)).toBeTruthy();
  });

  it('offers Preview and Start, and no End', () => {
    setup();
    expect(screen.getByRole('button', { name: 'Preview' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Start' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'End' })).toBeNull();
  });

  it('runs the scripted preview from Preview', () => {
    const { onStart, onStartLive } = setup();
    fireEvent.click(screen.getByRole('button', { name: 'Preview' }));
    expect(onStart).toHaveBeenCalledTimes(1);
    expect(onStartLive).not.toHaveBeenCalled();
  });

  it('starts live tracking from Start', () => {
    const { onStart, onStartLive } = setup({ locationStatus: 'ready' });
    fireEvent.click(screen.getByRole('button', { name: 'Start' }));
    expect(onStartLive).toHaveBeenCalledTimes(1);
    expect(onStart).not.toHaveBeenCalled();
  });
});

describe('RouteSummary while finding the location', () => {
  it('disables Start and says why', () => {
    setup({ locationStatus: 'locating' });
    const button = screen.getByRole('button', { name: /finding your location/i });
    expect(button.disabled).toBe(true);
    expect(screen.queryByRole('button', { name: 'Start' })).toBeNull();
  });

  it('does not start tracking when the disabled button is clicked', () => {
    const { onStartLive } = setup({ locationStatus: 'locating' });
    fireEvent.click(screen.getByRole('button', { name: /finding your location/i }));
    expect(onStartLive).not.toHaveBeenCalled();
  });

  it('keeps Preview available', () => {
    const { onStart } = setup({ locationStatus: 'locating' });
    fireEvent.click(screen.getByRole('button', { name: 'Preview' }));
    expect(onStart).toHaveBeenCalledTimes(1);
  });

  it.each(['idle', 'ready', 'denied', 'unsupported', 'error'])(
    'leaves Start enabled when the status is %s',
    (status) => {
      setup({ locationStatus: status });
      expect(screen.getByRole('button', { name: 'Start' }).disabled).toBe(false);
    },
  );
});

describe('RouteSummary while navigating', () => {
  it('shows the preview text and a single End button', () => {
    const { onEnd } = setup({ navigating: true });
    expect(screen.getByText('Navigating to Lally Hall')).toBeTruthy();
    expect(screen.queryByText(/Estimated Time/)).toBeNull();
    expect(screen.queryByRole('button', { name: 'Preview' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Start' })).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'End' }));
    expect(onEnd).toHaveBeenCalledTimes(1);
  });
});

describe('RouteSummary while tracking live', () => {
  it('shows the tracking text and a single End button', () => {
    const { onEnd } = setup({ liveTracking: true });
    expect(screen.getByText('Tracking to Lally Hall')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Start' })).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'End' }));
    expect(onEnd).toHaveBeenCalledTimes(1);
  });

  it('prefers the tracking text if both modes are somehow on', () => {
    setup({ liveTracking: true, navigating: true });
    expect(screen.getByText('Tracking to Lally Hall')).toBeTruthy();
  });

  it('still shows distance and elevation', () => {
    setup({ liveTracking: true });
    expect(screen.getByText(/Distance: 500 ft/)).toBeTruthy();
    expect(screen.getByText(/Elevation: 13 ft/)).toBeTruthy();
  });
});