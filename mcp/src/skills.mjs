/** 读取 skills/ 目录的 frontmatter 索引。 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
export const SKILLS_PATH = join(HERE, '..', '..', 'skills');

export function listSkills() {
  if (!existsSync(SKILLS_PATH)) return [];
  const out = [];
  for (const entry of readdirSync(SKILLS_PATH, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const file = join(SKILLS_PATH, entry.name, 'SKILL.md');
    if (!existsSync(file)) continue;
    const text = readFileSync(file, 'utf8');
    const match = /^description:\s*(.+)$/m.exec(text);
    out.push({ name: entry.name, description: match ? match[1].trim() : '' });
  }
  return out.sort((a, b) => a.name.localeCompare(b.name));
}
