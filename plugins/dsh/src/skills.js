/**
 * 包内 skills/ 的解析与 skill provider 构造。
 */
import { readdir, readFile } from 'node:fs/promises'
import path from 'node:path'

import { PROVIDER, RANK, SOURCE } from './constants.js'

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

/**
 * 读取并解析 SKILL.md；文件缺失或格式无效时返回 undefined。
 * @param {string} file SKILL.md 路径
 * @returns {Promise<ReturnType<typeof parseSkill>>}
 */
export async function readSkill(file) {
  try {
    return parseSkill(await readFile(file, 'utf8'))
  } catch {
    return undefined
  }
}

/**
 * 创建注册给 ctx.skills.registerProvider 的 provider 工厂。
 * @param {string} skillsRoot 包内 skills/ 目录
 * @returns {() => {name:string, list:Function, get:Function}}
 */
export function createSkillsProvider(skillsRoot) {
  return () => ({
    name: PROVIDER,
    async list() {
      let entries
      try {
        entries = await readdir(skillsRoot, { withFileTypes: true })
      } catch (error) {
        if (error?.code === 'ENOENT') return []
        throw error
      }
      const candidates = []
      for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
        if (!entry.isDirectory()) continue
        const directory = path.join(skillsRoot, entry.name)
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
  })
}
