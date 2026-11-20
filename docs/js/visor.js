/* Visor de simulaciones: las abre encima de lo que estés haciendo, en un
   iframe, para que al cerrar el feed siga exactamente donde estaba (sin
   recargar, sin perder el scroll ni la tarjeta a medio responder).

   También decide qué simulación ofrecer en cada tarjeta del feed. */

const SIMS = {
  dilatacion:  { url: 'extra/relatividad.html#dilatacion',  titulo: 'Dilatación del tiempo' },
  contraccion: { url: 'extra/relatividad.html#contraccion', titulo: 'Contracción de longitudes' },
  doppler:     { url: 'extra/relatividad.html#doppler',     titulo: 'Doppler relativista' },
  nave:        { url: 'extra/relatividad.html#nave',        titulo: 'La nave y el laboratorio' },
  escalon:     { url: 'extra/cuantica.html#escalon',        titulo: 'Escalón de potencial' },
  caja:        { url: 'extra/cuantica.html#caja',           titulo: 'Caja 2D: bosones y fermiones' },
  oscilador:   { url: 'extra/cuantica.html#oscilador',      titulo: 'Oscilador cuántico' },
  gauss:       { url: 'extra/gauss_ampere.html#gauss,esfera',   titulo: 'Gauss: E(r) por regiones' },
  ampere:      { url: 'extra/gauss_ampere.html#ampere,alambre', titulo: 'Ampère: B(r) por regiones' },
  fase:        { url: 'extra/mecanica.html#fase',           titulo: 'Espacio de fase' },
  dispersion:  { url: 'extra/mecanica.html#esfera',         titulo: 'Esfera dura' },
  monedas:     { url: 'extra/estadistica.html#monedas',     titulo: 'Monedas y entropía' },
  contacto:    { url: 'extra/estadistica.html#contacto',    titulo: 'Contacto térmico' },
  rc:          { url: 'extra/circuitos.html#rc',            titulo: 'Circuito RC' },
  rl:          { url: 'extra/circuitos.html#rl',            titulo: 'Circuito RL' },
  rlc:         { url: 'extra/circuitos.html#rlc',           titulo: 'Circuito LC / RLC' },
  amortiguado: { url: 'extra/oscilaciones.html#amortiguado', titulo: 'Oscilador amortiguado' },
  forzado:     { url: 'extra/oscilaciones.html#forzado',    titulo: 'Oscilador forzado y resonancia' },
  rodadura:    { url: 'extra/rodadura.html',                titulo: 'Rodadura y momentos de inercia' },
  estacionarias:{ url: 'extra/ondas_optica.html#estacionarias', titulo: 'Ondas estacionarias' },
  rendijas:    { url: 'extra/ondas_optica.html#rendijas',   titulo: 'Doble rendija' },
  lentes:      { url: 'extra/ondas_optica.html#lentes',     titulo: 'Lentes delgadas' },
  procesos:    { url: 'extra/termo_ciclos.html#procesos',   titulo: 'Los cuatro procesos' },
  carnot:      { url: 'extra/termo_ciclos.html#carnot',     titulo: 'Ciclo de Carnot' },
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
  gauss: /gauss|spherical shell|cascar[oó]n|uniformly charged (?:sphere|ball|cylinder)|esfera (?:maciza|s[oó]lida|cargada|hueca)|charged (?:sphere|cylinder|shell)|coaxial|cilindro/,
  ampere: /amp[eè]re|amperian|amperiana|solenoid|toroid|hollow (?:conductor|cylinder)|conductor hueco|cilindro hueco|cil[ií]ndric[oa][^.]*hueco|long straight wire|alambre (?:recto|largo)|coaxial/,
  fase: /phase space|phase-space|espacio de fase|liouville|action variable|variable de acci[oó]n|hamilton/,
  dispersion: /hard sphere|esfera dura|impact parameter|par[aá]metro de impacto|scattering angle|[aá]ngulo de dispersi[oó]n|cross section|secci[oó]n eficaz/,
  entropia: /multiplicit|microstate|microestado|macrostate|macroestado|\bcoins?\b|monedas?|einstein solid|s[oó]lido de einstein|k\s*ln|entrop[^.]*(?:\bln\b|ω|Ω|omega)|statistical weight|peso estad[ií]stico/,
  contacto: /thermal contact|contacto t[eé]rmico|einstein solid|s[oó]lido de einstein|two (?:systems|solids)|dos (?:sistemas|s[oó]lidos)/,
  rc: /\brc\b|capacitor[^.]*(?:resistor|resistance)|(?:resistor|resistance)[^.]*capacitor|condensador[^.]*resist|resist[^.]*condensador|time constant|constante de tiempo|discharg|descarg/,
  rl: /\brl\b|inductor[^.]*(?:resistor|resistance)|(?:resistor|resistance)[^.]*inductor|bobina[^.]*resist|inductance[^.]*resist/,
  rlc: /\brlc\b|\blc\b|lc circuit|circuito lc|resonan|resonancia|inductor[^.]*capacitor|capacitor[^.]*inductor/,
  amort: /damp|amortigu|critically|cr[ií]tico|quality factor|factor de calidad|decay of (?:the )?amplitude/,
  forz: /driven|forced|forzad|resonan|driving (?:force|frequency)/,
  rodadura: /\broll|rueda|rodando|without slipping|sin deslizar|moment of inertia|momento de inercia|rotational inertia|inercia rotacional/,
  estac: /standing wave|onda estacionaria|harmonic|arm[oó]nico|\bpipe|\btubo|organ|fundamental frequency|frecuencia fundamental|string (?:fixed|of length)|cuerda/,
  rendijas: /\bslits?\b|rendija|interference|interferencia|diffraction|difracci|grating|fringe|franja/,
  lentes: /\blens|\blente|focal|converging|diverging|convergente|divergente|mirror|espejo/,
  ciclo: /carnot|efficien|eficiencia|heat engine|m[aá]quina t[eé]rmica|refrigerat|\bcycle|\bciclo/,
  proc: /isobar|isochor|isoc[oó]ric|isob[aá]ric|first law|primera ley|adiabat|isotherm|isot[eé]rm|work done by the gas|trabajo (?:hecho|realizado) por el gas/,
  nave: /spaceship|space ship|\bnave\b|rocket|cohete|light-?years?|a[ñn]os luz|twin|gemel|\bstar\b|estrella|astronaut/,
  escalon: /\bstep\b|escal[oó]n|barrier|barrera|tunnel|t[uú]nel|reflection coef|transmission coef|coeficiente de (?:reflexi|transmisi)/,
  caja: /\bbox\b|caja|square well|infinite well|pozo|boson|fermion|pauli|indistinguish|indistinguib/,
  oscilador: /harmonic oscillator|oscilador|arm[oó]nico|zero-point|punto cero|ladder operator|operador(?:es)? escalera|creation operator/,
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
    if (RE.nave.test(txt)) out.unshift('nave');
    if (!out.length && t.area === 'relatividad') out.push('dilatacion', 'contraccion');
  } else if (etiquetas.includes('doppler') && !/sound|sonido/.test(txt) && /\blight\b|\bluz\b|relativis|\bstars?\b|galax|estrella|photon|fot[oó]n/.test(txt)) {
    out.push('doppler');
  }
  if (t.area === 'electromagnetismo') {
    if (RE.gauss.test(txt)) out.push('gauss');
    if (RE.ampere.test(txt)) out.push('ampere');
    if (RE.rlc.test(txt)) out.push('rlc');
    else if (RE.rc.test(txt)) out.push('rc');
    if (RE.rl.test(txt) && !out.includes('rlc')) out.push('rl');
    if (RE.imagenes.test(txt)) out.push('imagenes');
    if (RE.borde.test(txt)) out.push('borde');
  }
  if (t.area === 'termo_estadistica') {
    if (RE.ciclo.test(txt)) out.push('carnot');
    if (RE.proc.test(txt)) out.push('procesos');
    if (RE.adiabatica.test(txt)) out.push('adiabatica');
    if (RE.contacto.test(txt)) out.push('contacto');
    else if (RE.entropia.test(txt)) out.push('monedas');
  }
  if (t.area === 'mecanica') {
    if (RE.forz.test(txt)) out.push('forzado');
    else if (RE.amort.test(txt)) out.push('amortiguado');
    if (RE.rodadura.test(txt)) out.push('rodadura');
    if (RE.fase.test(txt)) out.push('fase');
    if (RE.dispersion.test(txt)) out.push('dispersion');
  }
  if (t.area === 'optica_ondas') {
    if (RE.estac.test(txt)) out.push('estacionarias');
    if (RE.rendijas.test(txt)) out.push('rendijas');
    if (RE.lentes.test(txt)) out.push('lentes');
  }
  if (t.area === 'moderna_cuantica') {
    if (RE.escalon.test(txt)) out.push('escalon');
    if (RE.caja.test(txt)) out.push('caja');
    if (RE.oscilador.test(txt)) out.push('oscilador');
  }
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
