/* Visor de simulaciones: las abre encima de lo que estés haciendo, en un
   iframe, para que al cerrar el feed siga exactamente donde estaba (sin
   recargar, sin perder el scroll ni la tarjeta a medio responder).

   También decide qué simulación ofrecer en cada tarjeta del feed. */

const SIMS = {
  dilatacion:  { url: 'extra/relatividad.html#dilatacion',  titulo: 'Dilatación del tiempo' },
  contraccion: { url: 'extra/relatividad.html#contraccion', titulo: 'Contracción de longitudes' },
  doppler:     { url: 'extra/relatividad.html#doppler',     titulo: 'Doppler relativista' },
  imagenes:    { url: 'extra/metodo_de_imagenes.html',      titulo: 'Método de las imágenes' },
  borde:       { url: 'extra/efectos_de_borde_linea_plano.html', titulo: 'Efectos de borde' },
  adiabatica:  { url: 'extra/p15_isoterma_adiabatica.html', titulo: 'Isoterma contra adiabática' },
};

const RE = {
  doppler: /doppler|wavelength|frequenc|longitud de onda|frecuencia|red ?shift|blue ?shift|corrimiento/,
  contraccion: /contract|(?<!wave)length|longitud(?! de onda)|meter stick|metre stick|\brods?\b|varilla|regla|volume|volumen|spaceship.*long/,
  dilatacion: /clock|dilat|lifetime|reloj|vida media|mu[oó]n|pion|half-life|time interval|intervalo de tiempo|proper time|tiempo propio|twin|gemel|\bages?\b|envejec/,
  imagenes: /image charge|method of images|m[eé]todo de (?:las )?im[aá]genes|carga imagen|grounded|a tierra|conducting plane|plano conductor|conductor plano/,
  borde: /infinite (?:line|sheet|plane|wire|rod|plate)|infinit[oa]s? (?:l[ií]nea|l[aá]mina|plano|hilo|alambre|placa)|finite (?:line|rod|sheet|wire)|edge effect|efectos? de borde|parallel[- ]plate|placas paralelas/,
  adiabatica: /adiabat|isotherm|isot[eé]rm/,
};

/** Qué simulaciones tienen que ver con esta tarjeta (claves de SIMS). */
export function simulacionesPara(t) {
  const etiquetas = t.etiquetas || [];
  // Las etiquetas no entran al texto: «dilatacion» etiqueta todo el capítulo de
  // relatividad, y haría que cualquier pregunta de Doppler pidiera el reloj.
  const txt = [t.enunciado, t.tema, t.titulo, t.texto, t.idea, ...Object.values(t.opciones || {})]
    .filter(Boolean).join(' ').toLowerCase();
  const out = [];
  const relativista = t.area === 'relatividad' || etiquetas.includes('dilatacion');

  if (relativista) {
    if (RE.dilatacion.test(txt)) out.push('dilatacion');
    if (RE.contraccion.test(txt)) out.push('contraccion');
    if (RE.doppler.test(txt)) out.push('doppler');
    if (!out.length && t.area === 'relatividad') out.push('dilatacion', 'contraccion');
  } else if (etiquetas.includes('doppler') && !/sound|sonido/.test(txt) && /\blight\b|\bluz\b|relativis|\bstars?\b|galax|estrella|photon|fot[oó]n/.test(txt)) {
    out.push('doppler');
  }
  if (t.area === 'electromagnetismo') {
    if (RE.imagenes.test(txt)) out.push('imagenes');
    if (RE.borde.test(txt)) out.push('borde');
  }
  if (t.area === 'termo_estadistica' && RE.adiabatica.test(txt)) out.push('adiabatica');
  return [...new Set(out)].slice(0, 3);
}

const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/** Los botones «Verlo» de una tarjeta, o '' si no hay simulación que venga al caso. */
export function htmlAccesos(t) {
  const claves = simulacionesPara(t);
  if (!claves.length) return '';
  return `
    <div class="accesos-sim">
      <span class="rotulo">Verlo</span>
      ${claves.map(k => `<button type="button" class="chip-sim"
          data-sim="${esc(SIMS[k].url)}" data-titulo="${esc(SIMS[k].titulo)}">▶ ${esc(SIMS[k].titulo)}</button>`).join('')}
    </div>`;
}

/* ── El visor ─────────────────────────────────────────────── */

let capa = null;

export function abrirVisor(url, titulo = '') {
  if (capa) cerrar();
  capa = document.createElement('div');
  capa.className = 'visor';
  capa.innerHTML = `
    <div class="visor-barra">
      <button type="button" class="visor-cerrar">✕ Volver</button>
      <span class="visor-titulo">${esc(titulo)}</span>
    </div>
    <iframe class="visor-marco" src="${esc(url)}" allow="fullscreen" title="${esc(titulo)}"></iframe>`;
  document.body.append(capa);
  document.body.classList.add('con-visor');
  capa.querySelector('.visor-cerrar').addEventListener('click', volver);
  // Una entrada en el historial para que el botón «atrás» del teléfono cierre
  // el visor en vez de salir de la app. No cambia el hash: el feed no se entera.
  history.pushState({ visor: true }, '');
}

function volver() {
  if (history.state?.visor) history.back();   // dispara popstate → cerrar()
  else cerrar();
}

function cerrar() {
  capa?.remove();
  capa = null;
  document.body.classList.remove('con-visor');
}

if (typeof window !== 'undefined') {
  window.addEventListener('popstate', () => { if (capa) cerrar(); });
  window.addEventListener('message', e => { if (e.data === 'andes-cerrar-visor' && capa) volver(); });
  document.addEventListener('click', e => {
    const b = e.target.closest?.('[data-sim]');
    if (!b) return;
    e.preventDefault();
    abrirVisor(b.dataset.sim, b.dataset.titulo);
  });
}
