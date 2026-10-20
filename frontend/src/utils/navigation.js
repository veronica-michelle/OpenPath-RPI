// Selects the next server-provided maneuver for the current route progress.
// Progress is UI state; the maneuver sequence is returned by the route API.
export function currentInstruction(steps, traveledDistance) {
  if (!steps.length) return null;
  const next = steps.find((step) => step.atDistance > traveledDistance + 0.01) ?? steps[steps.length - 1];
  return { ...next, remaining: Math.max(0, next.atDistance - traveledDistance) };
}
