import assert from 'node:assert/strict'
import { mkdtemp, mkdir, readdir, writeFile } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

import { apply, constraintsSection } from '../../plugins/dsh/src/index.js'

const PACKAGE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')

function createContext() {
  const factories = []
  const sections = []
  const ctx = {
    skills: { registerProvider(factory) { factories.push(factory) } },
    systemPrompt: { section(entry) { sections.push(entry) } },
  }
  apply(ctx)
  assert.equal(factories.length, 1)
  return { provider: factories[0](), sections }
}

test('list returns the nineteen bundled skills', async () => {
  const { provider } = createContext()
  const candidates = await provider.list()
  const directories = (await readdir(path.join(PACKAGE_ROOT, 'skills'))).filter((name) => !name.startsWith('.'))
  assert.equal(candidates.length, 19)
  assert.equal(candidates.length, directories.length)
  assert.deepEqual(candidates.map((item) => item.name), [...candidates.map((item) => item.name)].sort())
  for (const candidate of candidates) {
    assert.ok(candidate.description.length > 0)
    assert.equal(candidate.provider, 'global-user-constraints')
    assert.deepEqual(candidate.invocation, { modelInvocable: true, userInvocable: true })
  }
})

test('get loads the markdown body without frontmatter', async () => {
  const { provider } = createContext()
  const [candidate] = await provider.list()
  const definition = await provider.get(candidate)
  assert.ok(definition)
  assert.ok(definition.content.length > 100)
  assert.ok(!definition.content.startsWith('---'))
  assert.match(definition.content, /^#/u)
})

test('get returns undefined for a missing file', async () => {
  const { provider } = createContext()
  const definition = await provider.get({ locator: { file: path.join(PACKAGE_ROOT, 'skills', 'missing', 'SKILL.md') } })
  assert.equal(definition, undefined)
})

test('constraintsSection dedupes against a matching user AGENTS.md', async () => {
  const tmp = await mkdtemp(path.join(os.tmpdir(), 'dsh-constraints-'))
  const rulesDir = path.join(tmp, 'rules')
  await mkdir(rulesDir)
  const body = '# 测试约束\n\nMARKER-dsh-dedupe-5e2d\n'
  await writeFile(path.join(rulesDir, 'global-user-constraints.md'), body, 'utf8')

  const previousHome = process.env.DSH_HOME
  process.env.DSH_HOME = path.join(tmp, 'dsh-home')
  await mkdir(process.env.DSH_HOME, { recursive: true })
  await writeFile(path.join(process.env.DSH_HOME, 'AGENTS.md'), body, 'utf8')
  try {
    assert.equal(constraintsSection(tmp), undefined)
  } finally {
    if (previousHome === undefined) delete process.env.DSH_HOME
    else process.env.DSH_HOME = previousHome
  }
})

test('constraintsSection returns undefined when the rules file is missing', () => {
  const tmp = path.join(os.tmpdir(), 'dsh-constraints-missing-dir')
  assert.equal(constraintsSection(tmp), undefined)
})

test('constraintsSection returns a hint instead of the full text when oversized', async () => {
  const tmp = await mkdtemp(path.join(os.tmpdir(), 'dsh-constraints-'))
  const rulesDir = path.join(tmp, 'rules')
  await mkdir(rulesDir)
  const body = '# 测试约束\n\nMARKER-dsh-oversized-6b2e\n' + 'x'.repeat(32 * 1024)
  await writeFile(path.join(rulesDir, 'global-user-constraints.md'), body, 'utf8')

  const previousHome = process.env.DSH_HOME
  const previousAgents = process.env.DSH_AGENTS_HOME
  process.env.DSH_HOME = path.join(tmp, 'dsh-home')
  process.env.DSH_AGENTS_HOME = path.join(tmp, 'agents-home')
  try {
    const section = constraintsSection(tmp)
    assert.ok(section)
    assert.ok(!section.text.includes('MARKER-dsh-oversized-6b2e'))
    assert.match(section.text, /32 KiB/u)
    assert.match(section.text, /rules[/\\]global-user-constraints\.md/u)
  } finally {
    if (previousHome === undefined) delete process.env.DSH_HOME
    else process.env.DSH_HOME = previousHome
    if (previousAgents === undefined) delete process.env.DSH_AGENTS_HOME
    else process.env.DSH_AGENTS_HOME = previousAgents
  }
})

test('apply registers only the constraints section', async () => {
  const tmp = await mkdtemp(path.join(os.tmpdir(), 'dsh-sections-'))
  const previousHome = process.env.DSH_HOME
  const previousAgents = process.env.DSH_AGENTS_HOME
  process.env.DSH_HOME = tmp
  process.env.DSH_AGENTS_HOME = tmp
  try {
    const { sections } = createContext()
    assert.deepEqual(sections.map((item) => item.name), ['global-user-constraints'])
  } finally {
    if (previousHome === undefined) delete process.env.DSH_HOME
    else process.env.DSH_HOME = previousHome
    if (previousAgents === undefined) delete process.env.DSH_AGENTS_HOME
    else process.env.DSH_AGENTS_HOME = previousAgents
  }
})

test('constraintsSection preserves literal text including frontmatter and placeholders', async () => {
  const tmp = await mkdtemp(path.join(os.tmpdir(), 'dsh-constraints-'))
  const rulesDir = path.join(tmp, 'rules')
  await mkdir(rulesDir)
  const body = '---\nname: x\n---\n\n正文 {{不存在的变量}}。\n'
  await writeFile(path.join(rulesDir, 'global-user-constraints.md'), body, 'utf8')
  const previousHome = process.env.DSH_HOME
  process.env.DSH_HOME = path.join(tmp, 'dsh-home')
  try {
    const section = constraintsSection(tmp)
    assert.ok(section)
    assert.equal(section.interpolate, false)
    // interpolate: false 下原文原样保留，包括 frontmatter 与 {{}} 占位符。
    assert.match(section.text, /\{\{不存在的变量\}\}/u)
    assert.match(section.text, /^---/u)
  } finally {
    if (previousHome === undefined) delete process.env.DSH_HOME
    else process.env.DSH_HOME = previousHome
  }
})
