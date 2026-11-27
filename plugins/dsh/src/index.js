/**
 * DSH bundle：把包内 skills/ 注册为 skill 提供者，并把全局用户约束注入系统提示。
 *
 * 安装本 bundle 后，二十四个软件工程 skill 会出现在会话目录中；约束全文经
 * ctx.systemPrompt.section() 自动注入，无需手动复制 ~/.dsh/AGENTS.md。
 * 若用户级 AGENTS.md 已加载同内容约束（按 sha256 去重），则跳过注入避免重复。
 * 时间由 DSH 自身注入，本模块不重复。
 */
import path from 'node:path'

import { INJECT, NAME } from './constants.js'
import { constraintsSection } from './constraints.js'
import { findPackageRoot } from './paths.js'
import { createSkillsProvider } from './skills.js'

export { parseSkill } from './skills.js'
export { constraintsSection }
export const name = NAME
export const inject = INJECT

const PACKAGE_ROOT = findPackageRoot(import.meta.url)
const SKILLS_ROOT = path.join(PACKAGE_ROOT, 'skills')

export function apply(ctx) {
  const section = constraintsSection(PACKAGE_ROOT)
  if (section) ctx.systemPrompt.section(section)

  ctx.skills.registerProvider(createSkillsProvider(SKILLS_ROOT))
}
