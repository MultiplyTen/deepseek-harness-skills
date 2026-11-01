import test from 'node:test'
import assert from 'node:assert/strict'
import { startPulse } from './managed-pulse.mjs'

function controlledScheduler() {
  let sequence = 0
  const tasks = new Map()
  const cancelled = []
  return {
    tasks,
    cancelled,
    schedule(tick) {
      const handle = ++sequence
      tasks.set(handle, tick)
      return handle
    },
    cancel(handle) {
      cancelled.push(handle)
      tasks.delete(handle)
    },
  }
}

test('dispose cancels the timer and suppresses an already queued callback', () => {
  const clock = controlledScheduler()
  const lines = []
  const stop = startPulse({ label: 'first', write: value => lines.push(value), ...clock })
  const queuedTick = [...clock.tasks.values()][0]
  queuedTick()
  assert.deepEqual(lines, ['[first] pulse 1'])
  stop()
  queuedTick()
  stop()
  assert.equal(clock.tasks.size, 0)
  assert.equal(clock.cancelled.length, 1)
  assert.deepEqual(lines, ['[first] pulse 1', '[first] disposed after 1 pulses'])
})

test('a replacement resource leaves exactly one timer and no old output', () => {
  const clock = controlledScheduler()
  const lines = []
  const write = value => lines.push(value)
  const stopFirst = startPulse({ label: 'old', write, ...clock })
  const oldTick = [...clock.tasks.values()][0]
  stopFirst()
  const stopSecond = startPulse({ label: 'new', write, ...clock })
  oldTick()
  assert.equal(clock.tasks.size, 1)
  for (const tick of clock.tasks.values()) tick()
  assert.deepEqual(lines, ['[old] disposed after 0 pulses', '[new] pulse 1'])
  stopSecond()
  assert.equal(clock.tasks.size, 0)
})

test('invalid intervals fail before allocating a timer', () => {
  const clock = controlledScheduler()
  for (const periodMs of [0, -1, 1.5, Number.NaN]) {
    assert.throws(() => startPulse({ label: 'bad', periodMs, ...clock }), RangeError)
  }
  assert.equal(clock.tasks.size, 0)
})
