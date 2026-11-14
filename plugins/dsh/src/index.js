/**
 * DSH bundle：把包内 skills/ 注册为 skill 提供者。
 *
 * 使用方在 profile 里安装本 bundle 后，十八个通用规范 skill 会出现在会话目录中；
 * 约束正文与时间注入由 DSH 自身的用户级 AGENTS.md 与系统时间提示承担，本模块只负责 skill。
 */
import { existsSync } from 'node:fs'
import { readFile, readdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'global-user-constraints-skills'
export const inject = ['skills']

const PROVIDER = 'global-user-constraints'
const RANK = 700
const SOURCE = 'bundled'
function findPackageRoot() {
  let current = path.dirname(fileURLToPath(import.meta.url))
  for (;;) {
    if (existsSync(path.join(current, 'package.json'))) return current
    const parent = path.dirname(current)
    if (parent === current) return path.dirname(fileURLToPath(import.meta.url))
    current = parent
  }
}

const SKILLS_ROOT = path.join(findPackageRoot(), 'skills')

const NAME_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/

function unquote(value) {
  const text = value.trim()
  if (text.length >= 2 && (text[0] === '"' || text[0] === "'") && text.at(-1) === text[0]) {
    return text.slice(1, -1)
  }
  return text
}

function parseBoolean(value) {
  if (value === undefined) return undefined
  const text = unquote(value).toLowerCase()
  if (['true', 'yes', 'on', '1'].includes(text)) return true
  if (['false', 'no', 'off', '0'].includes(text)) return false
  return undefined
}

/**
 * 解析单个 SKILL.md 的 frontmatter 与正文。
 * @param {string} raw SKILL.md 全文
 * @returns {{name:string, description:string, whenToUse?:string, invocation:object, content:string}|undefined}
 *   frontmatter 缺失、name 不合法或 description 为空时返回 undefined。
 */
export function parseSkill(raw) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(raw)
  if (!match) return undefined
  const fields = {}
  for (const line of match[1].split(/\r?\n/)) {
    const pair = /^([A-Za-z][\w-]*):\s*(.*)$/.exec(line)
    if (pair && pair[1] in fields === false) fields[pair[1]] = pair[2]
  }
  const skillName = unquote(fields.name ?? '')
  const description = unquote(fields.description ?? '')
  if (!NAME_PATTERN.test(skillName) || description.length === 0) return undefined
  const whenToUse = unquote(fields.whenToUse ?? '')
  return {
    name: skillName,
    description,
    ...(whenToUse ? { whenToUse } : {}),
    invocation: {
      modelInvocable: parseBoolean(fields['disable-model-invocation']) !== true,
      userInvocable: parseBoolean(fields['user-invocable']) !== false,
    },
    content: match[2].trim(),
  }
}

async function readSkill(file) {
  try {
    return parseSkill(await readFile(file, 'utf8'))
  } catch {
    return undefined
  }
}

export function apply(ctx) {
  ctx.skills.registerProvider(() => ({
    name: PROVIDER,
    async list() {
      let entries
      try {
        entries = await readdir(SKILLS_ROOT, { withFileTypes: true })
      } catch (error) {
        if (error?.code === 'ENOENT') return []
        throw error
      }
      const candidates = []
      for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
        if (!entry.isDirectory()) continue
        const directory = path.join(SKILLS_ROOT, entry.name)
        const file = path.join(directory, 'SKILL.md')
        const parsed = await readSkill(file)
        if (!parsed) continue
        candidates.push({
          name: parsed.name,
          description: parsed.description,
          ...(parsed.whenToUse ? { whenToUse: parsed.whenToUse } : {}),
          invocation: parsed.invocation,
          provider: PROVIDER,
          source: SOURCE,
          rank: RANK,
          locator: { file, directory },
          resourceBase: { kind: 'directory', path: directory },
          path: file,
        })
      }
      return candidates
    },
    async get(candidate) {
      const locator = candidate?.locator
      if (!locator?.file) return undefined
      const parsed = await readSkill(locator.file)
      if (!parsed) return undefined
      return {
        name: parsed.name,
        description: parsed.description,
        ...(parsed.whenToUse ? { whenToUse: parsed.whenToUse } : {}),
        invocation: parsed.invocation,
        provider: PROVIDER,
        source: SOURCE,
        rank: RANK,
        locator,
        resourceBase: { kind: 'directory', path: locator.directory },
        path: locator.file,
        content: parsed.content,
      }
    },
  }))
}
