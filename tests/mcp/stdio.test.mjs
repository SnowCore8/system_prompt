import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const REPO = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const SERVER = join(REPO, 'mcp', 'server.mjs');

function rpcCall(child, request) {
  return new Promise((resolve, reject) => {
    const onLine = (chunk) => {
      for (const line of chunk.toString().split('\n')) {
        if (!line.trim()) continue;
        try {
          const message = JSON.parse(line);
          if (message.id === request.id) {
            child.stdout.off('data', onLine);
            resolve(message);
          }
        } catch {
          // 忽略非 JSON 输出
        }
      }
    };
    child.stdout.on('data', onLine);
    child.stdin.write(`${JSON.stringify(request)}\n`);
    child.on('exit', (code) => reject(new Error(`server exited early: ${code}`)));
  });
}

test('stdio 冒烟：initialize → tools/list → tools/call', async (t) => {
  const child = spawn(process.execPath, [SERVER], { stdio: ['pipe', 'pipe', 'pipe'] });
  t.after(() => child.kill());

  const init = await rpcCall(child, {
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'smoke', version: '0' } },
  });
  assert.equal(init.result.serverInfo.name, 'se-governance');

  const list = await rpcCall(child, { jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} });
  const names = list.result.tools.map((tool) => tool.name);
  for (const name of [
    'constraints_check',
    'risk_classify',
    'gate_record',
    'list_skills',
    'lifecycle_stage',
    'change_assessment',
    'release_checklist',
    'retrospective',
  ]) {
    assert.ok(names.includes(name), `缺少工具 ${name}`);
  }

  const call = await rpcCall(child, {
    jsonrpc: '2.0',
    id: 3,
    method: 'tools/call',
    params: { name: 'risk_classify', arguments: { production: true } },
  });
  assert.ok(JSON.stringify(call.result).includes('R2'));
});
