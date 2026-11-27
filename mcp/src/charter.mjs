/** 加载治理章程并建立条款索引。 */
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
export const RULES_PATH = join(HERE, '..', '..', 'rules', 'global-user-constraints.md');

export function loadCharter() {
  try {
    return readFileSync(RULES_PATH, 'utf8');
  } catch {
    return null;
  }
}

export function clauses() {
  const text = loadCharter();
  if (!text) return [];
  const bullet = /^- ([A-Z]{2,4})-(\d+) (.+)$/;
  const out = [];
  let current = null;
  for (const line of text.split('\n')) {
    const match = bullet.exec(line);
    if (match) {
      current = { id: `${match[1]}-${match[2]}`, title: match[3], body: [] };
      out.push(current);
    } else if (current && /^(#|-)/.test(line)) {
      current = null;
    } else if (current && line.trim()) {
      current.body.push(line.trim());
    }
  }
  return out;
}

const DOMAIN_KEYWORDS = {
  SEC: ['密码', '私钥', '令牌', 'token', '密钥', '凭据', '泄露', '个人信息', '隐私', '.env', '机密'],
  AUT: ['推送', 'push', '强制', '部署', '发布', '生产', '同意', '授权', '受保护', '共享分支'],
  IRR: ['删除', '覆盖', 'force', '--hard', '不可逆', '历史', '进程', '迁移', '回滚'],
  HON: ['完成', '通过', '测试', '声称', '验证', '编造', '占位', '未运行'],
  INT: ['优化', '加强', '调整', '改进', '意图', '歧义', '猜测'],
  GAT: ['门禁', '证据', '风险', '阶段', 'Go', 'Hold', 'Recycle', '基线', '依赖'],
  EXE: ['委派', '任务树', '工具', '子智能体', '进度', '提交', '复用'],
  CHG: ['变更', '范围', '重命名', '格式化', '清理'],
  UNC: ['例外', '豁免', '冲突', '超出范围'],
  OUT: ['输出', '报告', '结论', '状态'],
};

export function matchClauses(text) {
  const all = clauses();
  const lowered = text.toLowerCase();
  const domains = new Set();
  for (const [domain, keywords] of Object.entries(DOMAIN_KEYWORDS)) {
    if (keywords.some((keyword) => lowered.includes(keyword.toLowerCase()))) domains.add(domain);
  }
  return all.filter((clause) => domains.has(clause.id.split('-')[0]));
}
