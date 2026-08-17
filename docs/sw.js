/* Service worker: deja la app utilizable sin datos.
   El cascarón se guarda al instalar; el contenido, conforme lo pides. */

const CACHE = 'andes-v1';
const CASCARON = [
  './', './index.html', './css/estilo.css', './icono.svg',
  './js/app.js', './js/feed.js', './js/datos.js',
  './js/almacen.js', './js/tarjetas.js', './js/mate.js',
  './contenido/cronograma.json', './contenido/manifiesto.json',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CASCARON)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(claves => Promise.all(claves.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(resp => {
        const copia = resp.clone();
        caches.open(CACHE).then(c => c.put(e.request, copia)).catch(() => {});
        return resp;
      })
      .catch(() => caches.match(e.request).then(r => r || caches.match('./index.html')))
  );
});
