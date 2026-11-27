#!/usr/bin/env node
/**
 * 同步五个发布清单与 package-lock 的版本；不修改 CHANGELOG，不提交或打 tag。
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO = join(dirname(fileURLToPath(import.meta.url)), '..');
const version = process.argv[2];
if (!version || !/^\d+\.\d+\.\d+$/.test(version)) {
  console.error('用法: node scripts/bump-version.mjs <major.minor.patch>');
  process.exit(2);
}

const targets = JSON.parse(readFileSync(join(REPO, 'scripts', 'version-manifests.json'), 'utf8')).versionFiles;

for (const relative of targets) {
  const path = join(REPO, relative);
  const data = JSON.parse(readFileSync(path, 'utf8'));
  data.version = version;
  if (relative === 'package-lock.json' && data.packages?.['']) {
    data.packages[''].version = version;
  }
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`);
  console.log(`${relative}: ${version}`);
}
