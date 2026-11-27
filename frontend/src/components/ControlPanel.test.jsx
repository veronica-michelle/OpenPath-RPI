// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import ControlPanel from './ControlPanel.jsx';

afterEach(cleanup);

// The children have their own behavior, so stub them and test only what
// ControlPanel does: pass the right props down and show the right messages.
vi.mock('./SearchField.jsx', () => ({
  default: ({ label, excludeId, showNearestShortcut }) => (
    <div
      data-testid={`search-${label}`}
      data-exclude={excludeId ?? ''}
      data-shortcut={String(Boolean(showNearestShortcut))}
    />
  ),
}));
vi.mock('./EntrancePicker.jsx', () => ({
  default: ({ label, entrances, selectedId, onChange }) => (
    <button
      type="button"
      data-testid={`picker-${label}`}
      data-count={entrances?.length ?? 0}
      data-selected={selectedId ?? ''}
      onClick={() => onChange('east')}
    />
  ),
}));
vi.mock('./StairsToggle.jsx', () => ({
  default: ({ checked, onChange }) => (
    <input
      type="checkbox"
      aria-label="Avoid stairs"
      checked={checked}
      onChange={(e) => onChange(e.target.checked)}
    />
  ),
}));

const hall = { id: 'hall', name: 'Hall', entrances: [{ id: 'west' }, { id: 'east' }] };
const lab = { id: 'lab', name: 'Lab' };

function setup(props = {}) {
  const handlers = {
    onStartChange: vi.fn(),
    onEndChange: vi.fn(),
    onStartEntranceChange: vi.fn(),
    onEndEntranceChange: vi.fn(),
    onAvoidStairsChange: vi.fn(),
    onNeedLocation: vi.fn(),
  };
  render(
    <ControlPanel
      buildings={[hall, lab]}
      start={hall}
      end={lab}
      startEntranceId="west"
      endEntranceId={null}
      avoidStairs={false}
      {...handlers}
      {...props}
    />,
  );
  return handlers;
}

describe('ControlPanel wiring', () => {
  it('is a labelled region', () => {
    setup();
    expect(screen.getByRole('region', { name: 'Route controls' })).toBeTruthy();
  });

  it('excludes the other field\'s building from each search field', () => {
    setup();
    expect(screen.getByTestId('search-Starting point').dataset.exclude).toBe('lab');
    expect(screen.getByTestId('search-Destination').dataset.exclude).toBe('hall');
  });

  it('offers the nearest shortcut only on the starting point', () => {
    setup();
    expect(screen.getByTestId('search-Starting point').dataset.shortcut).toBe('true');
    expect(screen.getByTestId('search-Destination').dataset.shortcut).toBe('false');
  });

  it('gives each entrance picker its building\'s entrances and selection', () => {
    setup();
    const startPicker = screen.getByTestId('picker-Start entrance');
    expect(startPicker.dataset.count).toBe('2');
    expect(startPicker.dataset.selected).toBe('west');
    expect(screen.getByTestId('picker-Destination entrance').dataset.count).toBe('0');
  });

  it('reports entrance and stairs changes', () => {
    const h = setup();
    fireEvent.click(screen.getByTestId('picker-Start entrance'));
    fireEvent.click(screen.getByTestId('picker-Destination entrance'));
    fireEvent.click(screen.getByLabelText('Avoid stairs'));
    expect(h.onStartEntranceChange).toHaveBeenCalledWith('east');
    expect(h.onEndEntranceChange).toHaveBeenCalledWith('east');
    expect(h.onAvoidStairsChange).toHaveBeenCalledWith(true);
  });
});

describe('ControlPanel location messages', () => {
  it.each([
    ['denied', /blocked/i],
    ['unsupported', /cannot share location/i],
    ['locating', /finding your location/i],
    ['ready', /closest first/i],
    ['error', /could not be found/i],
  ])('shows the %s message as a status', (status, pattern) => {
    setup({ locationStatus: status });
    expect(screen.getByText(pattern).getAttribute('role')).toBe('status');
  });

  it('shows no location message while idle', () => {
    setup({ locationStatus: 'idle' });
    expect(screen.queryAllByRole('status')).toHaveLength(0);
  });

  it('shows only one location message at a time', () => {
    setup({ locationStatus: 'denied' });
    expect(screen.getAllByRole('status')).toHaveLength(1);
  });
});

describe('ControlPanel route messages', () => {
  it('announces loading as a status', () => {
    setup({ routeLoading: true });
    expect(screen.getByText(/finding a route/i).getAttribute('role')).toBe('status');
  });

  it('shows a failed request as an alert with the reason', () => {
    setup({ routeError: 'timeout' });
    expect(screen.getByRole('alert').textContent).toBe('Route request failed: timeout');
  });

  it('shows the default no-path message as an alert', () => {
    setup({ noRouteWarning: true });
    expect(screen.getByRole('alert').textContent).toMatch(/no accessible path/i);
  });

  it('shows the backend\'s message instead when there is one', () => {
    setup({ noRouteWarning: true, noRouteMessage: 'No stair-free route found' });
    expect(screen.getByRole('alert').textContent).toBe('No stair-free route found');
  });

  it('does not report a failed request as "no path"', () => {
    setup({ routeError: 'server down', noRouteWarning: false });
    expect(screen.queryByText(/no accessible path/i)).toBeNull();
  });

  it('warns when start and destination are the same', () => {
    setup({ sameBuildingWarning: true });
    expect(screen.getByRole('alert').textContent).toMatch(/choose two different locations/i);
  });

  it('shows no alerts when everything is fine', () => {
    setup();
    expect(screen.queryAllByRole('alert')).toHaveLength(0);
  });
});