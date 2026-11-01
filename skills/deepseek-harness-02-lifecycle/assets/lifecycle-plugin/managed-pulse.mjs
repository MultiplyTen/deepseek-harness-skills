/**
 * Start one synchronous pulse resource and return an idempotent disposer.
 * The injectable scheduler lets the example verify cleanup without sleeping.
 */
export function startPulse({
  label,
  periodMs = 1000,
  write = console.log,
  schedule = setInterval,
  cancel = clearInterval,
}) {
  if (typeof label !== 'string' || label.length === 0) {
    throw new TypeError('label must be a non-empty string')
  }
  if (!Number.isSafeInteger(periodMs) || periodMs < 1) {
    throw new RangeError('periodMs must be a positive safe integer')
  }

  let stopped = false
  let pulses = 0
  const handle = schedule(() => {
    if (stopped) return
    pulses += 1
    write(`[${label}] pulse ${pulses}`)
  }, periodMs)

  return () => {
    if (stopped) return
    stopped = true
    cancel(handle)
    write(`[${label}] disposed after ${pulses} pulses`)
  }
}
