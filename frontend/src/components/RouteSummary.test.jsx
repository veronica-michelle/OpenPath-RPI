// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import RouteSummary from './RouteSummary.jsx';

afterEach(cleanup);

const route = {
  minutes: 7,
  distanceFt: 300,
  elevationGainFt: 12.4,
  steepness: 'flat',
};

describe('RouteSummary', () => {
  it('renders nothing when there is no route', () => {
    const { container } = render(
      <RouteSummary
        route={null}
        destinationName="Lab"
        navigating={false}
        liveTracking={false}
        locationStatus="idle"
        onStart={vi.fn()}
        onStartLive={vi.fn()}
        onEnd={vi.fn()}
      />,
    );
    expect(container.firstChild).toBeNull();
  });

  it('shows the estimate and both actions when idle, and wires them up', () => {
    const onStart = vi.fn();
    const onStartLive = vi.fn();
    render(
      <RouteSummary
        route={route}
        destinationName="Lab"
        navigating={false}
        liveTracking={false}
        locationStatus="idle"
        onStart={onStart}
        onStartLive={onStartLive}
        onEnd={vi.fn()}
      />,
    );
    expect(screen.getByText('Estimated Time: 7 mins')).not.toBeNull();
    expect(screen.getByText(/Distance: 300 ft/)).not.toBeNull();
    expect(screen.getByText(/Elevation: 12 ft \(flat\)/)).not.toBeNull();

    fireEvent.click(screen.getByText('Preview'));
    expect(onStart).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByText('Start'));
    expect(onStartLive).toHaveBeenCalledTimes(1);
  });

  it('disables the live-start action while locating', () => {
    render(
      <RouteSummary
        route={route}
        destinationName="Lab"
        navigating={false}
        liveTracking={false}
        locationStatus="locating"
        onStart={vi.fn()}
        onStartLive={vi.fn()}
        onEnd={vi.fn()}
      />,
    );
    const liveButton = screen.getByText('Finding your location…');
    expect(liveButton.disabled).toBe(true);
  });

  it('switches to the active view and lets you end navigation', () => {
    const onEnd = vi.fn();
    render(
      <RouteSummary
        route={route}
        destinationName="Lab"
        navigating
        liveTracking={false}
        locationStatus="idle"
        onStart={vi.fn()}
        onStartLive={vi.fn()}
        onEnd={onEnd}
      />,
    );
    expect(screen.getByText('Navigating to Lab')).not.toBeNull();
    expect(screen.queryByText('Preview')).toBeNull();

    fireEvent.click(screen.getByText('End'));
    expect(onEnd).toHaveBeenCalledTimes(1);
  });

  it('shows the tracking label when live tracking is active', () => {
    render(
      <RouteSummary
        route={route}
        destinationName="Lab"
        navigating={false}
        liveTracking
        locationStatus="ready"
        onStart={vi.fn()}
        onStartLive={vi.fn()}
        onEnd={vi.fn()}
      />,
    );
    expect(screen.getByText('Tracking to Lab')).not.toBeNull();
  });
});
