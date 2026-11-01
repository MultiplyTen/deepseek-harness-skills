/** Counts Unicode code points; combining sequences may contain several points. */
export function countCodePoints(text, ignoreWhitespace) {
  const content = ignoreWhitespace ? text.replace(/\s/gu, '') : text
  return Array.from(content).length
}
