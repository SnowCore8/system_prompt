#!/usr/bin/env node
/**
 * Qoder 约束注入钩子：SessionStart 注入约束全文，UserPromptSubmit 发送固定提醒。
 *
 * 根目录优先取显式参数（argv[2]），其次宿主环境变量，最后从脚本位置向上查找。
 * `source=resume` 或任一配置根/项目级文件已有同内容时跳过；正文缺失、读取失败或
 * 超过 40 KiB 时只输出提示，不注入全文。异常静默退出 0，不阻断会话。
 */

import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const RULES_FILENAME = "global-user-constraints.md";
const MAX_BYTES = 40 * 1024;
const SKIP_SOURCES = new Set(["resume"]);
const PLUGIN_ROOT_ENVS = ["QODER_PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT"];
const CONFIG_ENVS = ["QODERCN_CONFIG_DIR", "QODER_CONFIG_DIR", "QWEN_HOME", "QWEN_CONFIG_DIR"];
const RULES_DIRS = ["constraints", "rules"];

function pluginRoot(argv) {
  if (argv.length > 2 && argv[2]) {
    return argv[2];
  }
  for (const name of PLUGIN_ROOT_ENVS) {
    const value = process.env[name];
    if (value) {
      return value;
    }
  }
  let current = __dirname;
  while (current !== dirname(current)) {
    for (const directory of RULES_DIRS) {
      if (existsSync(join(current, directory, RULES_FILENAME))) {
        return current;
      }
    }
    current = dirname(current);
  }
  return dirname(__dirname);
}

function rulesPathFor(root) {
  for (const directory of RULES_DIRS) {
    const candidate = join(root, directory, RULES_FILENAME);
    if (existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

function projectDirs(cwd) {
  let start;
  try {
    start = resolve(cwd);
  } catch {
    return [];
  }
  const dirs = [];
  let current = start;
  while (true) {
    dirs.push(current);
    if (existsSync(join(current, ".git"))) {
      break;
    }
    const parent = dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }
  return dirs;
}

function configRoots() {
  const roots = [];
  for (const name of CONFIG_ENVS) {
    const value = process.env[name];
    if (value) {
      roots.push(value);
    }
  }
  roots.push(join(homedir(), ".qoder-cn"), join(homedir(), ".qoder"), join(homedir(), ".qwen"));
  return roots;
}

function candidateFiles(payload) {
  const files = [];
  for (const root of configRoots()) {
    files.push(join(root, "rules", RULES_FILENAME), join(root, "AGENTS.md"), join(root, "QWEN.md"));
  }
  const cwd = typeof payload.cwd === "string" && payload.cwd ? payload.cwd : process.cwd();
  for (const dir of projectDirs(cwd)) {
    files.push(
      join(dir, ".qoder", "rules", RULES_FILENAME),
      join(dir, ".qwen", "rules", RULES_FILENAME),
      join(dir, "AGENTS.md"),
      join(dir, "AGENTS.local.md"),
      join(dir, "QWEN.md"),
      join(dir, "QWEN.local.md"),
    );
  }
  return files;
}

function hasSameContent(filePath, digest) {
  try {
    const data = readFileSync(filePath);
    return createHash("sha256").update(data).digest("hex") === digest;
  } catch {
    return false;
  }
}

function emit(event, context) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext: context,
    },
  }) + "\n");
}

function readStdin() {
  return new Promise((resolveInput, reject) => {
    const chunks = [];
    process.stdin.on("data", (chunk) => chunks.push(chunk));
    process.stdin.on("end", () => resolveInput(Buffer.concat(chunks)));
    process.stdin.on("error", reject);
  });
}

async function main() {
  let payload;
  try {
    payload = JSON.parse((await readStdin()).toString("utf-8"));
  } catch {
    return 0;
  }
  if (typeof payload !== "object" || payload === null) {
    return 0;
  }

  const event = payload.hook_event_name;
  if (event === "UserPromptSubmit") {
    emit("UserPromptSubmit", "Never violate global user constraints.");
    return 0;
  }
  if (event !== "SessionStart") {
    return 0;
  }
  if (typeof payload.source === "string" && SKIP_SOURCES.has(payload.source)) {
    return 0;
  }

  const root = pluginRoot(process.argv);
  const rulesPath = rulesPathFor(root);
  if (!rulesPath) {
    emit("SessionStart", "全局用户约束未注入：插件包内未找到 rules/ 或 constraints/ 下的 global-user-constraints.md。本会话须先读取约束；无法读取的，停止并报告安装缺失。");
    return 0;
  }

  let data;
  try {
    data = readFileSync(rulesPath);
  } catch (error) {
    const reason = error.code || error.message || "未知错误";
    emit("SessionStart", `全局用户约束未注入：读取 ${rulesPath} 失败（${reason}）。本会话须先读取约束；无法读取的，停止并报告。`);
    return 0;
  }

  const digest = createHash("sha256").update(data).digest("hex");
  if (candidateFiles(payload).some((file) => hasSameContent(file, digest))) {
    return 0;
  }
  if (data.length > MAX_BYTES) {
    emit("SessionStart", `全局用户约束正文超过 40 KiB 硬上限，未直接注入；应当读取 ${rulesPath} 并在本会话遵守。`);
    return 0;
  }

  emit("SessionStart", `全局用户约束（由插件于会话启动时注入，必须遵守）：\n\n${data.toString("utf-8").trim()}`);
  return 0;
}

main().then((code) => {
  process.exitCode = code;
}).catch(() => {
  process.exitCode = 0;
});
