import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const REPO = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const SCRIPTS = join(REPO, 'shared', 'scripts');
const HOOKS = ['inject-constraints.js', 'inject-clock.js', 'inject-compact.js'];
const ITERATIONS = 200;

function mulberry32(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const random = mulberry32(0x5eed);
const pieces = [
  '{"hook_event_name":"SessionStart","source":"start"}',
  '{',
  '}',
  '[]',
  '"x"',
  'null',
  '42',
  '{"session_id":',
  ',,,,',
  '{{{{',
  '\u0000\u0001',
  '长期中文与 emoji 🚀 混合',
  'a'.repeat(4096),
];
function randomPayload() {
  const count = 1 + Math.floor(random() * 6);
  const out = [];
  for (let i = 0; i < count; i += 1) out.push(pieces[Math.floor(random() * pieces.length)]);
  return out.join(random() < 0.5 ? '' : ' ');
}

test('hooks 对畸形输入静默且退出码为 0', () => {
  for (const hook of HOOKS) {
    for (let i = 0; i < ITERATIONS; i += 1) {
      const payload = randomPayload();
      const result = spawnSync(process.execPath, [join(SCRIPTS, hook)], {
        input: payload,
        encoding: 'utf8',
        env: { ...process.env, QODER_PLUGIN_ROOT: REPO },
      });
      assert.equal(result.status, 0, `${hook} 收到畸形输入后退出码非 0`);
      if (result.stdout && result.stdout.trim()) {
        const parsed = JSON.parse(result.stdout);
        assert.equal(typeof parsed, 'object');
        if (parsed && parsed.hookSpecificOutput) {
          assert.equal(typeof parsed.hookSpecificOutput.hookEventName, 'string');
          assert.equal(typeof parsed.hookSpecificOutput.additionalContext, 'string');
        }
      }
    }
  }
});
