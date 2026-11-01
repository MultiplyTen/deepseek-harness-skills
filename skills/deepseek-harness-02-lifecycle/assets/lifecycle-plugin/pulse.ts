import type { Context } from '@deepseek-ai/cordis'
import { startPulse } from './managed-pulse.mjs'

export const name = 'lifecycle-pulse'

// This plugin uses no Cordis service, so it needs no inject declaration.
export function apply(ctx: Context) {
  const instance = `pulse-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`
  console.log(`[${instance}] loaded`)

  // Cordis owns the disposer. The native timer itself is not auto-tracked.
  ctx.effect(() => startPulse({ label: instance, periodMs: 1000 }))
}
