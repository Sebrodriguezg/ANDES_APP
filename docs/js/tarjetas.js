/* Construcción del DOM de cada tipo de tarjeta del feed. */

import { mate, escapar } from './mate.js';
import { nombreArea } from './datos.js';
import * as almacen from './almacen.js';

const LETRAS = ['A', 'B', 'C', 'D', 'E'];

function elemento(html) {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

function encabezado(tarjeta, tipoTexto, derecha = '') {
  return `
    <div class="etiqueta-tarjeta">
      <span class="punto-area"></span>
      <span class="tipo">${escapar(tipoTexto)}</span>
      <span>${escapar(nombreArea(tarjeta.area))}</span>
      ${derecha ? `<span class="derecha">${escapar(derecha)}</span>` : ''}
    </div>`;
}

function vibrar(ms) {
  if (navigator.vibrate) { try { navigator.vibrate(ms); } catch { /* sin soporte */ } }
}

/* ── Opción múltiple ──────────────────────────────────────── */

function tarjetaMC(t, alResponder) {
  const letras = LETRAS.filter(l => l in t.opciones);
  const nodo = elemento(`
    <article class="tarjeta tarjeta-mc">
      ${encabezado(t, 'Pregunta', t.nivel === 'ALTO' ? 'nivel alto' : '')}
      <p class="enunciado">${mate(t.enunciado)}</p>
      <div class="opciones">
        ${letras.map(l => `
          <button class="opcion" data-letra="${l}">
            <span class="letra">${l}</span>
            <span class="cuerpo">${mate(t.opciones[l])}</span>
          </button>`).join('')}
      </div>
    </article>`);

  nodo.style.setProperty('--color-area', `var(--${t.area || 'transversal'})`);

  let respondida = false;
  nodo.querySelectorAll('.opcion').forEach(boton => {
    boton.addEventListener('click', () => {
      if (respondida) return;
      respondida = true;

      const marcada = boton.dataset.letra;
      const ok = marcada === t.respuesta;
      nodo.classList.add('respondida');

      nodo.querySelectorAll('.opcion').forEach(b => {
        if (b.dataset.letra === t.respuesta) b.classList.add('correcta');
        else if (b === boton) b.classList.add('incorrecta');
      });

      vibrar(ok ? 18 : [12, 40, 12]);

      const fuente = t.origen === 'HRW7'
        ? `Halliday–Resnick–Walker · cap. ${(t.id.match(/c(\d+)/) || [, '?'])[1]}`
        : escapar(t.origen || '');

      nodo.insertAdjacentHTML('beforeend', `
        <div class="veredicto ${ok ? 'bien' : 'mal'}">
          <span>${ok ? '✓ Correcta' : `✗ Era ${t.respuesta}`}</span>
          <span class="fuente">${fuente}</span>
        </div>`);

      almacen.registrarRespuesta({
        id: t.id, area: t.area, nivel: t.nivel,
        patron: t.patron || '', marcada, correcta: t.respuesta, ok,
      });
      alResponder?.(ok);
    });
  });

  return nodo;
}

/* ── Patrón ───────────────────────────────────────────────── */

function tarjetaPatron(t) {
  const estado = t.estado_d1 === 'fallado' ? 'lo fallaste en el D1'
    : t.estado_d1 === 'acertado' ? 'lo acertaste en el D1' : '';

  const nodo = elemento(`
    <article class="tarjeta tarjeta-patron">
      <div class="etiqueta-tarjeta">
        <span class="insignia-patron">${escapar(t.patron)}</span>
        <span class="tipo">Patrón</span>
        <span>${escapar(nombreArea(t.area))}</span>
        ${estado ? `<span class="derecha">${escapar(estado)}</span>` : ''}
      </div>
      <h3 class="titulo-tarjeta">${mate(t.titulo)}</h3>
      <p class="enunciado">${mate(t.idea)}</p>
      <div class="formula">${mate(t.formula)}</div>
      <div class="bloque"><span class="rotulo">Cuándo aparece</span>${mate(t.cuando)}</div>
      <div class="bloque trampa"><span class="rotulo">La trampa</span>${mate(t.trampa)}</div>
    </article>`);
  nodo.style.setProperty('--color-area', `var(--${t.area || 'transversal'})`);
  return nodo;
}

/* ── Error propio ─────────────────────────────────────────── */

const CAUSAS = {
  concepto: 'No sabías la física',
  algebra: 'Error de cuentas',
  lectura: 'Mala lectura del enunciado',
  tiempo: 'Se acabó el tiempo',
};

function tarjetaError(t) {
  const nodo = elemento(`
    <article class="tarjeta tarjeta-error">
      ${encabezado(t, 'Tu error', t.simulacro)}
      <h3 class="titulo-tarjeta">${mate(t.titulo)}</h3>
      <div class="comparacion">
        <div class="tuya">
          <span class="rotulo">Marcaste</span>
          <span class="valor">${escapar(t.marcaste)}</span>
        </div>
        <div class="correcta">
          <span class="rotulo">Era</span>
          <span class="valor">${escapar(t.respuesta)}</span>
        </div>
      </div>
      <div class="bloque">
        <span class="rotulo">Por qué falló</span>
        ${escapar(CAUSAS[t.causa] || t.causa || '—')}
      </div>
      ${t.patron ? `<div class="bloque"><span class="rotulo">Patrón</span>
        ${escapar(t.patron)} — búscalo en el feed y en 03_TEMARIO</div>` : ''}
    </article>`);
  nodo.style.setProperty('--color-area', `var(--${t.area || 'transversal'})`);
  return nodo;
}

/* ── Cierre de sesión ─────────────────────────────────────── */

export function tarjetaCierre({ n, aciertos, alSeguir }) {
  const pct = n ? Math.round(100 * aciertos / n) : 0;
  const nodo = elemento(`
    <article class="tarjeta tarjeta-cierre">
      <div class="grande">${aciertos}/${n}</div>
      <p>Meta del día cumplida — ${pct}% de acierto.</p>
      <p>Aquí se para. El feed tiene final a propósito: eso es lo que lo separa
         de las apps que borraste.</p>
      <button class="boton suave" type="button">Seguir de todos modos</button>
    </article>`);
  nodo.querySelector('button').addEventListener('click', () => {
    nodo.remove();
    alSeguir?.();
  });
  return nodo;
}

/* ── Despacho ─────────────────────────────────────────────── */

export function construir(t, alResponder) {
  switch (t.tipo) {
    case 'mc':     return tarjetaMC(t, alResponder);
    case 'patron': return tarjetaPatron(t);
    case 'error':  return tarjetaError(t);
    default:       return null;
  }
}
