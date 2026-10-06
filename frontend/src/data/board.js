// Real coordinates for the ARN pilot area (~0.1mi around Carnegie), looked
// up from OpenStreetMap (Nominatim). Buildings are real; the walkway
// junctions between them are still approximate placeholder waypoints (no
// surveyed sidewalk data yet), placed at sensible midpoints between the
// buildings they connect. Elevation is mock, authored to match the real
// story of this campus: EMPAC sits low near the Approach/river, the
// academic quad sits highest up the hill.

export const WALK_SPEED_MPH = 2.5; // accessible walking pace, not average 3mph

// Entrances are real OSM `entrance` nodes near each building, matched to
// their building and labeled by compass direction computed from the real
// bearing off the building's center — not invented. One (Walker Lab, east
// side) carries OSM's own `wheelchair=yes` tag, called out in its label
// rather than silently treated the same as the others. Buildings with only
// one tagged entrance in OSM (Amos Eaton, Lally) list just that one; the
// picker only appears when there's an actual choice to make.
export const BUILDINGS = [
  {
    id: 'carnegie',
    name: 'Carnegie',
    lat: 42.7304438,
    lng: -73.6831941,
    elevation: 58,
    entrances: [
      { id: 'carnegie-e1', lat: 42.7304826, lng: -73.6833129, label: 'Northwest' },
      { id: 'carnegie-e2', lat: 42.7304039, lng: -73.6830758, label: 'Southeast' },
    ],
  },
  {
    id: 'walker',
    name: 'Walker Lab',
    lat: 42.7308752,
    lng: -73.6825058,
    elevation: 60,
    entrances: [
      { id: 'walker-e1', lat: 42.7308502, lng: -73.6822893, label: 'East' },
      { id: 'walker-e2', lat: 42.7309589, lng: -73.6821182, label: 'East (Accessible)', wheelchair: true },
      { id: 'walker-e3', lat: 42.7306746, lng: -73.6827277, label: 'Southwest' },
    ],
  },
  {
    id: 'sage',
    name: 'Sage Lab',
    lat: 42.7308930,
    lng: -73.6816644,
    elevation: 66,
    entrances: [
      { id: 'sage-e1', lat: 42.7307679, lng: -73.6816787, label: 'South' },
      { id: 'sage-e2', lat: 42.7309716, lng: -73.681183, label: 'East' },
    ],
  },
  {
    id: 'pittsburgh',
    name: 'Pittsburgh',
    lat: 42.7311570,
    lng: -73.6833192,
    elevation: 55,
    entrances: [{ id: 'pittsburgh-e1', lat: 42.7310446, lng: -73.6833374, label: 'South' }],
  },
  {
    id: 'empac',
    name: 'EMPAC',
    lat: 42.7288114,
    lng: -73.6838551,
    elevation: 0,
    entrances: [
      { id: 'empac-e1', lat: 42.7285344, lng: -73.6836701, label: 'Southeast' },
      { id: 'empac-e2', lat: 42.7285846, lng: -73.6839246, label: 'South' },
      { id: 'empac-e3', lat: 42.7286302, lng: -73.6841558, label: 'Southwest' },
      { id: 'empac-e4', lat: 42.7291589, lng: -73.6836622, label: 'North' },
    ],
  },
  {
    id: 'westhall',
    name: 'West Hall',
    lat: 42.7317090,
    lng: -73.6831067,
    elevation: 18,
    entrances: [
      { id: 'westhall-e1', lat: 42.7316936, lng: -73.6827275, label: 'East' },
      { id: 'westhall-e2', lat: 42.7317588, lng: -73.6829431, label: 'Northeast' },
      { id: 'westhall-e3', lat: 42.7317388, lng: -73.6834818, label: 'West' },
      { id: 'westhall-e4', lat: 42.7315635, lng: -73.683056, label: 'South' },
    ],
  },
  {
    id: 'amoseaton',
    name: 'Amos Eaton',
    lat: 42.7302055,
    lng: -73.6825717,
    elevation: 42,
    entrances: [{ id: 'amoseaton-e1', lat: 42.7301741, lng: -73.6822909, label: 'East' }],
  },
  {
    id: 'lally',
    name: 'Lally',
    lat: 42.7300621,
    lng: -73.6819038,
    elevation: 48,
    entrances: [{ id: 'lally-e1', lat: 42.7301234, lng: -73.6818871, label: 'North' }],
  },
  {
    id: 'library',
    name: 'Library',
    lat: 42.7294564,
    lng: -73.6826452,
    elevation: 50,
    entrances: [{ id: 'library-e1', lat: 42.7293023, lng: -73.6824149, label: 'Southeast' }],
  },
  {
    id: 'vcc',
    name: 'VCC',
    lat: 42.7292341,
    lng: -73.6817738,
    elevation: 58,
    entrances: [
      { id: 'vcc-e1', lat: 42.7290895, lng: -73.6816222, label: 'Southeast' },
      { id: 'vcc-e2', lat: 42.7292812, lng: -73.6822042, label: 'West' },
      { id: 'vcc-e3', lat: 42.7293412, lng: -73.681573, label: 'Northeast' },
    ],
  },
];

