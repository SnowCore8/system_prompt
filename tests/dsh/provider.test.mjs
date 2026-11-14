import assert from 'node:assert/strict'
import { readdir } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

import { apply } from '../../plugins/dsh/src/index.js'

const PACKAGE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')

function createContext() {
  const factories = []
  const ctx = { skills: { registerProvider(factory) { factories.push(factory) } } }
  apply(ctx)
  assert.equal(factories.length, 1)
  return factories[0]()
}

test('list returns the twelve bundled skills', async () => {
  const provider = createContext()
  const candidates = await provider.list()
  const directories = (await readdir(path.join(PACKAGE_ROOT, 'skills'))).filter((name) => !name.startsWith('.'))
  assert.equal(candidates.length, directories.length)
  assert.deepEqual(candidates.map((item) => item.name), [...candidates.map((item) => item.name)].sort())
  for (const candidate of candidates) {
    assert.ok(candidate.description.length > 0)
    assert.equal(candidate.provider, 'global-user-constraints')
    assert.deepEqual(candidate.invocation, { modelInvocable: true, userInvocable: true })
  }
})

test('get loads the markdown body without frontmatter', async () => {
  const provider = createContext()
  const [candidate] = await provider.list()
  const definition = await provider.get(candidate)
  assert.ok(definition)
  assert.ok(definition.content.length > 100)
  assert.ok(!definition.content.startsWith('---'))
  assert.match(definition.content, /^#/u)
})

test('get returns undefined for a missing file', async () => {
  const provider = createContext()
  const definition = await provider.get({ locator: { file: path.join(PACKAGE_ROOT, 'skills', 'missing', 'SKILL.md') } })
  assert.equal(definition, undefined)
})
