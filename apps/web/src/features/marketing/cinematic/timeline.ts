/** Source durations; the unapproved return-to-opening is deliberately NOT part of playback. */
export const durations = [6700, 8600, 7200, 8700, 8100, 8500, 8500, 8600, 3300, 9400, 7200, 7600] as const;
export const offsets = durations.map((_, i) => durations.slice(0, i).reduce<number>((a, b) => a + b, 0));
export const duration = 92400;
export const clamp = (p: number) => Math.max(0, Math.min(1, p));
export const ease = (p: number) => { p = clamp(p); return p * p * (3 - 2 * p); };
export function position(time: number) {
  const ms = Math.max(0, Math.min(duration, time));
  const index = offsets.findLastIndex(start => ms >= start);
  return { index, local: ms - offsets[index] };
}
