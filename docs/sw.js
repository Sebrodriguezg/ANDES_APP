/* Service worker: deja la app utilizable sin datos.
   El cascarón se guarda al instalar; el contenido, conforme lo pides. */

/* La versión se sube a mano en cada publicación de contenido. Sin eso, un
   teléfono con la app instalada sigue sirviendo del caché la versión anterior:
   Sebastián vio preguntas con el signo × desplazado horas después de haberlo
   arreglado, porque su copia era la de antes. */
const CACHE = 'andes-v17';
const CASCARON = [
  './', './index.html', './css/estilo.css', './icono.svg',
  './js/app.js', './js/feed.js', './js/datos.js',
  './js/almacen.js', './js/tarjetas.js', './js/mate.js', './js/cripto.js',
  // Estos tres faltaban: solo se guardaban al usarlos por primera vez, así que
  // quien instalaba la app y se quedaba sin datos no podía abrir el simulacro
  // ni ver una fórmula compuesta.
  './js/hoja.js', './js/formula.js', './js/simulacro.js',
  './contenido/cronograma.json', './contenido/manifiesto.json',
  './contenido/examen.json',
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
