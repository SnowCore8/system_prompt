import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

import { registerTools } from './src/tools.mjs';

const server = new McpServer({ name: 'se-governance', version: '1.0.0' });
registerTools(server);
await server.connect(new StdioServerTransport());
