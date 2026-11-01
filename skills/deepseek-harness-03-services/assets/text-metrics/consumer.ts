import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'
import { resolveTextMetricsRequest } from './definition.ts'

export const name = 'lesson-text-metrics-tool'
export const inject = ['tools', 'textMetrics']

export function apply(context: Context) {
  const textCount = defineTool({
    name: 'text_count',
    description: '按 Unicode 码点统计文本长度，可选择排除空白。',
    parameters: {
      text: { type: 'string', required: true, description: '待统计的文本' },
      ignoreWhitespace: { type: 'boolean', description: '为 true 时排除空白，默认 false' },
    },
    output: {
      schema: { type: 'number' },
      render: (_input, value) => [{ type: 'text', text: `码点数：${value}` }],
    },
    async execute(input) {
      const request = resolveTextMetricsRequest(input)
      const result = await context.textMetrics.measure(request)
      return result.codePoints
    },
  })

  context.tools.register(textCount)
}
