/* Estado persistente en el teléfono: qué has visto, qué respondiste, tu racha.
   Todo vive en localStorage — no hay servidor y no sale nada del dispositivo. */

/* v2: hasta la v1 el progreso del día se incrementaba al pintar la tarjeta,
   no al trabajarla, así que los contadores guardados vienen inflados. Cambiar
   la clave hace que el conteo arranque limpio en vez de heredar el error. */
const CLAVE = 'andes.v2';

const INICIAL = {
  vistas: {},        // id de tarjeta -> timestamp de la última vez
  respuestas: [],    // {id, area, nivel, patron, marcada, correcta, ok, ts}
  dias: {},          // 'AAAA-MM-DD' -> {n, aciertos}
  meta_diaria: 30,
  tanda_actual: 0,
};

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

export function totales() {
  const n = estado.respuestas.length;
  const ok = estado.respuestas.filter(r => r.ok).length;
  return { n, ok, pct: n ? Math.round(100 * ok / n) : 0 };
}

/** Tarjetas falladas que toca repasar: a los 3 días y a los 14.
 *  Es la misma regla de práctica deliberada que ya usa el medidor. */
export function pendientesDeRepaso() {
  const dia = 86400000;
  const ahora = Date.now();
  const ultima = new Map();
  for (const r of estado.respuestas) ultima.set(r.id, r);

  const salida = [];
  for (const r of ultima.values()) {
    if (r.ok) continue;
    const edad = (ahora - r.ts) / dia;
    if (edad >= 3) salida.push({ id: r.id, dias: Math.floor(edad) });
  }
  return salida;
}

export function exportarCSV() {
  const cab = 'fecha,id,area,nivel,patron,marcada,correcta,ok\n';
  const filas = estado.respuestas.map(r => [
    new Date(r.ts).toISOString().slice(0, 10),
    r.id, r.area || '', r.nivel || '', r.patron || '',
    r.marcada || '', r.correcta || '', r.ok ? 1 : 0,
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
