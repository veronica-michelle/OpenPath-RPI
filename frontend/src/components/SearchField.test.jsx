// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import SearchField from './SearchField.jsx';

afterEach(cleanup);

const buildings = [
  { id: 'hall', name: 'Hall', lat: 42, lng: -73, entrances: [
    { id: 'west', lat: 42, lng: -73 }, { id: 'east', lat: 42, lng: -72.998 },
  ] },
  { id: 'lab', name: 'Lab', lat: 42, lng: -72.9995 },
];

describe('SearchField', () => {
  it('nearest shortcut selects the nearest actual door, not the building default', () => {
    const onChange = vi.fn();
    render(<SearchField label="Start" buildings={buildings} value={null} onChange={onChange}
      userPosition={{ lat: 42, lng: -72.998 }} showNearestShortcut />);
    fireEvent.focus(screen.getByRole('combobox'));
    fireEvent.click(screen.getByText('Nearest entrance'));
    expect(onChange.mock.calls[0][0]).toMatchObject({ id: 'hall', nearestEntranceId: 'east' });
  });

  it('keeps keyboard selection valid when filtering shrinks the list', () => {
    const onChange = vi.fn();
    render(<SearchField label="Start" buildings={buildings} value={null} onChange={onChange} />);
    const input = screen.getByRole('combobox');
    fireEvent.focus(input);
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.change(input, { target: { value: 'Hall' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(onChange.mock.calls[0][0].id).toBe('hall');
  });

  it('does not reference a nonexistent active option when there are no matches', () => {
    render(<SearchField label="Start" buildings={buildings} value={null} onChange={vi.fn()} />);
    const input = screen.getByRole('combobox');
    fireEvent.change(input, { target: { value: 'missing' } });
    expect(input.getAttribute('aria-activedescendant')).toBeNull();
  });
});

const listBuildings = [
  { id: 'carnegie', name: 'Carnegie Building', lat: 42.73, lng: -73.68 },
  { id: 'lally', name: 'Lally Hall', lat: 42.729, lng: -73.679 },
  { id: 'amos', name: 'Amos Eaton Hall', lat: 42.7295, lng: -73.6795 },
  { id: 'sage', name: 'Sage Lab', lat: 42.731, lng: -73.681 },
];

// Standing right next to Lally Hall. Nearest to farthest: Lally, Amos, Carnegie, Sage.
const nearLally = { lat: 42.729, lng: -73.6791, accuracy: 5, heading: null };

function setup(props = {}) {
  const onChange = vi.fn();
  const onNeedLocation = vi.fn();
  const utils = render(
    <SearchField
      label="Starting point"
      dotClass="search-dot-start"
      buildings={listBuildings}
      value={null}
      onChange={onChange}
      onNeedLocation={onNeedLocation}
      placeholder="Choose starting point"
      {...props}
    />,
  );
  const input = screen.getByRole('combobox');
  return { ...utils, input, onChange, onNeedLocation };
}

const open = (input) => fireEvent.focus(input);
const rows = () =>
  screen.queryAllByRole('option').map((o) => o.querySelector('.search-option-copy').textContent);

describe('SearchField basics', () => {
  it('is labelled for screen readers', () => {
    const { input } = setup();
    expect(screen.getByLabelText('Starting point')).toBe(input);
  });

  it('starts closed', () => {
    const { input } = setup();
    expect(input.getAttribute('aria-expanded')).toBe('false');
    expect(screen.queryByRole('listbox')).toBeNull();
  });

  it('opens the list and asks for location on focus', () => {
    const { input, onNeedLocation } = setup();
    open(input);
    expect(input.getAttribute('aria-expanded')).toBe('true');
    expect(screen.getByRole('listbox')).toBeTruthy();
    expect(onNeedLocation).toHaveBeenCalledTimes(1);
  });
});

describe('SearchField without a location', () => {
  it('lists buildings alphabetically with no distances', () => {
    const { input, container } = setup({ showNearestShortcut: true });
    open(input);
    expect(rows()).toEqual(['Amos Eaton Hall', 'Carnegie Building', 'Lally Hall', 'Sage Lab']);
    expect(container.querySelectorAll('.search-option-distance').length).toBe(0);
  });

  it('shows no "Nearest entrance" row', () => {
    const { input } = setup({ showNearestShortcut: true });
    open(input);
    expect(screen.queryByText('Nearest entrance')).toBeNull();
  });
});

describe('SearchField with a location', () => {
  it('sorts closest first and shows a distance on every row', () => {
    const { input, container } = setup({ userPosition: nearLally });
    open(input);
    expect(rows()).toEqual(['Lally Hall', 'Amos Eaton Hall', 'Carnegie Building', 'Sage Lab']);
    expect(container.querySelectorAll('.search-option-distance').length).toBe(4);
  });

  it('adds a "Nearest entrance" shortcut row when enabled', () => {
    const { input } = setup({ userPosition: nearLally, showNearestShortcut: true });
    open(input);
    expect(screen.getByText('Nearest entrance')).toBeTruthy();
    expect(rows()[0]).toContain('Lally Hall');
    expect(screen.getAllByRole('option').length).toBe(5);
  });

  it('has no shortcut row when the shortcut is not enabled', () => {
    const { input } = setup({ userPosition: nearLally });
    open(input);
    expect(screen.queryByText('Nearest entrance')).toBeNull();
  });

  it('hides the shortcut once the user types', () => {
    const { input } = setup({ userPosition: nearLally, showNearestShortcut: true });
    open(input);
    fireEvent.change(input, { target: { value: 'sa' } });
    expect(screen.queryByText('Nearest entrance')).toBeNull();
  });
});