/* Estado persistente en el teléfono: qué has visto, qué respondiste, tu racha.
   Todo vive en localStorage — no hay servidor y no sale nada del dispositivo. */

/* v2: hasta la v1 el progreso del día se incrementaba al pintar la tarjeta,
   no al trabajarla, así que los contadores guardados vienen inflados. Cambiar
   la clave hace que el conteo arranque limpio en vez de heredar el error. */
const CLAVE = 'andes.v2';

const INICIAL = {
  vistas: {},        // id -> timestamp de la última vez que salió
  respuestas: [],    // {id, area, nivel, patron, marcada, correcta, ok, segundos, causa, confianza, ts}
  dias: {},          // 'AAAA-MM-DD' -> {n, aciertos}
  repaso: {},        // id -> {seguidos, proximo, fallos}
  meta_diaria: 30,
  tanda_actual: 0,
};

/* Escalera de repaso espaciado, en días. Una tarjeta fallada vuelve mañana; con
   cada acierto sube un peldaño. Los dos primeros saltos son los del plan de
   estudio —repasar a los 3 y a los 14 días—; el resto los espacia para que el
   feed no se llene de cosas ya sabidas. */
const ESCALERA = [1, 3, 7, 14, 30];
const DIA = 86400000;

function leer() {
  try {
    const crudo = localStorage.getItem(CLAVE);
    return crudo ? { ...INICIAL, ...JSON.parse(crudo) } : { ...INICIAL };
  } catch {
    return { ...INICIAL };
  }
}

let estado = leer();

function guardar() {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(estado));
  } catch { /* cuota llena: se sigue en memoria */ }
}

export const hoyISO = () => new Date().toLocaleDateString('sv-SE');

export function obtener() { return estado; }

export function metaDiaria() { return estado.meta_diaria; }

export function fijarMeta(n) {
  estado.meta_diaria = Math.max(5, Math.min(200, n));
  guardar();
}

/* ── Sesión del día ───────────────────────────────────────────
   El orden en que fueron saliendo las tarjetas de hoy. Es lo que permite
   volver a entrar a media tarde y seguir donde ibas en vez de empezar de
   cero, y lo que le da a cada tarjeta su número dentro del día. */

function sesionDeHoy() {
  if (!estado.sesion || estado.sesion.fecha !== hoyISO()) {
    estado.sesion = { fecha: hoyISO(), orden: [] };
  }
  return estado.sesion;
}

export function sesion() { return sesionDeHoy(); }

/** Cuántas tarjetas llevas hoy; el ordinal de la siguiente es este más uno. */
export function posicionHoy() { return sesionDeHoy().orden.length; }

export function ordinalDe(id) {
  const i = sesionDeHoy().orden.findIndex(x => x.id === id);
  return i < 0 ? null : i + 1;
}

export function historialHoy() { return sesionDeHoy().orden.slice(); }

/** Deja constancia de que la tarjeta ya salió, para no repetirla.
 *  No suma al progreso del día: salir en pantalla no es haberla hecho. */
export function vista(id) {
  estado.vistas[id] = Date.now();
  guardar();
}

/** Suma la tarjeta al progreso del día y le asigna su número.
 *
 *  Se llama cuando de verdad la trabajaste: al responder una pregunta, o al
 *  haber tenido en pantalla una tarjeta de lectura. Antes esto ocurría al
 *  pintarla, y como el feed pinta de a seis, el contador arrancaba en 6/30 sin
 *  que hubieras tocado nada.
 *
 *  Es idempotente: al repintar el historial del día no vuelve a contar.
 */
export function contar(id, meta = {}) {
  const s = sesionDeHoy();
  const ya = s.orden.findIndex(x => x.id === id);
  if (ya >= 0) return ya + 1;

  s.orden.push({ id, codigo: meta.codigo || '', tipo: meta.tipo || '', ok: null });
  const d = estado.dias[hoyISO()] || { n: 0, aciertos: 0 };
  d.n += 1;
  estado.dias[hoyISO()] = d;
  guardar();
  return s.orden.length;
}

export function fueVista(id) { return id in estado.vistas; }

export function registrarRespuesta(r) {
  estado.respuestas.push({ ...r, ts: Date.now() });
  actualizarRepaso(r.id, r.ok);
  if (r.ok) {
    const d = estado.dias[hoyISO()] || { n: 0, aciertos: 0 };
    d.aciertos += 1;
    estado.dias[hoyISO()] = d;
  }
  // La respuesta queda anotada también en la sesión, para poder repintar el
  // historial del día con los aciertos y fallos ya marcados.
  const entrada = sesionDeHoy().orden.find(x => x.id === r.id);
  if (entrada) entrada.ok = !!r.ok;
  guardar();
}

