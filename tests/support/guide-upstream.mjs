// Local fixture server for BFF transport tests. Never a production/provider fallback.
import { createServer } from 'node:http';
let cancelled = 0;
createServer(async (request, response) => {
  if (request.method === 'GET') {
    response.writeHead(200, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify({ fixture: true, cancelled, items: [], total: 0, next_cursor: null })); return;
  }
  let body = ''; for await (const chunk of request) body += chunk;
  const payload = JSON.parse(body);
  if (payload.question === 'cancel_fixture' || payload.question === 'stall_fixture') {
    response.writeHead(200, { 'Content-Type': 'text/event-stream' });
    response.write('event: meta\ndata: {"mode":"live"}\n\n');
    const timer = setTimeout(() => response.end('event: done\ndata: {}\n\n'), payload.question === 'stall_fixture' ? 120000 : 10000);
    response.on('close', () => { clearTimeout(timer); if (!response.writableEnded) cancelled++; });
    return;
  }
  response.writeHead(payload.question === 'limit_fixture' ? 429 : 200, { 'Content-Type': 'application/json', 'X-Request-ID': 'fixture_request' });
  response.end(JSON.stringify({ fixture: true, received: { cookie: request.headers.cookie, origin: request.headers.origin, authorization: request.headers.authorization ?? null, path: request.url, payload } }));
}).listen(3210, '127.0.0.1');
