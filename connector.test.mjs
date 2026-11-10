import { createServer } from 'node:http';
import assert from 'node:assert/strict';
import test from 'node:test';
import { submitRequest } from './connector.mjs';

test('submits normalized data and handles HTTP failure', async t => {
  const server = createServer(async (req, res) => {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    res.writeHead(req.url === '/requests' && req.method === 'POST' ? 201 : 404,
      { 'Content-Type': 'application/json' });
    res.end(Buffer.concat(chunks));
  });
  t.after(() => server.close());
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  const request = { title: ' نمونه ', description: 'شرح', status: 'approved' };
  assert.deepEqual(await submitRequest(base + '/requests', request),
    { title: 'نمونه', description: 'شرح' });
  await assert.rejects(submitRequest(base + '/missing', request), /HTTP 404/);
  await assert.rejects(submitRequest(base, { title: ' ' }), TypeError);
});
