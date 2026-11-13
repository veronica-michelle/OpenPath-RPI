// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import SearchField from './SearchField.jsx';

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

const buildings = [
  { id: 'hall', name: 'Hall', lat: 42, lng: -73, entrances: [
    { id: 'west', lat: 42, lng: -73 }, { id: 'east', lat: 42, lng: -72.998 },
  ] },
  { id: 'lab', name: 'Lab', lat: 42, lng: -72.9995 },
];

describe('SearchField', () => {
  it('clears a selected location and cancels pending blur selection', () => {
    vi.useFakeTimers();
    const onChange = vi.fn();
    const { rerender } = render(<SearchField label="Starting point" buildings={buildings}
      value={buildings[0]} onChange={onChange} />);
    const input = screen.getByRole('combobox');
    fireEvent.change(input, { target: { value: 'Lab' } });
    fireEvent.blur(input);
    fireEvent.click(screen.getByRole('button', { name: 'Clear starting point' }));
    expect(onChange).toHaveBeenCalledExactlyOnceWith(null);
    rerender(<SearchField label="Starting point" buildings={buildings}
      value={null} onChange={onChange} />);
    vi.runAllTimers();
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(input.value).toBe('');
    expect(document.activeElement).toBe(input);
    expect(screen.queryByRole('button', { name: 'Clear starting point' })).toBeNull();
  });

  it('clears an uncommitted destination query', () => {
    const onChange = vi.fn();
    render(<SearchField label="Destination" buildings={buildings} value={null} onChange={onChange} />);
    const input = screen.getByRole('combobox');
    expect(screen.queryByRole('button', { name: 'Clear destination' })).toBeNull();
    fireEvent.change(input, { target: { value: 'Ha' } });
    fireEvent.click(screen.getByRole('button', { name: 'Clear destination' }));
    expect(input.value).toBe('');
    expect(onChange).toHaveBeenCalledExactlyOnceWith(null);
    expect(document.activeElement).toBe(input);
  });

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

describe('SearchField filtering', () => {
  it('leaves out the excluded building', () => {
    const { input } = setup({ excludeId: 'lally' });
    open(input);
    expect(rows()).not.toContain('Lally Hall');
    expect(rows().length).toBe(3);
  });

  it('puts names that start with the query before names that only contain it', () => {
    const { input } = setup();
    open(input);
    fireEvent.change(input, { target: { value: 'l' } });
    expect(rows()).toEqual(['Lally Hall', 'Amos Eaton Hall', 'Carnegie Building', 'Sage Lab']);
  });

  it('ignores upper and lower case', () => {
    const { input } = setup();
    open(input);
    fireEvent.change(input, { target: { value: 'SAGE' } });
    expect(rows()).toEqual(['Sage Lab']);
  });

  it('shows an empty message when nothing matches', () => {
    const { input } = setup();
    open(input);
    fireEvent.change(input, { target: { value: 'zzz' } });
    expect(screen.getByText('no match on the board')).toBeTruthy();
    expect(screen.queryByRole('listbox')).toBeNull();
  });

  it('clears the selection when the text is emptied', () => {
    const { input, onChange } = setup({ value: listBuildings[1] });
    fireEvent.change(input, { target: { value: '' } });
    expect(onChange).toHaveBeenCalledWith(null);
  });
});

describe('SearchField selecting', () => {
  it('selects a building on click', () => {
    const { input, onChange } = setup();
    open(input);
    fireEvent.click(screen.getByText('Lally Hall'));
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ id: 'lally' }));
    expect(screen.queryByRole('listbox')).toBeNull();
  });

  it('selects the nearest building from the shortcut row', () => {
    const { input, onChange } = setup({ userPosition: nearLally, showNearestShortcut: true });
    open(input);
    fireEvent.click(screen.getByText('Nearest entrance'));
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ id: 'lally' }));
  });
});

describe('SearchField keyboard', () => {
  it('moves the highlight with the arrow keys', () => {
    const { input } = setup();
    open(input);
    const options = () => screen.getAllByRole('option');
    expect(options()[0].getAttribute('aria-selected')).toBe('true');
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    expect(options()[1].getAttribute('aria-selected')).toBe('true');
    fireEvent.keyDown(input, { key: 'ArrowUp' });
    expect(options()[0].getAttribute('aria-selected')).toBe('true');
  });

  it('stops at the first and last rows', () => {
    const { input } = setup();
    open(input);
    for (let i = 0; i < 10; i++) fireEvent.keyDown(input, { key: 'ArrowDown' });
    const options = screen.getAllByRole('option');
    expect(options[options.length - 1].getAttribute('aria-selected')).toBe('true');
    for (let i = 0; i < 10; i++) fireEvent.keyDown(input, { key: 'ArrowUp' });
    expect(screen.getAllByRole('option')[0].getAttribute('aria-selected')).toBe('true');
  });

  it('selects the highlighted row with Enter', () => {
    const { input, onChange } = setup();
    open(input);
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ id: 'carnegie' }));
  });

  it('selects the nearest building with Enter when the shortcut row is highlighted', () => {
    const { input, onChange } = setup({ userPosition: nearLally, showNearestShortcut: true });
    open(input);
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ id: 'lally' }));
  });

  it('closes the list with Escape', () => {
    const { input } = setup();
    open(input);
    fireEvent.keyDown(input, { key: 'Escape' });
    expect(screen.queryByRole('listbox')).toBeNull();
    expect(input.getAttribute('aria-expanded')).toBe('false');
  });
});

describe('SearchField leaving the field', () => {
  afterEach(() => vi.useRealTimers());

  it('selects a building when the typed text exactly matches its name', () => {
    vi.useFakeTimers();
    const { input, onChange } = setup();
    open(input);
    fireEvent.change(input, { target: { value: 'lally hall' } });
    fireEvent.blur(input);
    act(() => {
      vi.advanceTimersByTime(150);
    });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ id: 'lally' }));
  });

  it('reverts partial text to the current selection', () => {
    vi.useFakeTimers();
    const { input, onChange } = setup({ value: null });
    open(input);
    fireEvent.change(input, { target: { value: 'zzz' } });
    fireEvent.blur(input);
    act(() => {
      vi.advanceTimersByTime(150);
    });
    expect(input.value).toBe('');
    expect(onChange).not.toHaveBeenCalled();
  });
});