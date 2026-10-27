import { describe, it, expect } from 'vitest';
import { bearingBetween, nearestPointOnRoute, haversineFeet } from './geo.js';

const a = { lat: 42.73, lng: -73.68 };
const north = { lat: 42.731, lng: -73.68 };
const east = { lat: 42.73, lng: -73.679 };

describe('bearingBetween', () => {
  it('returns about 0 when heading north', () => {
    expect(bearingBetween(a, north)).toBeCloseTo(0, 0);
  });
  it('returns about 90 when heading east', () => {
    expect(bearingBetween(a, east)).toBeCloseTo(90, 0);
  });
});

describe('nearestPointOnRoute', () => {
  const route = [a, north];
  it('reports about half the route traveled at the midpoint', () => {
    const mid = { lat: 42.7305, lng: -73.68 };
    const result = nearestPointOnRoute(mid, route);
    expect(result.distFt).toBeLessThan(2);
    expect(result.traveledFt).toBeCloseTo(haversineFeet(a, north) / 2, -1);
  });
  it('snaps a point past the end to the end of the route', () => {
    const past = { lat: 42.732, lng: -73.68 };
    const result = nearestPointOnRoute(past, route);
    expect(result.traveledFt).toBeCloseTo(haversineFeet(a, north), -1);
  });
});