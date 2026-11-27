import assert from 'node:assert/strict'
import { mkdir, mkdtemp, readdir, readFile, rm, writeFile } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath, pathToFileURL } from 'node:url'

import {
  CONSTRAINTS_MAX_BYTES,
  INJECT,
  NAME,
  PROVIDER,
  RANK,
  SECTION_NAME,
  SECTION_ORDER,
  SOURCE,
} from '../../plugins/dsh/src/constants.js'
import { constraintsSection, sha256 } from '../../plugins/dsh/src/constraints.js'
import {
  apply,
  inject,
  name,
  constraintsSection as reexportedConstraintsSection,
  parseSkill as reexportedParseSkill,
} from '../../plugins/dsh/src/index.js'
import { findPackageRoot, userInstructionFiles } from '../../plugins/dsh/src/paths.js'
import { createSkillsProvider, parseSkill } from '../../plugins/dsh/src/skills.js'

const PACKAGE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')

async function temporaryDirectory(t, prefix) {
  const directory = await mkdtemp(path.join(os.tmpdir(), prefix))
  t.after(() => rm(directory, { recursive: true, force: true }))
  return directory
}

async function createRulesPackage(t, body) {
  const root = await temporaryDirectory(t, 'dsh-constraints-')
  await mkdir(path.join(root, 'rules'))
  await writeFile(path.join(root, 'rules', 'global-user-constraints.md'), body, 'utf8')
  return root
}

function setEnvironment(key, value) {
  const previous = process.env[key]
  process.env[key] = value
  return () => {
    if (previous === undefined) delete process.env[key]
    else process.env[key] = previous
  }
}

async function withIsolatedUserHomes(t, callback) {
  const dshHome = await temporaryDirectory(t, 'dsh-home-')
  const agentsHome = await temporaryDirectory(t, 'agents-home-')
  const restoreDshHome = setEnvironment('DSH_HOME', dshHome)
  const restoreAgentsHome = setEnvironment('DSH_AGENTS_HOME', agentsHome)
  try {
    return await callback({ dshHome, agentsHome })
  } finally {
    restoreDshHome()
    restoreAgentsHome()
  }
}

function createContext() {
  const factories = []
  const sections = []
  const ctx = {
    skills: {
      registerProvider(factory) {
        factories.push(factory)
      },
    },
    systemPrompt: {
      section(entry) {
        sections.push(entry)
      },
    },
  }
  apply(ctx)
  assert.equal(factories.length, 1)
  return { provider: factories[0](), sections }
}

test('constants keep the bundle identity and injection contract', () => {
  assert.equal(NAME, 'se-governance-skills')
  assert.deepEqual(INJECT, ['skills', 'systemPrompt'])
  assert.equal(PROVIDER, 'se-governance')
  assert.equal(RANK, 700)
  assert.equal(SOURCE, 'bundled')
  assert.equal(SECTION_NAME, 'se-governance')
  assert.equal(SECTION_ORDER, 400)
  assert.equal(CONSTRAINTS_MAX_BYTES, 64 * 1024)
})

test('index exports the bundle identity and re-exports legacy helpers', () => {
  assert.equal(name, NAME)
  assert.deepEqual(inject, INJECT)
  assert.equal(typeof apply, 'function')
  assert.equal(reexportedConstraintsSection, constraintsSection)
  assert.equal(reexportedParseSkill, parseSkill)
})

