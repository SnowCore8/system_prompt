#!/usr/bin/env node
/**
 * Qoder/Qwen 约束注入钩子：在 SessionStart 注入约束全文，UserPromptSubmit 发送固定提醒。
 * 不再安装到用户级 rules，确保卸载时无残留。
 * 如果项目级 AGENTS.md 或 QWEN.md 已含同内容，则跳过注入避免重复。
 */

import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const RULES_FILENAME = "global-user-constraints.md";
const MAX_BYTES = 40 * 1024;
const PLUGIN_ROOT_ENVS = ["QODER_PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT"];
const RULES_DIRS = ["constraints", "rules"];

function pluginRoot(argv) {
  if (argv.length > 1) {
    return argv[1];
  }
  for (const envName of PLUGIN_ROOT_ENVS) {
    const envValue = process.env[envName];
    if (envValue && existsSync(envValue)) {
      return envValue;
    }
  }
  let current = __dirname;
  while (current !== dirname(current)) {
    for (const dir of RULES_DIRS) {
      const rulesPath = join(current, dir, RULES_FILENAME);
      if (existsSync(rulesPath)) {
        return current;
      }
    }
    current = dirname(current);
  }
  return dirname(__dirname);
}

function projectDirs(cwd) {
  const dirs = [];
  if (cwd) dirs.push(cwd);
  let current = process.cwd();
  while (current !== dirname(current)) {
    dirs.push(current);
    current = dirname(current);
  }
  return dirs;
}

function candidateFiles(payload) {
  const files = [];
  const cwd = typeof payload.cwd === "string" ? payload.cwd : process.cwd();
  for (const dir of projectDirs(cwd)) {
    for (const name of ["AGENTS.md", "QWEN.md"]) {
      const filePath = join(dir, name);
      files.push(filePath);
    }
  }
  return files;
}

function hasSameContent(filePath, digest) {
  try {
    const data = readFileSync(filePath);
    const hash = createHash("sha256").update(data).digest("hex");
    return hash === digest;
  } catch {
    return false;
  }
}

function emit(event, context) {
  const output = {
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext: context,
    },
  };
  process.stdout.write(JSON.stringify(output) + "\n");
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  return chunks.join("");
}

async function main() {
  let payload;
  try {
    const input = await readStdin();
    payload = JSON.parse(input);
  } catch {
    process.exit(0);
  }

  const event = payload.hook_event_name;
  if (event === "UserPromptSubmit") {
    emit("UserPromptSubmit", "Never violate global user constraints.");
    process.exit(0);
  }

  if (event !== "SessionStart") {
    process.exit(0);
  }

  const root = pluginRoot(process.argv);
  let rulesPath = null;
  for (const dir of RULES_DIRS) {
    const p = join(root, dir, RULES_FILENAME);
    if (existsSync(p)) {
      rulesPath = p;
      break;
    }
  }

  if (!rulesPath) {
    process.exit(0);
  }

  let data;
  try {
    data = readFileSync(rulesPath);
  } catch {
    process.exit(0);
  }

  if (data.length > MAX_BYTES) {
    process.exit(0);
  }

  const digest = createHash("sha256").update(data).digest("hex");
  
  // 检查项目级 AGENTS.md 或 QWEN.md 是否已有同内容
  if (candidateFiles(payload).some(path => hasSameContent(path, digest))) {
    process.exit(0);
  }

  const context = data.toString("utf-8");
  emit("SessionStart", context);
  process.exit(0);
}

main().catch(() => process.exit(0));
