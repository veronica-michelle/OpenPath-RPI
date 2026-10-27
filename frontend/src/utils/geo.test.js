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

const south = { lat: 42.729, lng: -73.68 };
const west = { lat: 42.73, lng: -73.681 };
const northEast = { lat: 42.731, lng: -73.679 };

describe('bearingBetween edge cases', () => {
  it('returns about 180 heading south', () => {
    expect(bearingBetween(a, south)).toBeCloseTo(180, 0);
  });
  it('returns about 270 heading west', () => {
    expect(bearingBetween(a, west)).toBeCloseTo(270, 0);
  });
  it('always stays within 0 to 360', () => {
    for (const p of [north, east, south, west, northEast]) {
      const b = bearingBetween(a, p);
      expect(b).toBeGreaterThanOrEqual(0);
      expect(b).toBeLessThan(360);
    }
  });
  it('does not return NaN for identical points', () => {
    expect(Number.isNaN(bearingBetween(a, a))).toBe(false);
  });
});

describe('nearestPointOnRoute edge cases', () => {
  const route = [a, north];

  it('clamps a point before the start to zero progress', () => {
    expect(nearestPointOnRoute(south, route).traveledFt).toBeCloseTo(0, 0);
  });
  it('reports sideways distance but the same progress for a point beside the route', () => {
    const beside = { lat: 42.7305, lng: -73.6799 };
    const r = nearestPointOnRoute(beside, route);
    expect(r.distFt).toBeGreaterThan(20);
    expect(r.distFt).toBeLessThan(35);
    expect(r.traveledFt).toBeCloseTo(haversineFeet(a, north) / 2, -1);
  });
  it('adds up distance across multiple segments', () => {
    const multi = [a, north, northEast];
    const r = nearestPointOnRoute(northEast, multi);
    expect(r.traveledFt).toBeCloseTo(
      haversineFeet(a, north) + haversineFeet(north, northEast), -1);
  });
  it('does not produce NaN when two route points are identical', () => {
    const r = nearestPointOnRoute({ lat: 42.7305, lng: -73.68 }, [a, a, north]);
    expect(Number.isFinite(r.traveledFt)).toBe(true);
  });
});

describe('haversineFeet', () => {
  it('is 0 for the same point', () => {
    expect(haversineFeet(a, a)).toBe(0);
  });
  it('is about 365 ft for 0.001 degrees of latitude', () => {
    expect(haversineFeet(a, north)).toBeCloseTo(365, -1);
  });
  it('is the same in both directions', () => {
    expect(haversineFeet(a, east)).toBeCloseTo(haversineFeet(east, a), 5);
  });
});