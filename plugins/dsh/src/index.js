/**
 * DSH bundle：把包内 skills/ 注册为 skill 提供者，并把用户全局约束注入系统提示。
 *
 * 安装本 bundle 后，十八个通用规范 skill 会出现在会话目录中；约束全文经
 * ctx.systemPrompt.section() 自动注入，无需手动复制 ~/.dsh/AGENTS.md。
 * 若用户级 AGENTS.md 已加载同内容约束（按 sha256 去重），则跳过注入避免重复。
 * 时间由 DSH 自身注入，本模块不重复。
 */
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { readFile, readdir } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'global-user-constraints-skills'
export const inject = ['skills', 'systemPrompt']

const PROVIDER = 'global-user-constraints'
const RANK = 700
const SOURCE = 'bundled'
const CONSTRAINTS_FILENAME = 'global-user-constraints.md'
// 常驻约束正文的硬上限，与 scripts/check.sh、shared/scripts/inject_constraints.py 保持一致。
const CONSTRAINTS_MAX_BYTES = 32 * 1024
const SECTION_NAME = 'global-user-constraints'
// 用户全局约束排在计划策略（500）之前。
const SECTION_ORDER = 400
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

function sha256(data) {
  return createHash('sha256').update(data).digest('hex')
}

/** DSH 指令链默认读取的用户级 AGENTS.md 候选。 */
function userInstructionFiles() {
  const home = os.homedir()
  const dshHome = process.env.DSH_HOME || path.join(home, '.dsh')
  const agentsHome = process.env.DSH_AGENTS_HOME || path.join(home, '.agents')
  return [path.join(dshHome, 'AGENTS.md'), path.join(agentsHome, 'AGENTS.md')]
}

/**
 * 从包内 rules/ 读取一个提示词 section；文件缺失或用户级 AGENTS.md 已含同内容时返回 undefined。
 * 传入 maxBytes 且文件超过上限时，返回提示读取原文的 section，不注入全文。
 * @param {string} pkgRoot 包根目录（含 rules/ 与 package.json）
 * @param {string} filename rules/ 下的文件名
 * @param {string} sectionName systemPrompt 章节名
 * @param {number} order 章节排序
 * @param {number} [maxBytes] 正文字节上限；省略时不限制
 * @returns {{name:string, order:number, text:string, interpolate:boolean}|undefined}
 */
function sectionFromFile(pkgRoot, filename, sectionName, order, maxBytes) {
  const filePath = path.join(pkgRoot, 'rules', filename)
  let data
  try {
    data = readFileSync(filePath)
  } catch {
    return undefined
  }
  const digest = sha256(data)
  for (const file of userInstructionFiles()) {
    try {
      if (existsSync(file) && sha256(readFileSync(file)) === digest) return undefined
    } catch {
      // 候选文件不可读时继续检查下一个，不阻断注入。
    }
  }
  if (maxBytes !== undefined && data.length > maxBytes) {
    return {
      name: sectionName,
      order,
      text: `用户全局约束正文超过 ${maxBytes / 1024} KiB 硬上限，未注入全文；应当读取 ${filePath} 并在本会话遵守。`,
      interpolate: false,
    }
  }
  return {
    name: sectionName,
    order,
    text: data.toString('utf8').trim(),
    interpolate: false,
  }
}

/** 用户全局约束 section；文件缺失或已去重时返回 undefined，超过 32 KiB 硬上限时返回提示 section。 */
export function constraintsSection(pkgRoot) {
  return sectionFromFile(pkgRoot, CONSTRAINTS_FILENAME, SECTION_NAME, SECTION_ORDER, CONSTRAINTS_MAX_BYTES)
}

export function apply(ctx) {
  const section = constraintsSection(findPackageRoot())
  if (section) ctx.systemPrompt.section(section)

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
