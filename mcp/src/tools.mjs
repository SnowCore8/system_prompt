/** MCP 工具注册与纯函数实现（纯函数供单元测试直接使用）。 */
import { z } from 'zod';

import { matchClauses } from './charter.mjs';
import { listSkills } from './skills.mjs';

export const DISCLAIMER = '本结果为启发式审查，依据治理章程条款静态匹配，不构成人工审查或批准结论。';

export function classifyRisk({ files = 1, shared = false, production = false, irreversible = false }) {
  const reasons = [];
  if (production || irreversible) {
    reasons.push('涉及生产或不可逆操作');
    return { level: 'R2', reasons };
  }
  if (shared || files > 1) {
    reasons.push(shared ? '涉及共享状态或共享分支' : `涉及 ${files} 个文件`);
    return { level: 'R1', reasons };
  }
  reasons.push('可逆、局部、无共享状态');
  return { level: 'R0', reasons };
}

export function gateTemplate({ gate, decision, evidence, conditions, owner, nextGate }) {
  const lines = ['## 门禁记录', ''];
  lines.push(`- 门禁：${gate}`);
  lines.push(`- 决定：${decision}`);
  lines.push(`- 证据：${evidence || '（待补充：测试输出、审查结论、演练记录、指标或明确批准）'}`);
  if (conditions) lines.push(`- 条件：${conditions}（附负责人与到期日）`);
  lines.push(`- 负责人：${owner || '（待补充）'}`);
  lines.push(`- 下一门禁：${nextGate || '（待补充）'}`);
  lines.push('', `> ${DISCLAIMER}`);
  return lines.join('\n');
}

const STAGE_MAP = {
  question: { stage: 'S0', gate: 'G0', evidence: '请求复述、授权依据、风险级别、停止条件' },
  requirement: { stage: 'S1', gate: 'G1', evidence: '需求与用户、结果指标、收益基线、选项比较' },
  design: { stage: 'S2', gate: 'G2', evidence: '范围与非范围、验收标准、ADR、测试策略、回滚计划' },
  build: { stage: 'S3', gate: 'G3', evidence: '可运行增量、相关测试、评审结论、DoD 检查' },
  verify: { stage: 'S4', gate: 'G4', evidence: '测试输出、安全与性能结论、验收结论、独立审查' },
  release: { stage: 'S5', gate: 'G5', evidence: '版本与制品、CI/CD 记录、回滚演练、生产授权' },
  operate: { stage: 'S6', gate: 'G6', evidence: '监控告警、值守升级、恢复演练、事故记录' },
  retire: { stage: 'S7', gate: 'G7', evidence: '收益对照、复盘行动、退役归档、交接' },
};

export function stageAdvice(kind) {
  const entry = STAGE_MAP[kind] || STAGE_MAP.question;
  return { ...entry, note: DISCLAIMER };
}

export function changeTemplate({ baseline, change, reason }) {
  const lines = ['## 变更请求', ''];
  lines.push(`- 原基线：${baseline || '（待补充）'}`);
  lines.push(`- 拟变更：${change || '（待补充）'}`);
  lines.push(`- 原因：${reason || '（待补充）'}`);
  lines.push('- 影响评估：');
  lines.push('- 替代方案：');
  lines.push('- 回滚方式：');
  lines.push('- 需重新取得的授权：');
  lines.push('', `> ${DISCLAIMER}`);
  return lines.join('\n');
}

export const RELEASE_CHECKLIST = `## 发布检查单（G5）
- [ ] G4 证据齐备，全量校验通过
- [ ] 版本清单与 tag 一致
- [ ] 变更记录已加版本节，破坏性变更写明迁移路径
- [ ] 工作区干净，出包校验通过
- [ ] 生产授权已取得（逐次明确同意）
- [ ] 回滚路径与演练就绪，可观测性与通告就绪
- [ ] 发布后核对制品、校验和与来源证明`;

export const RETROSPECTIVE = `## 复盘（G7）
- 收益对照：目标 vs 实际（引用 G1 基线）
- 偏差：范围 / 进度 / 成本 / 质量
- 教训：假设、执行、环境原因
- 行动项：每项有负责人与到期日
- 退役与归档：数据、制品、运行责任交接
- 未关闭风险：负责人与复核时间`;

