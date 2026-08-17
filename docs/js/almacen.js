/* Estado persistente en el teléfono: qué has visto, qué respondiste, tu racha.
   Todo vive en localStorage — no hay servidor y no sale nada del dispositivo. */

const CLAVE = 'andes.v1';

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

export function vista(id) {
  estado.vistas[id] = Date.now();
  const d = estado.dias[hoyISO()] || { n: 0, aciertos: 0 };
  d.n += 1;
  estado.dias[hoyISO()] = d;
  guardar();
}

export function fueVista(id) { return id in estado.vistas; }

export function registrarRespuesta(r) {
  estado.respuestas.push({ ...r, ts: Date.now() });
  if (r.ok) {
    const d = estado.dias[hoyISO()] || { n: 0, aciertos: 0 };
    d.aciertos += 1;
    estado.dias[hoyISO()] = d;
  }
  guardar();
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

export function reiniciar() {
  estado = { ...INICIAL };
  guardar();
}
