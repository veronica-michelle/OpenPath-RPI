// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
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
