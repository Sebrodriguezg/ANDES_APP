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

/* El hueco del ordinal se deja siempre; se rellena cuando la tarjeta cuenta
   para la meta del día, que es al responderla o al haberla leído. */
function ranura(tarjeta) {
  const n = almacen.ordinalDe(tarjeta.id);
  return n
    ? `<span class="ordinal">#${n}</span>`
    : '<span class="punto-area ranura-ordinal"></span>';
}

export function pintarOrdinal(nodo, n) {
  const hueco = nodo.querySelector('.ranura-ordinal, .ordinal');
  if (!hueco || !n) return;
  const marca = document.createElement('span');
  marca.className = 'ordinal';
  marca.textContent = `#${n}`;
  hueco.replaceWith(marca);
}

function encabezado(tarjeta, tipoTexto, derecha = '') {
  return `
    <div class="etiqueta-tarjeta">
      ${ranura(tarjeta)}
      <span class="tipo">${escapar(tipoTexto)}</span>
      <span>${escapar(nombreArea(tarjeta.area))}</span>
      <span class="derecha">${escapar(derecha || tarjeta.codigo || '')}</span>
    </div>`;
}

function vibrar(ms) {
  if (navigator.vibrate) { try { navigator.vibrate(ms); } catch { /* sin soporte */ } }
}

/* ── Opción múltiple ──────────────────────────────────────── */

/* La figura va rescatada del PDF como PNG en base64, así que viaja dentro del
   contenido cifrado igual que el texto. */
function bloqueFigura(t) {
  if (!t.figura) return '';
  return `
    <figure class="figura">
      <img src="data:image/png;base64,${t.figura.png}"
           width="${t.figura.ancho}" height="${t.figura.alto}"
           alt="Figura de la pregunta" loading="lazy" decoding="async">
      <figcaption class="pie-figura">Figura del enunciado</figcaption>
    </figure>`;
}

function tarjetaMC(t, alResponder) {
  const letras = LETRAS.filter(l => l in t.opciones);
  // Hay preguntas cuyas cinco alternativas son gráficas: el texto de la opción
  // viene vacío y lo que se elige está dentro de la figura. En ese caso el botón
  // se queda solo con la letra.
  const soloLetras = letras.every(l => !t.opciones[l].trim());

  const nodo = elemento(`
    <article class="tarjeta tarjeta-mc${soloLetras ? ' opciones-en-figura' : ''}">
      ${encabezado(t, 'Pregunta', t.nivel === 'ALTO' ? 'nivel alto' : '')}
      <p class="enunciado">${mate(t.enunciado)}</p>
      ${bloqueFigura(t)}
      <div class="opciones">
        ${letras.map(l => `
          <button class="opcion" data-letra="${l}">
            <span class="letra">${l}</span>
            ${soloLetras ? '' : `<span class="cuerpo">${mate(t.opciones[l])}</span>`}
          </button>`).join('')}
      </div>
    </article>`);

  nodo.style.setProperty('--color-area', `var(--${t.area || 'transversal'})`);

  let respondida = false;

  function marcar(marcada, { anotar }) {
    if (respondida) return;
    respondida = true;

    const ok = marcada === t.respuesta;
    nodo.classList.add('respondida');

    nodo.querySelectorAll('.opcion').forEach(b => {
      if (b.dataset.letra === t.respuesta) b.classList.add('correcta');
      else if (b.dataset.letra === marcada) b.classList.add('incorrecta');
    });

    const fuente = t.origen === 'HRW7'
      ? `Halliday–Resnick–Walker · cap. ${(t.id.match(/c(\d+)/) || [, '?'])[1]}`
      : escapar(t.origen || '');

    nodo.insertAdjacentHTML('beforeend', `
      <div class="veredicto ${ok ? 'bien' : 'mal'}">
        <span>${ok ? '✓ Correcta' : `✗ Era ${t.respuesta}`}</span>
        <span class="fuente">${fuente}</span>
      </div>`);

    // Al repintar el historial del día no se vuelve a anotar la respuesta:
    // ya está registrada y contaría doble.
    if (!anotar) return;

    vibrar(ok ? 18 : [12, 40, 12]);
    // Una pregunta cuenta para la meta cuando la respondes, no cuando aparece.
    const n = almacen.contar(t.id, { codigo: t.codigo, tipo: t.tipo });
    pintarOrdinal(nodo, n);
    almacen.registrarRespuesta({
      id: t.id, area: t.area, nivel: t.nivel,
      patron: t.patron || '', marcada, correcta: t.respuesta, ok,
    });
    alResponder?.(ok);
  }

  nodo.querySelectorAll('.opcion').forEach(boton => {
    boton.addEventListener('click', () => marcar(boton.dataset.letra, { anotar: true }));
  });

  const previa = almacen.respuestaPrevia(t.id);
  if (previa) marcar(previa.marcada, { anotar: false });

  return nodo;
}

/* ── Patrón ───────────────────────────────────────────────── */