export function registerTools(server) {
  server.registerTool(
    'constraints_check',
    {
      description: '对请求、方案或命令文本做治理章程条款级静态审查；结果仅供提示，不构成人工审查结论',
      inputSchema: z.object({
        text: z.string().describe('待审查的请求、方案或命令文本'),
      }),
    },
    async ({ text }) => {
      const hits = matchClauses(String(text));
      if (hits.length === 0) {
        return { content: [{ type: 'text', text: `未匹配到明显条款。\n> ${DISCLAIMER}` }] };
      }
      const body = hits.map((clause) => `- ${clause.id} ${clause.title}`).join('\n');
      return { content: [{ type: 'text', text: `可能相关的条款：\n${body}\n\n> ${DISCLAIMER}` }] };
    },
  );

  server.registerTool(
    'risk_classify',
    {
      description: '按文件数、共享状态、生产与不可逆性判定风险级别 R0/R1/R2',
      inputSchema: z.object({
        files: z.number().optional().describe('涉及的文件数量，默认 1'),
        shared: z.boolean().optional().describe('是否涉及共享分支、共享状态或共享配置'),
        production: z.boolean().optional().describe('是否涉及生产环境'),
        irreversible: z.boolean().optional().describe('是否含不可逆操作（推送、部署、删除、迁移等）'),
      }),
    },
    async ({ files, shared, production, irreversible }) => {
      const result = classifyRisk({
        files: files ?? 1,
        shared: shared ?? false,
        production: production ?? false,
        irreversible: irreversible ?? false,
      });
      return { content: [{ type: 'text', text: `风险级别：${result.level}\n依据：${result.reasons.join('；')}` }] };
    },
  );

  server.registerTool(
    'gate_record',
    {
      description: '生成门禁记录（G0–G7）模板',
      inputSchema: z.object({
        gate: z.string().describe('门禁编号，如 G4'),
        decision: z.string().describe('Go / Conditional Go / Hold / Recycle / No-Go'),
        evidence: z.string().describe('可核验证据链接或描述'),
        conditions: z.string().optional().describe('Conditional Go 的条件（可选）'),
        owner: z.string().optional().describe('负责人（可选）'),
        nextGate: z.string().optional().describe('下一门禁（可选）'),
      }),
    },
    async ({ gate, decision, evidence, conditions, owner, nextGate }) => {
      return {
        content: [{ type: 'text', text: gateTemplate({ gate, decision, evidence, conditions, owner, nextGate }) }],
      };
    },
  );

  server.registerTool(
    'list_skills',
    {
      description: '列出本套件的全部 skill 及其触发描述',
      inputSchema: z.object({}),
    },
    async () => {
      const skills = listSkills();
      if (skills.length === 0) {
        return { content: [{ type: 'text', text: 'skills/ 目录暂不可用或为空。' }] };
      }
      const body = skills.map((skill) => `- ${skill.name}：${skill.description}`).join('\n');
      return { content: [{ type: 'text', text: `共 ${skills.length} 个 skill：\n${body}` }] };
    },
  );

  server.registerTool(
    'lifecycle_stage',
    {
      description: '按请求类型建议所处生命周期阶段、门禁与最低证据清单',
      inputSchema: z.object({
        kind: z.string().describe('question | requirement | design | build | verify | release | operate | retire'),
      }),
    },
    async ({ kind }) => {
      const advice = stageAdvice(kind);
      return {
        content: [
          {
            type: 'text',
            text: `建议阶段：${advice.stage}（门禁 ${advice.gate}）\n最低证据：${advice.evidence}\n> ${advice.note}`,
          },
        ],
      };
    },
  );

  server.registerTool(
    'change_assessment',
    {
      description: '生成基线变更请求与影响评估模板',
      inputSchema: z.object({
        baseline: z.string().describe('原基线描述'),
        change: z.string().describe('拟变更内容'),
        reason: z.string().describe('变更原因'),
      }),
    },
    async ({ baseline, change, reason }) => {
      return { content: [{ type: 'text', text: changeTemplate({ baseline, change, reason }) }] };
    },
  );

  server.registerTool(
    'release_checklist',
    {
      description: '生成发布门（G5）检查单',
      inputSchema: z.object({}),
    },
    async () => ({ content: [{ type: 'text', text: RELEASE_CHECKLIST }] }),
  );

  server.registerTool(
    'retrospective',
    {
      description: '生成收尾门（G7）复盘模板',
      inputSchema: z.object({}),
    },
    async () => ({ content: [{ type: 'text', text: RETROSPECTIVE }] }),
  );
}
