// Wolves service worker: makes the app installable and shows a friendly screen
// when there is no internet. It never caches pages or data, so numbers are always live.
const CACHE = 'wsa-static-v3';
const ASSETS = ['/static/logo-mark.png', '/static/icon-192.png'];
const OFFLINE = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Offline</title></head><body style="margin:0;min-height:100vh;display:grid;place-items:center;background:#150A27;
color:#ECEEF2;font-family:system-ui,sans-serif;text-align:center;padding:24px">
<div><img src="/static/logo-mark.png" alt="" style="width:120px"><h1 style="font-size:20px;margin:18px 0 6px">No internet</h1>
<p style="opacity:.75;margin:0 0 18px">Wolves needs a connection. / لازم يكون في إنترنت.</p>
<button onclick="(navigator.serviceWorker ? navigator.serviceWorker.getRegistrations().then(rs => Promise.all(rs.map(r => r.unregister()))) : Promise.resolve()).finally(() => location.reload())" style="background:#8522FF;color:#fff;border:0;border-radius:4px;padding:12px 18px;font-weight:700">Try again</button>
</div></body></html>`;

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  // Online: the service worker stays out of the way entirely. Some iPhones fail any request routed
  // through it (pages got stuck on the offline screen, app.css never loaded). Only offline do we answer.
  if (req.method !== 'GET' || self.navigator.onLine !== false) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(() => new Response(OFFLINE, { headers: { 'Content-Type': 'text/html; charset=utf-8' } })));
  } else if (new URL(req.url).pathname.startsWith('/static/')) {
    e.respondWith(caches.match(req).then(r => r || fetch(req)));
  }
});