function tarjetaPatron(t) {
  const estado = t.estado_d1 === 'fallado' ? 'lo fallaste en el D1'
    : t.estado_d1 === 'acertado' ? 'lo acertaste en el D1' : '';

  const nodo = elemento(`
    <article class="tarjeta tarjeta-patron">
      <div class="etiqueta-tarjeta">
        ${ranura(t)}
        <span class="insignia-patron">${escapar(t.patron)}</span>
        <span class="tipo">Patrón</span>
        <span>${escapar(nombreArea(t.area))}</span>
        <span class="derecha">${escapar(estado || t.codigo || '')}</span>
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

/* ── Ecuación ─────────────────────────────────────────────── */

function tarjetaEcuacion(t) {
  const nodo = elemento(`
    <article class="tarjeta tarjeta-ecuacion">
      ${encabezado(t, 'Ecuación', t.semana || '')}
      <h3 class="titulo-tarjeta">${mate(t.titulo)}</h3>
      <div class="formula grande">${mate(t.formula)}</div>
      <div class="bloque"><span class="rotulo">Qué dice</span>${mate(t.significa)}</div>
      <div class="bloque trampa"><span class="rotulo">La trampa</span>${mate(t.trampa)}</div>
    </article>`);
  nodo.style.setProperty('--color-area', `var(--${t.area || 'transversal'})`);
  return nodo;
}

/* ── Técnica de descarte ──────────────────────────────────── */

/* Estas se revelan por pasos: primero la situación, y solo cuando has intentado
   descartar por tu cuenta aparecen las opciones muertas y la regla. */
function tarjetaDescarte(t) {
  const nodo = elemento(`
    <article class="tarjeta tarjeta-descarte">
      <div class="etiqueta-tarjeta">
        ${ranura(t)}
        <span class="tipo">Descarte</span>
        <span>${escapar(t.tecnica)}</span>
        <span class="derecha">${t.estado_d1 === 'fallado'
          ? 'lo fallaste en el D1' : escapar(t.codigo || '')}</span>
      </div>
      <h3 class="titulo-tarjeta">${mate(t.titulo)}</h3>
      <p class="enunciado">${mate(t.situacion)}</p>
      <button class="boton suave revelar" type="button">Ver qué se puede matar</button>
      <div class="oculto" hidden>
        <ul class="lista muertas">
          ${(t.opciones_falsas || []).map(o => `<li>${mate(o)}</li>`).join('')}
        </ul>
        <div class="bloque"><span class="rotulo">Conclusión</span>${mate(t.conclusion)}</div>
        <div class="bloque trampa"><span class="rotulo">La regla</span>${mate(t.regla)}</div>
      </div>
    </article>`);

  nodo.style.setProperty('--color-area', `var(--${t.area || 'transversal'})`);
  const boton = nodo.querySelector('.revelar');
  boton.addEventListener('click', () => {
    nodo.querySelector('.oculto').hidden = false;
    boton.remove();
    vibrar(12);
  });
  return nodo;
}

/* ── Dato / constante ─────────────────────────────────────── */

function tarjetaDato(t) {
  const nodo = elemento(`
    <article class="tarjeta tarjeta-dato">
      ${encabezado(t, 'Para memorizar')}
      <h3 class="titulo-tarjeta">${mate(t.titulo)}</h3>
      <div class="formula">${mate(t.valor)}</div>
      <div class="bloque"><span class="rotulo">Por qué importa</span>${mate(t.porque)}</div>
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

/* ── Reanudar la sesión del día ───────────────────────────── */

/* Entrar tres veces en un día no debería significar empezar tres veces. Esta
   tarjeta abre el feed diciendo por dónde ibas, y deja volver a lo anterior
   si quieres releer algo. */
export function tarjetaReanudar({ n, aciertos, meta, ultimo, alVerAnteriores }) {
  const nodo = elemento(`
    <article class="tarjeta tarjeta-reanudar">
      <div class="etiqueta-tarjeta">
        <span class="punto-area"></span>
        <span class="tipo">Continúas</span>
        <span class="derecha">hoy</span>
      </div>
      <div class="marcador">
        <span class="posicion">#${n}</span>
        <span class="de">de ${meta}</span>
      </div>
      <p>Llevas <strong>${aciertos}</strong> de ${n} hoy.
         ${ultimo ? `La última fue <strong>${escapar(ultimo)}</strong>.` : ''}
         Sigues en la <strong>#${n + 1}</strong>.</p>
      <button class="boton suave" type="button">Ver las anteriores</button>
    </article>`);

  const boton = nodo.querySelector('button');
  boton.addEventListener('click', async () => {
    boton.disabled = true;
    boton.textContent = 'Cargando…';
    await alVerAnteriores?.();
    boton.remove();
  });
  return nodo;
}

/* ── Despacho ─────────────────────────────────────────────── */

export function construir(t, alResponder) {
  switch (t.tipo) {
    case 'mc':       return tarjetaMC(t, alResponder);
    case 'patron':   return tarjetaPatron(t);
    case 'error':    return tarjetaError(t);
    case 'ecuacion': return tarjetaEcuacion(t);
    case 'descarte': return tarjetaDescarte(t);
    case 'dato':     return tarjetaDato(t);
    default:         return null;
  }
}
