/* Carga del contenido: cronograma completo y tandas bajo demanda.

   El corpus entero son ~1,2 MB. No se descarga de golpe: la app pide el manifiesto
   y la primera tanda (~105 kB) y va trayendo las siguientes conforme avanzas. */

import * as cripto from './cripto.js';

const BASE = 'contenido/';

let manifiesto = null;
let cronograma = null;
const tandasCargadas = new Map();

async function traer(archivo) {
  const resp = await fetch(BASE + archivo, { cache: 'no-cache' });
  if (!resp.ok) throw new Error(`No pude cargar ${archivo} (${resp.status})`);
  return resp.json();
}

async function traerCifrado(archivo, clave) {
  const resp = await fetch(BASE + archivo, { cache: 'no-cache' });
  if (!resp.ok) throw new Error(`No pude cargar ${archivo} (${resp.status})`);
  const blob = await resp.arrayBuffer();
  return JSON.parse(await cripto.descifrar(clave, blob));
}

export async function cargarManifiesto() {
  if (!manifiesto) manifiesto = await traer('manifiesto.json');
  return manifiesto;
}

export async function cargarCronograma() {
  if (!cronograma) cronograma = await traer('cronograma.json');
  return cronograma;
}

export async function cargarTanda(indice) {
  if (tandasCargadas.has(indice)) return tandasCargadas.get(indice);
  const m = await cargarManifiesto();
  const meta = m.tandas[indice];
  if (!meta) return [];

  let tarjetas;
  if (m.cifrado) {
    const clave = await cripto.recuperar(m.cifrado);
    if (!clave) throw new Error('sin-clave');
    tarjetas = await traerCifrado(meta.archivo, clave);
  } else {
    tarjetas = await traer(meta.archivo);
  }

  tandasCargadas.set(indice, tarjetas);
  return tarjetas;
}

/** ¿El contenido viene cifrado y todavía no hay clave válida en el teléfono? */
export async function necesitaClave() {
  const m = await cargarManifiesto();
  if (!m.cifrado) return false;
  return !(await cripto.recuperar(m.cifrado));
}

export async function desbloquear(frase) {
  const m = await cargarManifiesto();
  const clave = await cripto.probarFrase(frase, m.cifrado);
  if (!clave) return false;
  await cripto.recordar(clave);
  return true;
}

export function datosCifrado() { return manifiesto?.cifrado || null; }

export function numeroDeTandas() {
  return manifiesto ? manifiesto.tandas.length : 0;
}

/* ── Utilidades de calendario ─────────────────────────────── */

export const hoyISO = () => new Date().toLocaleDateString('sv-SE');

export function diasHasta(iso) {
  const objetivo = new Date(iso + 'T00:00:00');
  const hoy = new Date(hoyISO() + 'T00:00:00');
  return Math.round((objetivo - hoy) / 86400000);
}

/** La semana que contiene la fecha; si ninguna la contiene, la siguiente que venga. */
export function semanaDe(crono, iso = hoyISO()) {
  const dentro = crono.semanas.find(s => iso >= s.inicio && iso <= s.fin);
  if (dentro) return dentro;
  return crono.semanas.find(s => s.inicio > iso) || crono.semanas.at(-1);
}

export function diaDe(semana, iso = hoyISO()) {
  return semana.dias?.find(d => d.fecha === iso) || null;
}

const NOMBRES_DIA = {
  lunes: 'lunes', martes: 'martes', miercoles: 'miércoles', jueves: 'jueves',
  viernes: 'viernes', sabado: 'sábado', domingo: 'domingo',
};

export const nombreDia = d => NOMBRES_DIA[d] || d;

const NOMBRES_AREA = {
  mecanica: 'Mecánica',
  electromagnetismo: 'Electromagnetismo',
  termo_estadistica: 'Termo y estadística',
  moderna_cuantica: 'Moderna y cuántica',
  relatividad: 'Relatividad',
  optica_ondas: 'Óptica y ondas',
  transversal: 'Transversal',
};

export const nombreArea = a => NOMBRES_AREA[a] || a || '—';

const NOMBRES_BLOQUE = {
  teoria: 'Teoría', problemas: 'Problemas', mc: 'Opción múltiple',
  repaso: 'Repaso activo', descanso: 'Descanso',
};

export const nombreBloque = b => NOMBRES_BLOQUE[b] || b;

export function fechaLarga(iso) {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('es-CO', {
    weekday: 'long', day: 'numeric', month: 'long',
  });
}

export function rangoCorto(inicio, fin) {
  const opciones = { day: 'numeric', month: 'short' };
  const a = new Date(inicio + 'T00:00:00').toLocaleDateString('es-CO', opciones);
  const b = new Date(fin + 'T00:00:00').toLocaleDateString('es-CO', opciones);
  return `${a} – ${b}`;
}
