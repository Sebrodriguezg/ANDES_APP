/* Modo simulacro: el examen real, no el feed.
 *
 * 25 preguntas y 3 horas, sin decir nada hasta el final. Es lo que piden las
 * semanas 12 y 13 del cronograma, y sin esto la app se queda corta justo en las
 * dos que deciden.
 *
 * La diferencia con el feed no es cosmética. En el feed sabes al instante si
 * acertaste, que es lo que hace que enganche; aquí no se sabe nada hasta el
 * final, porque lo que se entrena es aguantar tres horas sin esa señal y
 * repartir el tiempo entre veinticinco preguntas. */

import * as datos from './datos.js';
import * as almacen from './almacen.js';
import { mate, escapar } from './mate.js';

/* Reparto del examen real, contado sobre el simulacro oficial de 2024.
   Suma 25. */
export const REPARTO = {
  mecanica: 8,
  electromagnetismo: 6,
  termo_estadistica: 5,
  moderna_cuantica: 4,
  relatividad: 2,
};

export const MINUTOS = 180;
const LETRAS = ['A', 'B', 'C', 'D', 'E'];

let examen = null;

/** Arma las 25 preguntas respetando el reparto por áreas.
 *
 *  Prefiere las que vienen del examen real de Uniandes y del GRE, que son las
 *  que se parecen a lo que va a caer; el banco de HRW rellena lo que falte. */
export async function armar() {
  await datos.cargarManifiesto();

  const porArea = {};
  for (let i = 0; i < datos.numeroDeTandas(); i++) {
    let tanda;
    try { tanda = await datos.cargarTanda(i); } catch { break; }
    for (const t of tanda) {
      if (t.tipo !== 'mc' || !t.respuesta) continue;
      (porArea[t.area] ??= []).push(t);
    }
  }

  const prioridad = t => (
    t.origen === 'Uniandes2024' ? 0 : t.origen === 'ETS-GR1775' ? 1 : 2
  );

  const elegidas = [];
  for (const [area, cuantas] of Object.entries(REPARTO)) {
    const bolsa = (porArea[area] || []).slice();
    // Se baraja y luego se ordena por procedencia: dentro de cada origen el
    // orden es aleatorio, pero el examen real va primero.
    bolsa.sort(() => Math.random() - 0.5);
    bolsa.sort((a, b) => prioridad(a) - prioridad(b));
    elegidas.push(...bolsa.slice(0, cuantas));
  }

  elegidas.sort(() => Math.random() - 0.5);
  examen = {
    preguntas: elegidas,
    marcadas: new Array(elegidas.length).fill(null),
    dudosas: new Set(),
    inicio: Date.now(),
    fin: null,
  };
  return examen;
}

export function estado() { return examen; }

export function marcar(indice, letra) {
  if (!examen) return;
  examen.marcadas[indice] = letra;
}

export function alternarDuda(indice) {
  if (!examen) return false;
  if (examen.dudosas.has(indice)) { examen.dudosas.delete(indice); return false; }
  examen.dudosas.add(indice);
  return true;
}

export function segundosRestantes() {
  if (!examen) return 0;
  const usados = (Date.now() - examen.inicio) / 1000;
  return Math.max(0, MINUTOS * 60 - usados);
}

/** Corrige, registra cada respuesta y devuelve el desglose. */
export function corregir() {
  if (!examen) return null;
  examen.fin = Date.now();

  const minutos = Math.round((examen.fin - examen.inicio) / 60000);
  const porArea = {};
  let aciertos = 0;

  examen.preguntas.forEach((t, i) => {
    const marcada = examen.marcadas[i];
    const ok = marcada === t.respuesta;
    if (ok) aciertos += 1;

    porArea[t.area] ??= { n: 0, ok: 0 };
    porArea[t.area].n += 1;
    if (ok) porArea[t.area].ok += 1;

    // Entra en el mismo registro que el feed: cuenta para el acierto por área
    // y alimenta la cola de repaso con lo que falló.
    almacen.registrarRespuesta({
      id: t.id, area: t.area, nivel: t.nivel, patron: t.patron || '',
      marcada: marcada || '', correcta: t.respuesta, ok,
      origen: 'simulacro',
    });
  });

  const resultado = {
    n: examen.preguntas.length,
    aciertos,
    pct: Math.round(100 * aciertos / examen.preguntas.length),
    minutos,
    sin_responder: examen.marcadas.filter(m => !m).length,
    porArea,
  };
  almacen.registrarSimulacro(resultado);
  return resultado;
}

/* ── Dibujo ──────────────────────────────────────────────── */

export function pintarPregunta(t, indice, total) {
  const letras = LETRAS.filter(l => l in t.opciones);
  const soloLetras = letras.every(l => !t.opciones[l].trim());
  const marcada = examen?.marcadas[indice];

  return `
    <div class="sim-cabecera">
      <span class="sim-indice">${indice + 1} <span>de ${total}</span></span>
      <button class="sim-duda ${examen?.dudosas.has(indice) ? 'activa' : ''}"
              type="button" data-duda="${indice}">Dudosa</button>
    </div>
    <p class="enunciado">${mate(t.enunciado)}</p>
    ${t.figura ? `<figure class="figura">
      <img src="data:image/png;base64,${t.figura.png}"
           width="${t.figura.ancho}" height="${t.figura.alto}"
           alt="Figura de la pregunta" decoding="async">
    </figure>` : ''}
    <div class="opciones ${soloLetras ? 'opciones-en-figura' : ''}">
      ${letras.map(l => `
        <button class="opcion ${marcada === l ? 'elegida' : ''}"
                data-letra="${l}">
          <span class="letra">${l}</span>
          ${soloLetras ? '' : `<span class="cuerpo">${mate(t.opciones[l])}</span>`}
        </button>`).join('')}
    </div>`;
}

export function pintarResultado(r) {
  const NOMBRES = {
    mecanica: 'Mecánica', electromagnetismo: 'Electromagnetismo',
    termo_estadistica: 'Termo y estadística', moderna_cuantica: 'Moderna y cuántica',
    relatividad: 'Relatividad', optica_ondas: 'Óptica y ondas',
  };
  // La meta del plan para el último simulacro antes del examen.
  const meta = r.pct >= 72;

  const areas = Object.entries(r.porArea)
    .sort((a, b) => (a[1].ok / a[1].n) - (b[1].ok / b[1].n))
    .map(([area, v]) => `
      <div class="barra-area" style="--color-area: var(--${area})">
        <div class="encabezado">
          <span>${escapar(NOMBRES[area] || area)}</span>
          <span class="pct">${v.ok}/${v.n}</span>
        </div>
        <div class="canal"><div class="relleno"
          style="width:${Math.round(100 * v.ok / v.n)}%"></div></div>
      </div>`).join('');

  return `
    <div class="tarjeta tarjeta-cierre">
      <div class="grande">${r.aciertos}/${r.n}</div>
      <p>${r.pct} % en ${r.minutos} minutos${
        r.sin_responder ? ` · ${r.sin_responder} sin responder` : ''}</p>
      <p>${meta
        ? 'Por encima del 72 % que pide el plan para noviembre.'
        : `La meta del plan es 18 de 25. Faltan ${Math.max(0, 18 - r.aciertos)}.`}</p>
    </div>
    <h2 class="seccion">Por área</h2>
    ${areas}
    <p class="nota-meta">Las que fallaste ya entraron en la cola de repaso:
    van a volver a salirte en el feed.</p>`;
}
