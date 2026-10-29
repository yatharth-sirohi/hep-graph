// result-types.js — what each kind of result is, for a reader new to the field, and the
// three bands the Results list opens in (landmarks first). Shared by the result panel
// (panels.js) and the Results list (modes.js).

/** A result type's meaning, in a sentence: shown on hover and focus wherever it is named. */
export const RESULT_TYPE_HELP = {
  discovery: 'Discovery: something new, established beyond reasonable doubt (in particle physics, usually at 5 standard deviations)',
  first_detection: 'First detection: the first time this was seen at all',
  observation: 'Observation: a signal seen clearly enough to claim it (usually 5 standard deviations)',
  evidence: 'Evidence: a signal that is strong but not yet conclusive (usually 3 standard deviations)',
  anomaly: 'Anomaly: a result that does not fit the expected picture, not yet explained or confirmed',
  measurement: 'Measurement: a quantity determined with a stated uncertainty',
  precision_measurement: 'Precision measurement: a quantity pinned down very precisely, often to test a theory',
  limit: 'Limit: a search that found no signal, and so sets a bound on how large the effect can be',
  technology_milestone: 'Technology milestone: a detector or accelerator achievement, not a physics result',
};

/** The Results list's "Landmarks first" order: each band newest first within it. */
export const RESULT_BANDS = [
  { label: 'Discoveries and first detections', types: ['discovery', 'first_detection'] },
  { label: 'Observations, evidence and anomalies', types: ['observation', 'evidence', 'anomaly'] },
  { label: 'Measurements, limits and milestones', types: null },
];

export function resultBand(result) {
  const index = RESULT_BANDS.findIndex((band) => band.types && band.types.includes(result.result_type));
  return index === -1 ? RESULT_BANDS.length - 1 : index;
}
