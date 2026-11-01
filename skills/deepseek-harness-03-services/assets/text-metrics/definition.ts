import { Service, type Context } from '@deepseek-ai/cordis'

export interface TextMetricsInput {
  text: string
  ignoreWhitespace?: boolean
}

export interface TextMetricsRequest {
  text: string
  ignoreWhitespace: boolean
}

export interface TextMetricsResult {
  codePoints: number
}

export function resolveTextMetricsRequest(input: TextMetricsInput): TextMetricsRequest {
  return { text: input.text, ignoreWhitespace: input.ignoreWhitespace === true }
}

export abstract class TextMetricsService extends Service {
  constructor(context: Context) {
    super(context, 'textMetrics')
  }

  abstract measure(request: TextMetricsRequest): Promise<TextMetricsResult>
}

declare module '@deepseek-ai/cordis' {
  interface Context {
    textMetrics: TextMetricsService
  }
}
