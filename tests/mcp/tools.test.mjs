import assert from 'node:assert/strict';
import test from 'node:test';

import { clauses, matchClauses } from '../../mcp/src/charter.mjs';
import { listSkills } from '../../mcp/src/skills.mjs';
import {
  changeTemplate,
  classifyRisk,
  gateTemplate,
  RELEASE_CHECKLIST,
  RETROSPECTIVE,
  stageAdvice,
} from '../../mcp/src/tools.mjs';

test('章程条款索引可解析且覆盖十个域', () => {
  const all = clauses();
  assert.ok(all.length >= 50, `条款过少: ${all.length}`);
  const domains = new Set(all.map((clause) => clause.id.split('-')[0]));
  for (const domain of ['SEC', 'AUT', 'IRR', 'HON', 'INT', 'GAT', 'EXE', 'CHG', 'UNC']) {
    assert.ok(domains.has(domain), `缺少 ${domain} 域条款`);
  }
});

test('条款匹配按域命中', () => {
  const hits = matchClauses('把数据库密码写进日志并强制推送覆盖远端');
  const ids = hits.map((clause) => clause.id);
  assert.ok(
    ids.some((id) => id.startsWith('SEC-')),
    '应命中 SEC',
  );
  assert.ok(
    ids.some((id) => id.startsWith('IRR-')),
    '应命中 IRR',
  );
  assert.ok(
    ids.some((id) => id.startsWith('AUT-')),
    '应命中 AUT',
  );
});

test('风险分级判定', () => {
  assert.equal(classifyRisk({ files: 1 }).level, 'R0');
  assert.equal(classifyRisk({ files: 3 }).level, 'R1');
  assert.equal(classifyRisk({ shared: true }).level, 'R1');
  assert.equal(classifyRisk({ production: true }).level, 'R2');
  assert.equal(classifyRisk({ irreversible: true }).level, 'R2');
});

test('门禁记录模板包含全部字段', () => {
  const text = gateTemplate({
    gate: 'G4',
    decision: 'Conditional Go',
    evidence: '测试输出',
    conditions: '补齐安全结论',
    owner: '质量',
    nextGate: 'G5',
  });
  for (const field of [
    '门禁：G4',
    '决定：Conditional Go',
    '证据：测试输出',
    '条件：补齐安全结论',
    '负责人：质量',
    '下一门禁：G5',
  ]) {
    assert.ok(text.includes(field), `缺少 ${field}`);
  }
});

test('阶段建议映射', () => {
  const advice = stageAdvice('release');
  assert.equal(advice.stage, 'S5');
  assert.equal(advice.gate, 'G5');
  assert.ok(advice.evidence.includes('回滚'));
});

test('变更与收尾模板', () => {
  assert.ok(changeTemplate({ baseline: 'A', change: 'B', reason: 'C' }).includes('原基线：A'));
  assert.ok(RELEASE_CHECKLIST.includes('G5'));
  assert.ok(RETROSPECTIVE.includes('收益对照'));
});

test('skill 索引读取', () => {
  const skills = listSkills();
  assert.ok(Array.isArray(skills));
  for (const skill of skills) {
    assert.ok(skill.name && skill.description, '索引项缺少字段');
  }
});
