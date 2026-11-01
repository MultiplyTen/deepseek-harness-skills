import type { Context } from '@deepseek-ai/cordis'
import {
  TextMetricsService,
  type TextMetricsRequest,
  type TextMetricsResult,
} from './definition.ts'
import { countCodePoints } from './measure.mjs'

class LocalTextMetrics extends TextMetricsService {
  async measure(request: TextMetricsRequest): Promise<TextMetricsResult> {
    return { codePoints: countCodePoints(request.text, request.ignoreWhitespace) }
  }
}

export const name = 'lesson-text-metrics-local'

export function apply(context: Context) {
  context.plugin(LocalTextMetrics)
}
