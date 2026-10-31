export const meta = {
  name: "ts2cpp",
  description:
    "按切片执行 TS→C++ 翻译流水线：Translator 翻译、Critic 钉住语义分歧、Fixer 逐个最小修复、Orchestrator 门禁放行",
  whenToUse:
    "已划定一个 TypeScript 切片、要翻译为 C++ 且需要逐条钉住语义分歧时使用。args 传 { slice, tsPath, cppPath, maxRounds? }，或直接传切片描述字符串",
  phases: [
    { title: "Translate" },
    { title: "Critique" },
    { title: "Fix" },
    { title: "Gate" },
  ],
};

const MAX_ROUNDS_DEFAULT = 3;
const RECORD_ONLY = "记录";
const PLUGIN_PREFIX = "global-user-constraints:";

const DIVERGENCE_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["id", "severity", "summary", "tsBehavior", "cppBehavior", "failingTest", "output"],
  properties: {
    id: { type: "string", description: "分歧编号，如 D1" },
    severity: { type: "string", enum: ["阻断放行", "需修复", "记录"] },
    summary: { type: "string" },
    tsBehavior: { type: "string", description: "TS 期望行为与证据位置，路径:行号" },
    cppBehavior: { type: "string" },
    failingTest: { type: "string", description: "失败测试文件路径" },
    output: { type: "string", description: "真实失败输出摘要，含退出码" },
  },
};

const CRITIQUE_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["divergences", "covered", "uncovered"],
  properties: {
    divergences: { type: "array", items: DIVERGENCE_SCHEMA },
    covered: { type: "array", items: { type: "string" }, description: "已验证等价的行为" },
    uncovered: { type: "array", items: { type: "string" }, description: "未覆盖或未钉住的行为" },
  },
};

const FIX_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["divergenceId", "rootCause", "changed", "verification", "status"],
  properties: {
    divergenceId: { type: "string" },
    rootCause: { type: "string" },
    changed: { type: "string", description: "改动位置，路径:行号" },
    verification: { type: "string", description: "验证命令与真实输出摘要" },
    status: { type: "string", enum: ["已修复", "未修复", "需重构"] },
  },
};

const GATE_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["release", "reasons", "risks", "coverage", "unverified"],
  properties: {
    release: { type: "boolean", description: "是否放行本切片" },
    reasons: { type: "array", items: { type: "string" } },
    risks: { type: "array", items: { type: "string" } },
    coverage: { type: "array", items: { type: "string" } },
    unverified: { type: "array", items: { type: "string" } },
  },
};

async function runAgent(prompt, opts) {
  try {
    return await agent(prompt, opts);
  } catch (err) {
    const message = String(err && err.message ? err.message : err);
    if (!message.includes("Unknown agent type")) throw err;
    return await agent(prompt, { ...opts, agentType: PLUGIN_PREFIX + opts.agentType });
  }
}

const input = typeof args === "string" ? { slice: args } : args || {};
const slice = input.slice || "未指定切片";
const tsPath = input.tsPath || "由 Translator 按切片定位";
const cppPath = input.cppPath || "由 Translator 按工程约定定位";
const maxRounds =
  Number.isInteger(input.maxRounds) && input.maxRounds > 0 ? input.maxRounds : MAX_ROUNDS_DEFAULT;

const task = [`切片：${slice}`, `TS 源：${tsPath}`, `C++ 目标：${cppPath}`].join("\n");

function pending(divergences) {
  return (divergences || []).filter((d) => d && d.severity !== RECORD_ONLY);
}

function renderDivergences(divergences) {
  if (!divergences || divergences.length === 0) return "无已钉住的分歧。";
  return divergences
    .map(
      (d) =>
        `[${d.id}] 严重度=${d.severity}\n` +
        `  分歧：${d.summary}\n` +
        `  TS 行为：${d.tsBehavior}\n` +
        `  C++ 行为：${d.cppBehavior}\n` +
        `  失败测试：${d.failingTest}\n` +
        `  真实输出：${d.output}`,
    )
    .join("\n");
}

phase("Translate");
log(`ts2cpp 开始：${slice}`);
const translation = await runAgent(
  `${task}\n\n只翻译这个切片，TS 行为是唯一规范。产出文件、行为等价性说明、以及真实编译输出。`,
  { agentType: "Translator", phase: "Translate", label: "translate" },
);

phase("Critique");
log("开始猎杀语义分歧");
let critique = await runAgent(
  `${task}\n\nTranslator 交付如下：\n${translation}\n\n` +
    `只找茬，不修复，不修改生产代码。每个分歧都要有一个可复现的失败测试，并粘贴证明它失败的退出码与输出。`,
  { agentType: "Critic", phase: "Critique", label: "critique", schema: CRITIQUE_SCHEMA },
);

const fixes = [];
let round = 0;
let escalated = false;

while (critique && pending(critique.divergences).length > 0 && round < maxRounds) {
  round += 1;
  log(`第 ${round}/${maxRounds} 轮修复，待修 ${pending(critique.divergences).length} 条`);

  for (const divergence of pending(critique.divergences)) {
    const fix = await runAgent(
      `${task}\n\n只修这一条分歧，不做任何其他改动：\n${renderDivergences([divergence])}\n\n` +
        `禁止弱化或跳过测试。修复后运行该分歧的测试与本切片既有测试，给出真实输出。`,
      { agentType: "Fixer", phase: "Fix", label: `fix:${divergence.id}`, schema: FIX_SCHEMA },
    );
    if (fix) {
      fixes.push({ round, ...fix });
      if (fix.status !== "已修复") escalated = true;
    } else {
      escalated = true;
    }
  }

  critique = await runAgent(
    `${task}\n\n修复记录：\n${JSON.stringify(fixes, null, 2)}\n\n` +
      `重新审查该切片：确认已修分歧的测试通过，并继续寻找新的语义分歧。只找茬，不修复。`,
    { agentType: "Critic", phase: "Critique", label: `critique:round${round}`, schema: CRITIQUE_SCHEMA },
  );
}

const outstanding = pending(critique ? critique.divergences : []);
if (outstanding.length > 0 && round >= maxRounds) escalated = true;

phase("Gate");
log(`门禁：待放行分歧 ${outstanding.length} 条，修复轮次 ${round}`);
const gate = await runAgent(
  `${task}\n\n` +
    `翻译交付：\n${translation}\n\n` +
    `最终分歧清单：\n${renderDivergences(outstanding)}\n` +
    `已修复：\n${JSON.stringify(fixes, null, 2)}\n` +
    `覆盖行为：${JSON.stringify(critique ? critique.covered : [])}\n` +
    `未覆盖行为：${JSON.stringify(critique ? critique.uncovered : [])}\n\n` +
    `按门禁条款决定是否放行；证据缺失即不放行。测试要亲自运行或逐字核对后再采信。`,
  { agentType: "Orchestrator", phase: "Gate", label: "gate", schema: GATE_SCHEMA },
);

return {
  slice,
  rounds: round,
  escalated,
  translation,
  outstanding,
  fixes,
  coverage: critique ? critique.covered : [],
  unverified: critique ? critique.uncovered : [],
  gate,
};
