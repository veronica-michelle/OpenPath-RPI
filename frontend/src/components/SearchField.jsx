import { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import { haversineFeet } from '../utils/geo.js';
import { formatDistance } from '../utils/metrics.js';

function matchBuildings(buildings, query, excludeId) {
  const q = query.trim().toLowerCase();
  const pool = buildings.filter((b) => b.id !== excludeId);
  if (!q) return [...pool].sort((a, b) => a.name.localeCompare(b.name));
  const starts = pool.filter((b) => b.name.toLowerCase().startsWith(q));
  const contains = pool.filter(
    (b) => !b.name.toLowerCase().startsWith(q) && b.name.toLowerCase().includes(q),
  );
  return [...starts, ...contains].sort((a, b) => a.name.localeCompare(b.name)).sort((a, b) => {
    const aStarts = a.name.toLowerCase().startsWith(q);
    const bStarts = b.name.toLowerCase().startsWith(q);
    return aStarts === bStarts ? 0 : aStarts ? -1 : 1;
  });
}

function withDistance(buildings, origin) {
  if (!origin) return buildings.map((b) => ({ ...b, distanceFt: null }));
  return buildings
    .map((b) => ({ ...b, distanceFt: haversineFeet(origin, b) }))
    .sort((a, b) => a.distanceFt - b.distanceFt);
}

export default function SearchField({
  label,
  dotClass,
  buildings,
  value,
  onChange,
  excludeId,
  placeholder,
  userPosition,
  onNeedLocation,
  showNearestShortcut,
}) {
  const [text, setText] = useState(value?.name ?? '');
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const blurTimer = useRef(null);
  const inputId = useId();
  const listId = useId();

  useEffect(() => {
    setText(value?.name ?? '');
  }, [value]);

  const ranked = useMemo(
    () => withDistance(matchBuildings(buildings, open ? text : '', excludeId), userPosition),
    [buildings, excludeId, open, text, userPosition],
  );

  const nearest = ranked[0] ?? null;
  const queryEmpty = text.trim() === '';
  const showNearest = Boolean(showNearestShortcut && userPosition && nearest && queryEmpty && open);
  const options = ranked;
  const rowCount = options.length + (showNearest ? 1 : 0);

  const commit = useCallback((building) => {
    onChange(building);
    setText(building ? building.name : '');
    setOpen(false);
  }, [onChange]);

  const handleInput = useCallback((e) => {
    const next = e.target.value;
    setText(next);
    setOpen(true);
    setActiveIndex(0);
    if (next.trim() === '') onChange(null);
  }, [onChange]);

  const handleFocus = useCallback(() => {
    setOpen(true);
    onNeedLocation?.();
  }, [onNeedLocation]);

  const handleBlur = useCallback(() => {
    blurTimer.current = setTimeout(() => {
      setOpen(false);
      const exact = buildings.find((b) => b.name.toLowerCase() === text.trim().toLowerCase());
      if (exact) {
        commit(exact);
      } else if (text.trim() === '') {
        onChange(null);
      } else {
        setText(value?.name ?? '');
      }
    }, 120);
  }, [buildings, commit, onChange, text, value]);

  const activateRow = useCallback((index) => {
    if (showNearest && index === 0) {
      commit(nearest);
      return;
    }
    const buildingIndex = showNearest ? index - 1 : index;
    if (options[buildingIndex]) commit(options[buildingIndex]);
  }, [commit, nearest, options, showNearest]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setOpen(true);
      setActiveIndex((i) => Math.min(i + 1, Math.max(rowCount - 1, 0)));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (open) activateRow(activeIndex);
    } else if (e.key === 'Escape') {
      setOpen(false);
      setText(value?.name ?? '');
    }
  }, [activateRow, activeIndex, open, rowCount, value]);

  return (
    <div className={`search-field${open ? ' is-open' : ''}`} data-no-pan>
      <span className={`search-dot ${dotClass}`} aria-hidden="true" />
      <label htmlFor={inputId} className="search-label-visually-hidden">
        {label}
      </label>
      <input
        id={inputId}
        className="search-input"
        type="text"
        role="combobox"
        aria-expanded={open}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={open ? `${listId}-row-${activeIndex}` : undefined}
        autoComplete="off"
        placeholder={placeholder}
        value={text}
        onChange={handleInput}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
      />
      {open && (options.length > 0 || showNearest) && (
        <ul
          id={listId}
          role="listbox"
          className="search-listbox"
          onMouseDown={(e) => {
            e.preventDefault();
            clearTimeout(blurTimer.current);
          }}
        >
          {showNearest && (
            <li
              id={`${listId}-row-0`}
              role="option"
              aria-selected={activeIndex === 0}
              className={`search-option search-option-nearest${activeIndex === 0 ? ' is-active' : ''}`}
              onMouseEnter={() => setActiveIndex(0)}
              onClick={() => commit(nearest)}
            >
              <span className="search-option-copy">
                <span className="search-option-title">Nearest entrance</span>
                <span className="search-option-meta">{nearest.name}</span>
              </span>
              <span className="search-option-distance">{formatDistance(nearest.distanceFt)}</span>
            </li>
          )}
          {options.map((b, i) => {
            const row = showNearest ? i + 1 : i;
            return (
              <li
                key={b.id}
                id={`${listId}-row-${row}`}
                role="option"
                aria-selected={activeIndex === row}
                className={`search-option${activeIndex === row ? ' is-active' : ''}`}
                onMouseEnter={() => setActiveIndex(row)}
                onClick={() => commit(b)}
              >
                <span className="search-option-copy">{b.name}</span>
                {b.distanceFt != null && (
                  <span className="search-option-distance">{formatDistance(b.distanceFt)}</span>
                )}
              </li>
            );
          })}
        </ul>
      )}
      {open && options.length === 0 && !showNearest && (
        <div className="search-listbox search-empty">no match on the board</div>
      )}
    </div>
  );
}
