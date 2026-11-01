import assert from 'node:assert/strict'
import test from 'node:test'
import { countCodePoints } from './measure.mjs'

test('empty text has no code points', () => {
  assert.equal(countCodePoints('', false), 0)
})

test('the whitespace policy changes the result explicitly', () => {
  assert.equal(countCodePoints('你好 Agent', false), 8)
  assert.equal(countCodePoints('你好 Agent', true), 7)
  assert.equal(countCodePoints('A\tB\nC', false), 5)
  assert.equal(countCodePoints('A\tB\nC', true), 3)
})

test('supplementary-plane symbols count once, not as UTF-16 pairs', () => {
  assert.equal(countCodePoints('A😀', false), 2)
})

test('the contract counts code points rather than grapheme clusters', () => {
  assert.equal(countCodePoints('e\u0301', false), 2)
  assert.equal(countCodePoints('👩‍💻', false), 3)
})
