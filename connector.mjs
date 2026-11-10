export async function submitRequest(endpoint, request) {
  const url = new URL(endpoint);
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) {
    throw new TypeError('Expected an HTTP(S) endpoint without URL credentials');
  }
  const title = request?.title?.trim?.();
  const description = request?.description?.trim?.();
  if (!title || title.length > 120 || !description || description.length > 2000) {
    throw new TypeError('Expected a title (1–120) and description (1–2000)');
  }
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ title, description }),
    redirect: 'error',
    signal: AbortSignal.timeout(5000)
  });
  if (!response.ok) throw new Error('Request failed with HTTP ' + response.status);
  return response.json();
}
