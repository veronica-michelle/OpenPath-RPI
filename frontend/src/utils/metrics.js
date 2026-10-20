export function formatDistance(feet) {
  if (feet < 528) return `${Math.round(feet)} ft`;
  return `${(feet / 5280).toFixed(1)} mi`;
}

export function formatMinutes(minutes) {
  return `${minutes} min`;
}
