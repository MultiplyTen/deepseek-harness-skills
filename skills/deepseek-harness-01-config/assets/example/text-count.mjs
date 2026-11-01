// Original teaching helper. Counts code points, not grapheme clusters.
export function countText(text, ignoreWhitespace = false) {
  if (typeof text !== 'string' || typeof ignoreWhitespace !== 'boolean') {
    throw new TypeError('text must be a string and ignoreWhitespace a boolean')
  }
  const input = ignoreWhitespace ? text.replace(/\s/gu, '') : text
  return Array.from(input).length
}
