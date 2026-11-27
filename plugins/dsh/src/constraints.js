/**
 * 全局用户约束 section：读取包内 rules/ 正文，并按 sha256 与用户级 AGENTS.md 去重。
 */
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { CONSTRAINTS_FILENAME, CONSTRAINTS_MAX_BYTES, SECTION_NAME, SECTION_ORDER } from './constants.js'
import { userInstructionFiles } from './paths.js'

/**
 * 计算字节内容的 sha256 摘要。
 * @param {Buffer|string} data 待摘要内容
 * @returns {string} 十六进制摘要
 */
export function sha256(data) {
  return createHash('sha256').update(data).digest('hex')
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
export function sectionFromFile(pkgRoot, filename, sectionName, order, maxBytes) {
  const filePath = path.join(pkgRoot, 'rules', filename)
  let data
  try {
    data = readFileSync(filePath)
  } catch {
    return undefined
  }
  const digest = sha256(data)
  for (const file of userInstructionFiles(process.env, os.homedir())) {
    try {
      if (sha256(readFileSync(file)) === digest) return undefined
    } catch {
      // 候选文件缺失或不可读时继续检查下一个，不阻断注入。
    }
  }
  if (maxBytes !== undefined && data.length > maxBytes) {
    return {
      name: sectionName,
      order,
      text: `全局用户约束正文超过 ${maxBytes / 1024} KiB 硬上限，未注入全文；应当读取 ${filePath} 并在本会话遵守。`,
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

/** 全局用户约束 section；文件缺失或已去重时返回 undefined，超过 40 KiB 硬上限时返回提示 section。 */
export function constraintsSection(pkgRoot) {
  return sectionFromFile(pkgRoot, CONSTRAINTS_FILENAME, SECTION_NAME, SECTION_ORDER, CONSTRAINTS_MAX_BYTES)
}