/** Anota por qué falló, después de haber respondido.
 *  Va aparte porque la causa se pregunta cuando ya se reveló el resultado. */
export function anotarCausa(id, causa) {
  for (let i = estado.respuestas.length - 1; i >= 0; i--) {
    if (estado.respuestas[i].id === id) {
      estado.respuestas[i].causa = causa;
      guardar();
      return true;
    }
  }
  return false;
}

/** La última respuesta dada a una tarjeta, si ya la respondiste. */
export function respuestaPrevia(id) {
  for (let i = estado.respuestas.length - 1; i >= 0; i--) {
    if (estado.respuestas[i].id === id) return estado.respuestas[i];
  }
  return null;
}

export function progresoHoy() {
  return estado.dias[hoyISO()] || { n: 0, aciertos: 0 };
}

/** Días seguidos con al menos una tarjeta, contando hacia atrás desde hoy.
 *  Si hoy todavía no has abierto la app, la racha de ayer sigue viva. */
export function racha() {
  let n = 0;
  const cursor = new Date();
  if (!estado.dias[hoyISO()]) cursor.setDate(cursor.getDate() - 1);
  for (;;) {
    const clave = cursor.toLocaleDateString('sv-SE');
    if (!estado.dias[clave] || estado.dias[clave].n === 0) break;
    n += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return n;
}

/** Acierto por área sobre todo lo respondido. */
export function aciertoPorArea() {
  const acc = {};
  for (const r of estado.respuestas) {
    if (!r.area) continue;
    acc[r.area] = acc[r.area] || { n: 0, ok: 0 };
    acc[r.area].n += 1;
    if (r.ok) acc[r.area].ok += 1;
  }
  return acc;
}

/** Tiempo medio por pregunta respondida, en segundos. */
export function tiempoMedio(soloHoy = false) {
  const desde = soloHoy ? new Date(hoyISO() + 'T00:00:00').getTime() : 0;
  const t = estado.respuestas.filter(r => r.segundos > 0 && r.ts >= desde);
  if (!t.length) return null;
  return Math.round(t.reduce((s, r) => s + r.segundos, 0) / t.length);
}

/** Por qué fallas, que es la pregunta que más rinde del diagnóstico. */
export function porCausa() {
  const acc = {};
  for (const r of estado.respuestas) {
    if (r.ok || !r.causa) continue;
    acc[r.causa] = (acc[r.causa] || 0) + 1;
  }
  return acc;
}

/** Calibración: qué tan bien sabes lo que sabes.
 *  El caso peligroso es confianza alta con acierto bajo. */
export function calibracion() {
  const acc = {};
  for (const r of estado.respuestas) {
    if (!r.confianza) continue;
    acc[r.confianza] = acc[r.confianza] || { n: 0, ok: 0 };
    acc[r.confianza].n += 1;
    if (r.ok) acc[r.confianza].ok += 1;
  }
  return acc;
}

export function totales() {
  const n = estado.respuestas.length;
  const ok = estado.respuestas.filter(r => r.ok).length;
  return { n, ok, pct: n ? Math.round(100 * ok / n) : 0 };
}

/* ── Repaso espaciado ────────────────────────────────────────
   Una tarjeta que fallaste no se pierde en el corpus: entra en una cola y
   vuelve a aparecer con espaciado creciente hasta que la domines. Es la regla
   de práctica deliberada del plan de estudio, aplicada por la app en vez de a
   mano. */

function actualizarRepaso(id, ok) {
  if (!id) return;
  const ficha = estado.repaso[id] || { seguidos: 0, fallos: 0, proximo: 0 };

  if (ok) {
    ficha.seguidos += 1;
    // Dos aciertos seguidos y la tarjeta sale de la cola: ya está.
    if (ficha.seguidos >= 2 && ficha.fallos > 0) {
      delete estado.repaso[id];
      return;
    }
  } else {
    ficha.fallos += 1;
    ficha.seguidos = 0;
  }

  const peldano = Math.min(ficha.seguidos, ESCALERA.length - 1);
  ficha.proximo = Date.now() + ESCALERA[peldano] * DIA;
  estado.repaso[id] = ficha;
}

/** Las que ya toca repasar hoy, de la más atrasada a la más reciente. */
export function pendientesDeRepaso() {
  const ahora = Date.now();
  return Object.entries(estado.repaso)
    .filter(([, f]) => f.fallos > 0 && f.proximo <= ahora)
    .map(([id, f]) => ({
      id,
      fallos: f.fallos,
      dias: Math.max(0, Math.floor((ahora - f.proximo) / DIA)),
      // Una tarjeta fallada dos veces o más es hueso: cuesta y hay que insistir.
      hueso: f.fallos >= 2,
    }))
    .sort((a, b) => b.dias - a.dias);
}

/** Cuántas hay en la cola aunque todavía no toquen. */
export function enCola() {
  return Object.values(estado.repaso).filter(f => f.fallos > 0).length;
}

/** CSV con las mismas columnas que espera 06_SEGUIMIENTO/medidor.py, para que
 *  lo que haces en el teléfono alimente el tablero que ya existe. */
export function exportarCSV() {
  const cab = 'fecha,id,area,nivel,patron,marcada,correcta,ok,segundos,causa,confianza\n';
  const filas = estado.respuestas.map(r => [
    new Date(r.ts).toISOString().slice(0, 10),
    r.id, r.area || '', r.nivel || '', r.patron || '',
    r.marcada || '', r.correcta || '', r.ok ? 1 : 0,
    r.segundos || '', r.causa || '', r.confianza || '',
  ].join(','));
  return cab + filas.join('\n');
}

/* ── Traspaso entre dispositivos ──────────────────────────────
   El progreso vive en el navegador, así que el celular y el computador no lo
   comparten. Estas dos funciones lo mueven de uno a otro como un texto que se
   copia y se pega, sin necesidad de servidor ni de cuenta. */

export function exportarEstado() {
  const util = {
    v: 2,
    vistas: estado.vistas,
    respuestas: estado.respuestas,
    dias: estado.dias,
    repaso: estado.repaso,
    sesion: estado.sesion,
    meta_diaria: estado.meta_diaria,
  };
  // btoa no admite caracteres fuera de latin-1; los ids y códigos son ASCII,
  // pero se codifica a UTF-8 primero por si acaso.
  const bytes = new TextEncoder().encode(JSON.stringify(util));
  let binario = '';
  for (const b of bytes) binario += String.fromCharCode(b);
  return 'ANDES1:' + btoa(binario);
}

export function importarEstado(texto) {
  const limpio = String(texto || '').trim().replace(/\s+/g, '');
  if (!limpio.startsWith('ANDES1:')) return { ok: false, motivo: 'no parece un código de ANDES' };

  try {
    const binario = atob(limpio.slice(7));
    const bytes = Uint8Array.from(binario, c => c.charCodeAt(0));
    const datos = JSON.parse(new TextDecoder().decode(bytes));
    if (!datos || typeof datos !== 'object' || !datos.respuestas) {
      return { ok: false, motivo: 'el código está incompleto' };
    }

    // Se fusiona en vez de reemplazar: si respondiste cosas distintas en cada
    // dispositivo, se conservan las dos.
    const porClave = new Map();
    for (const r of [...estado.respuestas, ...datos.respuestas]) {
      porClave.set(`${r.id}|${r.ts}`, r);
    }
    estado.respuestas = [...porClave.values()].sort((a, b) => a.ts - b.ts);
    estado.vistas = { ...estado.vistas, ...datos.vistas };
    estado.repaso = { ...estado.repaso, ...(datos.repaso || {}) };

    for (const [dia, v] of Object.entries(datos.dias || {})) {
      const mio = estado.dias[dia];
      // Se queda el día con más avance, no la suma: sumarlos contaría doble lo
      // que se hizo en los dos aparatos.
      if (!mio || v.n > mio.n) estado.dias[dia] = v;
    }

    if (datos.sesion?.fecha === hoyISO()) {
      const mia = sesionDeHoy();
      if ((datos.sesion.orden || []).length > mia.orden.length) {
        estado.sesion = datos.sesion;
      }
    }
    if (datos.meta_diaria) estado.meta_diaria = datos.meta_diaria;

    guardar();
    return { ok: true, respuestas: estado.respuestas.length };
  } catch {
    return { ok: false, motivo: 'no pude leer el código' };
  }
}

export function reiniciar() {
  estado = { ...INICIAL };
  guardar();
}