// Waypoints: path junctions along the walkway network, not selectable —
// placed as midpoints between the real buildings they connect.
export const JUNCTIONS = [
  { id: 'j1', lat: 42.7306021, lng: -73.6830283, elevation: 50 },
  { id: 'j2', lat: 42.7306595, lng: -73.6828500, elevation: 56 },
  { id: 'j3', lat: 42.7303341, lng: -73.6819813, elevation: 62 },
  { id: 'j4', lat: 42.7309573, lng: -73.6828392, elevation: 30 },
  { id: 'j5', lat: 42.7299501, lng: -73.6829197, elevation: 54 },
  { id: 'j6', lat: 42.7295842, lng: -73.6821076, elevation: 52 },
  { id: 'j7', lat: 42.7302602, lng: -73.6834809, elevation: 8 },
];

const NODE_LIST = [...BUILDINGS, ...JUNCTIONS];
export const NODES = Object.fromEntries(NODE_LIST.map((n) => [n.id, n]));

export const EDGES = [
  // accessible backbone — always usable when stairs are excluded
  { a: 'carnegie', b: 'j1', stairs: false },
  { a: 'carnegie', b: 'j2', stairs: false },
  { a: 'carnegie', b: 'j5', stairs: false },
  { a: 'pittsburgh', b: 'j1', stairs: false },
  { a: 'amoseaton', b: 'j1', stairs: false },
  { a: 'amoseaton', b: 'j4', stairs: false },
  { a: 'westhall', b: 'j4', stairs: false },
  { a: 'westhall', b: 'j7', stairs: false },
  { a: 'empac', b: 'j7', stairs: false },
  { a: 'walker', b: 'j2', stairs: false },
  { a: 'walker', b: 'j3', stairs: false },
  { a: 'sage', b: 'j3', stairs: false },
  { a: 'vcc', b: 'j3', stairs: false },
  { a: 'vcc', b: 'j6', stairs: false },
  { a: 'library', b: 'j5', stairs: false },
  { a: 'library', b: 'j6', stairs: false },
  { a: 'lally', b: 'j6', stairs: false },
  { a: 'j1', b: 'j2', stairs: false },
  { a: 'j1', b: 'j4', stairs: false },
  { a: 'j2', b: 'j3', stairs: false },
  { a: 'j2', b: 'j5', stairs: false },
  { a: 'j4', b: 'j7', stairs: false },
  { a: 'j5', b: 'j6', stairs: false },
  { a: 'j3', b: 'j6', stairs: false },

  // stairs shortcuts — shorter, but excluded when the toggle is off
  { a: 'carnegie', b: 'library', stairs: true },
  { a: 'walker', b: 'amoseaton', stairs: true },
  { a: 'pittsburgh', b: 'westhall', stairs: true },
  { a: 'sage', b: 'vcc', stairs: true },
  { a: 'lally', b: 'vcc', stairs: true },
  { a: 'empac', b: 'library', stairs: true },
];
