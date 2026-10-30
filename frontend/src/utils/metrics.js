export function formatDistance(feet) {
  if (feet < 501) return `${Math.round(feet)} ft`;
  return `${(feet / 5280).toFixed(2)} mi`;
}

export function formatMinutes(minutes) {
  return `${minutes} min`;
}
