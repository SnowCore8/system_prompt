/**
 * 插件路径解析：定位包根目录与 DSH 用户级 AGENTS.md 候选文件。
 */
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

/**
 * 从调用模块的 URL 向上查找包含 package.json 的包根目录。
 * @param {string} metaUrl 调用方的 import.meta.url
 * @returns {string} 包根目录；找不到 package.json 时回退到模块所在目录
 */
export function findPackageRoot(metaUrl) {
  const moduleDirectory = path.dirname(fileURLToPath(metaUrl))
  let current = moduleDirectory
  for (;;) {
    if (existsSync(path.join(current, 'package.json'))) return current
    const parent = path.dirname(current)
    if (parent === current) return moduleDirectory
    current = parent
  }
}

/**
 * DSH 指令链默认读取的用户级 AGENTS.md 候选。
 * @param {Record<string, string | undefined>} env 环境变量表
 * @param {string} home 用户主目录
 * @returns {string[]} 形如 [<DSH_HOME>/AGENTS.md, <DSH_AGENTS_HOME>/AGENTS.md] 的候选路径
 */
export function userInstructionFiles(env, home) {
  const dshHome = env.DSH_HOME || path.join(home, '.dsh')
  const agentsHome = env.DSH_AGENTS_HOME || path.join(home, '.agents')
  return [path.join(dshHome, 'AGENTS.md'), path.join(agentsHome, 'AGENTS.md')]
}
