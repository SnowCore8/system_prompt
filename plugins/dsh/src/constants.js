/**
 * DSH bundle 的插件标识、skill provider 元数据与全局用户约束 section 参数。
 *
 * 这些值同时被 index.js 的导出与各内部模块使用，集中于此避免重复定义。
 */
export const NAME = 'global-user-constraints-skills'
export const INJECT = ['skills', 'systemPrompt']
export const PROVIDER = 'global-user-constraints'
export const RANK = 700
export const SOURCE = 'bundled'
export const SECTION_NAME = 'global-user-constraints'
// 全局用户约束排在计划策略（500）之前。
export const SECTION_ORDER = 400
export const CONSTRAINTS_FILENAME = 'global-user-constraints.md'
// 常驻约束正文的硬上限，与 scripts/check.sh、shared/scripts/inject-constraints.js 保持一致。
export const CONSTRAINTS_MAX_BYTES = 64 * 1024
