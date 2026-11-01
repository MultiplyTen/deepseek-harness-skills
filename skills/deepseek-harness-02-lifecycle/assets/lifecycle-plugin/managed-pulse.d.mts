export interface PulseOptions {
  label: string
  periodMs?: number
  write?: (line: string) => void
  schedule?: (tick: () => void, periodMs: number) => ReturnType<typeof setInterval>
  cancel?: (handle: ReturnType<typeof setInterval>) => void
}

export function startPulse(options: PulseOptions): () => void
