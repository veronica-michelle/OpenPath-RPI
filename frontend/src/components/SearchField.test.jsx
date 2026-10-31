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
