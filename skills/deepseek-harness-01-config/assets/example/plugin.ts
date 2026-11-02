import type { Context } from '@deepseek-ai/cordis'
import Schema from '@deepseek-ai/schemastery'
import { defineTool } from '@deepseek-ai/dsh-tools'
import { countText } from './text-count.mjs'

export const name = 'text-counter-config'
export const inject = ['tools']

export interface Config {
  ignoreWhitespace: boolean
}

export const Config: Schema<Config> = Schema.object({
  ignoreWhitespace: Schema.boolean().default(false),
})

export function apply(ctx: Context, config: Config) {
  const counter = defineTool({
    name: 'text_count',
    description: '统计 Unicode 码点数；是否忽略空白由此插件实例的配置决定。 / Count Unicode code points; this plugin instance controls whether whitespace is ignored.',
    parameters: {
      text: { type: 'string', required: true, description: '待统计的文本 / Text to count' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, result) => [{ type: 'text', text: result }],
    },
    async execute(input) {
      return String(countText(input.text, config.ignoreWhitespace))
    },
  })
  ctx.tools.register(counter)
}