test('list returns the twenty-four bundled skills', async () => {
  const { provider } = createContext()
  const candidates = await provider.list()
  const directories = (await readdir(path.join(PACKAGE_ROOT, 'skills'))).filter((entry) => !entry.startsWith('.'))
  assert.equal(candidates.length, 24)
  assert.equal(candidates.length, directories.length)
  assert.deepEqual(
    candidates.map((item) => item.name),
    [...candidates.map((item) => item.name)].sort(),
  )
  assert.equal(provider.name, PROVIDER)
  for (const candidate of candidates) {
    assert.ok(candidate.description.length > 0)
    assert.equal(candidate.provider, PROVIDER)
    assert.equal(candidate.source, SOURCE)
    assert.equal(candidate.rank, RANK)
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
  assert.equal(definition.name, candidate.name)
  assert.equal(definition.provider, PROVIDER)
  assert.equal(definition.source, SOURCE)
  assert.equal(definition.rank, RANK)
  assert.deepEqual(definition.locator, candidate.locator)
})

test('get returns undefined for a missing file', async () => {
  const { provider } = createContext()
  const definition = await provider.get({ locator: { file: path.join(PACKAGE_ROOT, 'skills', 'missing', 'SKILL.md') } })
  assert.equal(definition, undefined)
  assert.equal(await provider.get({}), undefined)
})

test('createSkillsProvider lists and loads skill definitions', async (t) => {
  const skillsRoot = await temporaryDirectory(t, 'dsh-skills-')
  const skillDirectory = path.join(skillsRoot, 'demo-skill')
  await mkdir(skillDirectory)
  const skillFile = path.join(skillDirectory, 'SKILL.md')
  const raw = [
    '---',
    'name: demo-skill',
    'description: 演示用 skill',
    'whenToUse: 需要演示时',
    '---',
    '',
    '# 演示',
    '',
    '正文内容。',
    '',
  ].join('\n')
  await writeFile(skillFile, raw, 'utf8')
  const provider = createSkillsProvider(skillsRoot)()
  assert.equal(provider.name, PROVIDER)
  const candidates = await provider.list()
  assert.equal(candidates.length, 1)
  const [candidate] = candidates
  assert.equal(candidate.name, 'demo-skill')
  assert.equal(candidate.description, '演示用 skill')
  assert.equal(candidate.whenToUse, '需要演示时')
  assert.equal(candidate.provider, PROVIDER)
  assert.equal(candidate.source, SOURCE)
  assert.equal(candidate.rank, RANK)
  assert.deepEqual(candidate.invocation, { modelInvocable: true, userInvocable: true })
  assert.deepEqual(candidate.locator, { file: skillFile, directory: skillDirectory })
  assert.deepEqual(candidate.resourceBase, { kind: 'directory', path: skillDirectory })
  assert.equal(candidate.path, skillFile)
  const definition = await provider.get(candidate)
  assert.ok(definition)
  assert.equal(definition.content, '# 演示\n\n正文内容。')
  assert.equal(definition.path, skillFile)
  assert.equal(await provider.get({ locator: { file: path.join(skillDirectory, 'missing.md') } }), undefined)
})

test('list returns an empty array when the skills root is missing', async (t) => {
  const root = path.join(await temporaryDirectory(t, 'dsh-skills-missing-'), 'missing')
  const provider = createSkillsProvider(root)()
  assert.deepEqual(await provider.list(), [])
})

test('parseSkill keeps frontmatter and invocation parsing', () => {
  const parsed = parseSkill(
    '---\nname: demo-skill\ndescription: "演示用 skill"\nwhenToUse: 需要演示时\nuser-invocable: false\ndisable-model-invocation: true\n---\n\n# 演示\n\n',
  )
  assert.ok(parsed)
  assert.equal(parsed.name, 'demo-skill')
  assert.equal(parsed.description, '演示用 skill')
  assert.equal(parsed.whenToUse, '需要演示时')
  assert.deepEqual(parsed.invocation, { modelInvocable: false, userInvocable: false })
  assert.equal(parsed.content, '# 演示')
  assert.equal(parseSkill('没有 frontmatter'), undefined)
  assert.equal(parseSkill('---\nname: Bad_Name\ndescription: x\n---\n'), undefined)
  assert.equal(parseSkill('---\nname: demo-skill\ndescription:\n---\n'), undefined)
})

test('sha256 returns a stable hex digest', () => {
  assert.equal(sha256('abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
})

test('userInstructionFiles returns only the two user-level AGENTS.md candidates', () => {
  assert.deepEqual(userInstructionFiles({ DSH_HOME: '/dsh-home', DSH_AGENTS_HOME: '/agents-home' }, '/home/tester'), [
    path.join('/dsh-home', 'AGENTS.md'),
    path.join('/agents-home', 'AGENTS.md'),
  ])
  assert.deepEqual(userInstructionFiles({}, '/home/tester'), [
    path.join('/home/tester', '.dsh', 'AGENTS.md'),
    path.join('/home/tester', '.agents', 'AGENTS.md'),
  ])
})

test('findPackageRoot locates the bundle root from the plugin module', () => {
  const moduleUrl = pathToFileURL(path.join(PACKAGE_ROOT, 'plugins', 'dsh', 'src', 'index.js')).href
  assert.equal(findPackageRoot(moduleUrl), PACKAGE_ROOT)
})

test('findPackageRoot walks up to the nearest package.json', async (t) => {
  const root = await temporaryDirectory(t, 'dsh-package-')
  const sourceDirectory = path.join(root, 'plugins', 'dsh', 'src')
  await mkdir(sourceDirectory, { recursive: true })
  await writeFile(path.join(root, 'package.json'), '{}', 'utf8')
  const moduleUrl = pathToFileURL(path.join(sourceDirectory, 'index.js')).href
  assert.equal(findPackageRoot(moduleUrl), root)
})

test('constraintsSection returns the stable section metadata', async (t) => {
  const body = '# 元数据约束\n\nMARKER-dsh-metadata-8f1c\n'
  const root = await createRulesPackage(t, body)
  await withIsolatedUserHomes(t, async () => {
    const section = constraintsSection(root)
    assert.ok(section)
    assert.equal(section.name, SECTION_NAME)
    assert.equal(section.order, SECTION_ORDER)
    assert.equal(section.interpolate, false)
    assert.equal(section.text, body.trim())
  })
})

test('constraintsSection dedupes against a matching user AGENTS.md', async (t) => {
  const body = '# 测试约束\n\nMARKER-dsh-dedupe-5e2d\n'
  const root = await createRulesPackage(t, body)
  await withIsolatedUserHomes(t, async ({ dshHome }) => {
    await writeFile(path.join(dshHome, 'AGENTS.md'), body, 'utf8')
    assert.equal(constraintsSection(root), undefined)
  })
})

test('constraintsSection dedupes against the DSH_AGENTS_HOME AGENTS.md', async (t) => {
  const body = '# 测试约束\n\nMARKER-dsh-agents-home-7a3e\n'
  const root = await createRulesPackage(t, body)
  await withIsolatedUserHomes(t, async ({ agentsHome }) => {
    await writeFile(path.join(agentsHome, 'AGENTS.md'), body, 'utf8')
    assert.equal(constraintsSection(root), undefined)
  })
})

test('constraintsSection returns undefined when the rules file is missing', async (t) => {
  const root = await temporaryDirectory(t, 'dsh-constraints-missing-')
  assert.equal(constraintsSection(root), undefined)
})

test('constraintsSection returns a hint instead of the full text when oversized', async (t) => {
  const body = '# 测试约束\n\nMARKER-dsh-oversized-6b2e\n' + 'x'.repeat(64 * 1024)
  const root = await createRulesPackage(t, body)
  await withIsolatedUserHomes(t, async () => {
    const section = constraintsSection(root)
    assert.ok(section)
    assert.equal(section.name, SECTION_NAME)
    assert.equal(section.order, SECTION_ORDER)
    assert.equal(section.interpolate, false)
    assert.ok(!section.text.includes('MARKER-dsh-oversized-6b2e'))
    assert.match(section.text, /64 KiB/u)
    assert.match(section.text, /rules[/\\]global-user-constraints\.md/u)
  })
})

test('apply registers only the constraints section', async (t) => {
  await withIsolatedUserHomes(t, async () => {
    const { sections } = createContext()
    assert.deepEqual(
      sections.map((item) => item.name),
      [SECTION_NAME],
    )
    assert.equal(sections.length, 1)
    assert.equal(sections[0].order, SECTION_ORDER)
    assert.equal(sections[0].interpolate, false)
  })
})

test('apply skips the constraints section when a user AGENTS.md already has it', async (t) => {
  const constraints = await readFile(path.join(PACKAGE_ROOT, 'rules', 'global-user-constraints.md'), 'utf8')
  await withIsolatedUserHomes(t, async ({ dshHome }) => {
    await writeFile(path.join(dshHome, 'AGENTS.md'), constraints, 'utf8')
    const { sections } = createContext()
    assert.deepEqual(sections, [])
  })
})

test('constraintsSection preserves literal text including frontmatter and placeholders', async (t) => {
  const body = '---\nname: x\n---\n\n正文 {{不存在的变量}}。\n'
  const root = await createRulesPackage(t, body)
  await withIsolatedUserHomes(t, async () => {
    const section = constraintsSection(root)
    assert.ok(section)
    assert.equal(section.interpolate, false)
    // interpolate: false 下原文原样保留，包括 frontmatter 与 {{}} 占位符。
    assert.match(section.text, /\{\{不存在的变量\}\}/u)
    assert.match(section.text, /^---/u)
  })
})
