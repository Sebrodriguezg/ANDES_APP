/* Arranque, enrutado por hash y las vistas Hoy, Plan y Yo. */

import * as datos from './datos.js';
import * as almacen from './almacen.js';
import * as feed from './feed.js';
import * as simulacro from './simulacro.js';
import * as hoja from './hoja.js';
import { escapar } from './mate.js';

let crono = null;

/* Dónde vive lo que la app no puede llevar dentro: los libros, los bancos de
   examen y el material de seguimiento. Son 650 MB con copyright, así que no
   pueden estar en un repositorio público. */
const CARPETA_DRIVE =
  'https://drive.google.com/drive/folders/1py2fECGlQFPfMQoG-C6TOAmt_fT_80Ai';
const REPOSITORIO = 'https://github.com/Sebrodriguezg/ANDES_APP';

const $ = id => document.getElementById(id);
const VISTAS = ['hoy', 'feed', 'hoja', 'plan', 'yo', 'simulacro'];

/* ── Vista HOY ────────────────────────────────────────────── */

function anillo(n, meta) {
  const r = 34, c = 2 * Math.PI * r;
  const frac = Math.min(1, meta ? n / meta : 0);
  return `
    <div class="anillo">
      <svg width="84" height="84" viewBox="0 0 84 84" aria-hidden="true">
        <circle cx="42" cy="42" r="${r}" fill="none"
                stroke="var(--borde)" stroke-width="7"/>
        <circle cx="42" cy="42" r="${r}" fill="none"
                stroke="var(--acento)" stroke-width="7" stroke-linecap="round"
                stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - frac)}"/>
      </svg>
      <div class="centro">
        <span class="n">${n}</span>
        <span class="de">de ${meta}</span>
      </div>
    </div>`;
}

function listaSeccion(titulo, renglones) {
  if (!renglones?.length) return '';
  return `
    <h2 class="seccion">${escapar(titulo)}</h2>
    <ul class="lista">${renglones.map(r => `<li>${escapar(r)}</li>`).join('')}</ul>`;
}

function pintarHoy() {
  const hoy = datos.hoyISO();
  const semana = datos.semanaDe(crono, hoy);
  const dia = datos.diaDe(semana, hoy);
  const { n, aciertos } = almacen.progresoHoy();
  const meta = almacen.metaDiaria();
  const s = semana.secciones || {};

  const enCurso = hoy >= semana.inicio && hoy <= semana.fin;

  $('vista-hoy').innerHTML = `
    <div class="cabecera-hoy">
      <div class="fecha">${escapar(datos.fechaLarga(hoy))}</div>
      <h1>${escapar(semana.titulo)}</h1>
      <div class="semana">${escapar(semana.id)} · ${escapar(datos.rangoCorto(semana.inicio, semana.fin))}
        ${enCurso ? '' : ' · aún no empieza'}</div>
    </div>

    <div class="anillo-fila">
      ${anillo(n, meta)}
      <div>
        <div class="racha"><strong>${almacen.racha()}</strong> días seguidos</div>
        <div class="racha">${n
          ? `${aciertos} de ${n} hoy · vas en la <strong>#${n}</strong>`
          : 'Sin tarjetas hoy todavía'}</div>
      </div>
    </div>

    ${dia ? `
      <h2 class="seccion">Hoy toca</h2>
      <div class="tarjeta">
        <div class="etiqueta-tarjeta">
          <span class="punto-area"></span>
          <span class="tipo">${escapar(datos.nombreBloque(dia.bloque))}</span>
          <span class="derecha">${dia.horas ? dia.horas + ' h' : 'sin asignación'}</span>
        </div>
        <p class="enunciado"${dia.material?.length ? '' : ' style="margin:0"'}>${escapar(dia.que)}</p>
        ${dia.material?.length ? `
          <div class="bloque">
            <span class="rotulo">Con qué</span>
            <ul class="lista material">
              ${dia.material.map(m => `<li>${escapar(m)}</li>`).join('')}
            </ul>
          </div>` : ''}
      </div>` : ''}

    <a class="boton suave enlace-simulacro" href="#simulacro">Hacer un simulacro completo</a>
    <a class="boton suave enlace-simulacro" href="${CARPETA_DRIVE}"
       target="_blank" rel="noopener noreferrer">Descargar todo el material</a>

    ${listaSeccion('Temas de la semana', s['Temas'] || s['Temas — prioridad descendente'])}
    ${listaSeccion('Leer — base', s['BASE — leer'] || s['BASE/ALTO — leer (en este orden)']
        || s['BASE/ALTO — leer (núcleo de la semana)'])}
    ${listaSeccion('Leer — alto', s['ALTO — leer'] || s['ALTO — leer (núcleo de la semana)'])}
    ${listaSeccion('Problemas', s['PROBLEMAS'])}
    ${listaSeccion('Entregable', s['Entregable'])}
  `;

  $('vista-hoy').querySelectorAll('.punto-area').forEach(el => {
    el.style.background = `var(--${semana.area || 'transversal'})`;
  });
}

/* ── Vista PLAN ───────────────────────────────────────────── */

function pintarPlan() {
  const hoy = datos.hoyISO();
  const actual = datos.semanaDe(crono, hoy);

  $('vista-plan').innerHTML = `
    <h2 class="seccion">Las 14 semanas</h2>
    <div id="lista-semanas"></div>
    <div class="detalle-semana" id="detalle-semana"></div>`;

  const lista = $('lista-semanas');
  for (const s of crono.semanas) {
    const clase = s.id === actual.id ? 'actual' : (s.fin < hoy ? 'pasada' : '');
    const fila = document.createElement('button');
    fila.className = `fila-semana ${clase}`;
    fila.style.setProperty('--color-area', `var(--${s.area || 'transversal'})`);
    fila.innerHTML = `
      <span class="ident">${escapar(s.id)}</span>
      <span class="texto">
        <span class="titulo">${escapar(s.titulo)}</span>
        <span class="rango">${escapar(datos.rangoCorto(s.inicio, s.fin))}</span>
      </span>`;
    fila.addEventListener('click', () => detalleSemana(s));
    lista.append(fila);
  }
  detalleSemana(actual);
}

function detalleSemana(s) {
  const sec = s.secciones || {};
  const bloques = Object.entries(sec)
    .map(([titulo, renglones]) => listaSeccion(titulo, renglones))
    .join('');

  $('detalle-semana').innerHTML = `
    <h2 class="seccion">${escapar(s.id)} · ${escapar(s.titulo)}</h2>
    <div class="tarjeta">
      ${(s.dias || []).map(d => `
        <div class="bloque-dia ${d.fecha === datos.hoyISO() ? 'hoy' : ''}">
          <span class="dia">${escapar(datos.nombreDia(d.dia))}</span>
          <span>${escapar(d.que)}</span>
          <span class="horas">${d.horas ? d.horas + ' h' : '—'}</span>
        </div>`).join('')}
    </div>
    ${bloques || '<p class="vacio">Esta semana no tiene desglose en 03_TEMARIO.</p>'}`;
  $('detalle-semana').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ── Vista YO ─────────────────────────────────────────────── */

function pintarYo() {
  const t = almacen.totales();
  const porArea = almacen.aciertoPorArea();
  const repaso = almacen.pendientesDeRepaso();

  const barras = Object.entries(porArea)
    .sort((a, b) => (a[1].ok / a[1].n) - (b[1].ok / b[1].n))
    .map(([area, r]) => {
      const pct = Math.round(100 * r.ok / r.n);
      return `
        <div class="barra-area" style="--color-area: var(--${area})">
          <div class="encabezado">
            <span>${escapar(datos.nombreArea(area))}</span>
            <span class="pct">${r.ok}/${r.n} · ${pct}%</span>
          </div>
          <div class="canal"><div class="relleno" style="width:${pct}%"></div></div>
        </div>`;
    }).join('');

  const medio = almacen.tiempoMedio();
  const reloj = medio
    ? `${Math.floor(medio / 60)}:${String(medio % 60).padStart(2, '0')}`
    : '—';

  const CAUSAS = {
    concepto: 'No sabía la física', algebra: 'Error de cuentas',
    lectura: 'Leí mal', tiempo: 'Me quedé sin tiempo',
  };
  const causas = almacen.porCausa();
  const totalCausas = Object.values(causas).reduce((a, b) => a + b, 0);
  const bloqueCausas = totalCausas ? Object.entries(causas)
    .sort((a, b) => b[1] - a[1])
    .map(([k, n]) => `
      <div class="fila-dato" style="--color-dato: var(--aviso)">
        <span class="etiqueta">${escapar(CAUSAS[k] || k)}</span>
        <span class="canal"><span class="relleno"
          style="width:${Math.round(100 * n / totalCausas)}%"></span></span>
        <span class="valor">${n}</span>
      </div>`).join('') : '';

  // La calibración es el dato que más cuesta ver de otra forma: confianza alta
  // con acierto bajo es exactamente lo que pasó en la pregunta 8 del D1.
  const cal = almacen.calibracion();
  const NIVEL = { 1: 'Adiviné', 2: 'Dudo', 3: 'Creo que sí', 4: 'Seguro' };
  const bloqueCalibracion = Object.keys(cal).length ? [4, 3, 2, 1]
    .filter(n => cal[n])
    .map(n => {
      const { n: total, ok } = cal[n];
      const pct = Math.round(100 * ok / total);
      const peligro = n >= 3 && pct < 60;
      return `
        <div class="fila-dato ${peligro ? 'alerta' : ''}"
             style="--color-dato: var(--${peligro ? 'mal' : 'ok'})">
          <span class="etiqueta">${NIVEL[n]}</span>
          <span class="canal"><span class="relleno" style="width:${pct}%"></span></span>
          <span class="valor">${ok}/${total} · ${pct}%</span>
        </div>`;
    }).join('') : '';

  $('vista-yo').innerHTML = `
    <h2 class="seccion">Tu desempeño en la app</h2>
    <div class="rejilla-cifras">
      <div class="cifra"><div class="n">${t.n}</div><div class="r">respondidas</div></div>
      <div class="cifra"><div class="n">${t.pct}%</div><div class="r">acierto</div></div>
      <div class="cifra"><div class="n">${reloj}</div><div class="r">por pregunta</div></div>
      <div class="cifra"><div class="n">${repaso.length}</div><div class="r">toca repasar</div></div>
      <div class="cifra"><div class="n">${almacen.racha()}</div><div class="r">racha</div></div>
      <div class="cifra"><div class="n">${almacen.enCola()}</div><div class="r">en la cola</div></div>
    </div>
    ${medio ? `<p class="nota-meta">${medio <= 360
        ? 'Vas por debajo de los 6 min que pide el plan.'
        : `Meta: 6:00 por pregunta. Vas ${Math.round((medio - 360) / 6)} % por encima.`}</p>` : ''}

    <h2 class="seccion">Todo el material</h2>
    <div class="tarjeta">
      <p style="margin:0 0 12px;color:var(--texto-suave);font-size:.9rem">
        Los libros, los bancos de examen, el plan, el temario y el seguimiento
        completos. Un gigabyte que la app no puede llevar dentro.
      </p>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <a class="boton suave enlace-externo" href="${CARPETA_DRIVE}"
           target="_blank" rel="noopener noreferrer">Descargar el paquete</a>
        <a class="boton suave enlace-externo" href="${REPOSITORIO}"
           target="_blank" rel="noopener noreferrer">Ver el repositorio</a>
      </div>
      <p class="pie-fuentes">
        El banco sale de Halliday–Resnick–Walker, del GRE Physics del ETS, del
        EUF de Brasil y del examen de admisión de Uniandes 2024. Material de
        estudio personal.
        <br><span id="version-contenido"></span>
      </p>
    </div>

    <h2 class="seccion">Por área</h2>
    ${barras || '<p class="vacio">Responde algunas preguntas en el feed y aquí aparece el desglose.</p>'}

    ${bloqueCausas ? `<h2 class="seccion">Por qué fallas</h2>${bloqueCausas}` : ''}

    ${bloqueCalibracion ? `<h2 class="seccion">Qué tan bien sabes lo que sabes</h2>
      ${bloqueCalibracion}
      <p class="nota-meta">Marcar alto y fallar es el caso peligroso: crees que
      la sabes, así que nunca la vuelves a repasar.</p>` : ''}

    <h2 class="seccion">Ajustes</h2>
    <div class="tarjeta">
      <label style="display:flex;align-items:center;gap:12px">
        <span style="flex:1">Meta diaria</span>
        <input id="meta" type="number" min="5" max="200" value="${almacen.metaDiaria()}"
               style="width:80px;padding:8px;border-radius:8px;border:1px solid var(--borde);
                      background:var(--tarjeta-alta);color:var(--texto)">
      </label>
      <div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap">
        <button class="boton suave" id="exportar">Exportar respuestas (CSV)</button>
        <button class="boton suave" id="reiniciar">Borrar mi progreso</button>
      </div>
    </div>

    <h2 class="seccion">Pasar el progreso a otro aparato</h2>
    <div class="tarjeta">
      <p style="margin:0 0 12px;color:var(--texto-suave);font-size:.9rem">
        El avance vive en este navegador. Para seguir en otro, copia el código
        aquí y pégalo allá. Se fusiona con lo que ya hubiera, no lo pisa.
      </p>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <button class="boton suave" id="copiar-estado">Copiar mi progreso</button>
        <button class="boton suave" id="pegar-estado">Pegar progreso</button>
      </div>
      <textarea id="caja-estado" rows="3" hidden
        placeholder="Pega aquí el código que empieza por ANDES1:"
        style="width:100%;margin-top:12px;padding:10px;border-radius:var(--radio);
               border:1px solid var(--borde-vivo);background:var(--fondo);
               color:var(--texto);font-family:var(--mono);font-size:.72rem"></textarea>
      <div id="aviso-estado" style="margin-top:10px;font-size:.84rem"></div>
    </div>`;

  $('meta').addEventListener('change', e => {
    almacen.fijarMeta(parseInt(e.target.value, 10) || 30);
    feed.refrescarProgreso();
  });

  // Qué versión del contenido tiene este aparato. Útil cuando un despliegue
  // falla y la app se queda sirviendo lo de antes sin que se note.
  datos.cargarManifiesto().then(m => {
    const marca = $('version-contenido');
    if (marca && m.generado) {
      marca.textContent = `Contenido del ${m.generado} · ${m.total} tarjetas.`;
    }
  }).catch(() => {});

  $('exportar').addEventListener('click', () => {
    // La app no puede escribir archivos: se copia al portapapeles y de ahí
    // se pega en 06_SEGUIMIENTO para el medidor.
    navigator.clipboard?.writeText(almacen.exportarCSV())
      .then(() => { $('exportar').textContent = 'Copiado al portapapeles'; })
      .catch(() => { $('exportar').textContent = 'No pude copiar'; });
  });

  const caja = $('caja-estado');
  const aviso = $('aviso-estado');

  $('copiar-estado').addEventListener('click', () => {
    const codigo = almacen.exportarEstado();
    navigator.clipboard?.writeText(codigo)
      .then(() => { aviso.textContent = `Copiado (${codigo.length} caracteres).`;
                    aviso.style.color = 'var(--ok)'; })
      .catch(() => { caja.hidden = false; caja.value = codigo; caja.select();
                     aviso.textContent = 'No pude copiar solo: cópialo de la caja.';
                     aviso.style.color = 'var(--aviso)'; });
  });

  $('pegar-estado').addEventListener('click', () => {
    if (caja.hidden) {
      caja.hidden = false;
      caja.value = '';
      caja.focus();
      aviso.textContent = 'Pega el código y vuelve a tocar el botón.';
      aviso.style.color = 'var(--texto-tenue)';
      return;
    }
    const r = almacen.importarEstado(caja.value);
    aviso.textContent = r.ok
      ? `Listo: ${r.respuestas} respuestas en total.`
      : `No se pudo: ${r.motivo}.`;
    aviso.style.color = r.ok ? 'var(--ok)' : 'var(--mal)';
    if (r.ok) { caja.hidden = true; pintarYo(); }
  });

  $('reiniciar').addEventListener('click', () => {
    if ($('reiniciar').dataset.seguro !== '1') {
      $('reiniciar').dataset.seguro = '1';
      $('reiniciar').textContent = '¿Seguro? Toca otra vez';
      return;
    }
    almacen.reiniciar();
    pintarYo();
  });
}

/** Avisa cuando se publicó contenido nuevo desde la última visita.
 *
 *  El service worker puede tardar en reemplazar lo cacheado, y sin aviso no hay
 *  forma de saber que lo que estás viendo ya se corrigió. */
async function avisarSiHayContenidoNuevo() {
  try {
    const m = await datos.cargarManifiesto();
    const firma = `${m.total}·${m.semilla}·${m.tandas.length}`;
    const previa = localStorage.getItem('andes.firma');
    localStorage.setItem('andes.firma', firma);

    if (!previa || previa === firma) return;

    const aviso = document.createElement('div');
    aviso.className = 'aviso-actualizacion';
    aviso.innerHTML = `<span>Hay contenido corregido.</span>
      <button type="button">Recargar</button>`;
    aviso.querySelector('button').addEventListener('click', async () => {
      if ('caches' in window) {
        for (const c of await caches.keys()) await caches.delete(c);
      }
      location.reload();
    });
    document.body.append(aviso);
  } catch { /* sin manifiesto no hay nada que comparar */ }
}

/* ── Vista SIMULACRO ──────────────────────────────────────── */

let relojSimulacro = null;

function salaDeExamen() {
  const ex = simulacro.estado();
  let i = 0;

  function reloj() {
    const s = Math.round(simulacro.segundosRestantes());
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const marca = $('sim-reloj');
    if (marca) {
      marca.textContent = `${h}:${String(m).padStart(2, '0')}`;
      marca.classList.toggle('poco', s < 15 * 60);
    }
    if (s <= 0) terminar();
  }

  function pintar() {
    $('sim-cuerpo').innerHTML = simulacro.pintarPregunta(
      ex.preguntas[i], i, ex.preguntas.length);

    $('sim-cuerpo').querySelectorAll('.opcion').forEach(b => {
      b.addEventListener('click', () => {
        simulacro.marcar(i, b.dataset.letra);
        pintar();
      });
    });
    $('sim-cuerpo').querySelector('.sim-duda')?.addEventListener('click', () => {
      simulacro.alternarDuda(i);
      pintar();
    });
    pintarMapa();
    $('sim-anterior').disabled = i === 0;
    window.scrollTo(0, 0);
  }

  function pintarMapa() {
    $('sim-mapa').innerHTML = ex.preguntas.map((_, k) => `
      <button class="sim-casilla ${k === i ? 'actual' : ''}
        ${ex.marcadas[k] ? 'hecha' : ''} ${ex.dudosas.has(k) ? 'dudosa' : ''}"
        data-ir="${k}">${k + 1}</button>`).join('');
    $('sim-mapa').querySelectorAll('[data-ir]').forEach(b => {
      b.addEventListener('click', () => { i = Number(b.dataset.ir); pintar(); });
    });
  }

  function terminar() {
    clearInterval(relojSimulacro);
    const r = simulacro.corregir();
    $('vista-simulacro').innerHTML = `
      <div class="cabecera-hoy"><h1>Simulacro terminado</h1></div>
      ${simulacro.pintarResultado(r)}
      <button class="boton" id="sim-salir" type="button">Volver</button>`;
    $('sim-salir').addEventListener('click', () => { location.hash = 'hoy'; });
  }

  $('vista-simulacro').innerHTML = `
    <div class="sim-barra">
      <span class="sim-reloj" id="sim-reloj">3:00</span>
      <button class="sim-entregar" id="sim-entregar" type="button">Entregar</button>
    </div>
    <div class="tarjeta" id="sim-cuerpo"></div>
    <div class="sim-mapa" id="sim-mapa"></div>
    <div class="sim-nav">
      <button class="boton suave" id="sim-anterior" type="button">Anterior</button>
      <button class="boton" id="sim-siguiente" type="button">Siguiente</button>
    </div>`;

  $('sim-anterior').addEventListener('click', () => { if (i > 0) { i--; pintar(); } });
  $('sim-siguiente').addEventListener('click', () => {
    if (i < ex.preguntas.length - 1) { i++; pintar(); }
  });
  $('sim-entregar').addEventListener('click', () => {
    const faltan = ex.marcadas.filter(m => !m).length;
    const boton = $('sim-entregar');
    if (faltan && boton.dataset.seguro !== '1') {
      boton.dataset.seguro = '1';
      boton.textContent = `Faltan ${faltan}. ¿Entregar?`;
      return;
    }
    terminar();
  });

  pintar();
  clearInterval(relojSimulacro);
  relojSimulacro = setInterval(reloj, 1000);
  reloj();
}

async function pintarSimulacro() {
  if (simulacro.estado() && !simulacro.estado().fin) { salaDeExamen(); return; }

  const ultimo = almacen.ultimoSimulacro();
  $('vista-simulacro').innerHTML = `
    <div class="cabecera-hoy">
      <div class="fecha">Semanas 12 y 13 del plan</div>
      <h1>Simulacro</h1>
    </div>
    <div class="tarjeta">
      <p class="enunciado">25 preguntas y 3 horas, con el reparto del examen
      real: 8 de mecánica, 6 de electromagnetismo, 5 de termodinámica y
      estadística, 4 de cuántica y moderna, 2 de relatividad.</p>
      <p class="enunciado">No se corrige nada hasta el final. Lo que se entrena
      aquí no es la física, es aguantar tres horas sin saber si vas bien y
      repartir el tiempo entre las veinticinco.</p>
      ${ultimo ? `<div class="bloque"><span class="rotulo">Último</span>
        ${ultimo.aciertos}/${ultimo.n} · ${ultimo.pct} % en ${ultimo.minutos} min
        (${ultimo.fecha})</div>` : ''}
      <button class="boton" id="sim-empezar" type="button">Empezar</button>
    </div>`;

  $('sim-empezar').addEventListener('click', async () => {
    $('sim-empezar').disabled = true;
    $('sim-empezar').textContent = 'Armando el examen…';
    try {
      await simulacro.armar();
      salaDeExamen();
    } catch {
      $('vista-simulacro').innerHTML =
        '<p class="vacio">No pude armar el simulacro. ¿Metiste la clave?</p>';
    }
  });
}

/* ── Desbloqueo ───────────────────────────────────────────── */

/** El contenido va cifrado porque el repositorio es público. La frase se pide
 *  una sola vez: después queda la clave derivada guardada en el teléfono. */
function pedirClave() {
  return new Promise(resolve => {
    const capa = document.createElement('div');
    capa.className = 'capa-clave';
    capa.innerHTML = `
      <div class="tarjeta caja-clave">
        <svg class="candado" viewBox="0 0 512 512" aria-hidden="true">
          <defs>
            <linearGradient id="inferno-clave" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0" stop-color="#420A68"/><stop offset="0.4" stop-color="#932667"/>
              <stop offset="0.7" stop-color="#F37819"/><stop offset="1" stop-color="#FCFFA4"/>
            </linearGradient>
          </defs>
          <path d="M20 400 L196 96 L272 246 L332 158 L492 400 Z" fill="url(#inferno-clave)"/>
          <rect x="20" y="418" width="472" height="26" fill="#FCA50A"/>
        </svg>
        <h3 class="titulo-tarjeta">Desbloquear el contenido</h3>
        <p style="color:var(--texto-suave);font-size:.9rem">
          El banco de preguntas va cifrado porque el repositorio es público.
          Escribe la clave una vez y queda guardada en este dispositivo.
        </p>
        <input id="frase" type="text" inputmode="text" autocapitalize="none"
               autocomplete="off" spellcheck="false" placeholder="andes-····-····-····">
        <div class="error-clave" id="error-clave" hidden>Clave incorrecta</div>
        <button class="boton" id="abrir" type="button">Abrir</button>
      </div>`;
    document.body.append(capa);

    const campo = capa.querySelector('#frase');
    const boton = capa.querySelector('#abrir');
    const error = capa.querySelector('#error-clave');

    async function intentar() {
      const frase = campo.value.trim();
      if (!frase) return;
      boton.disabled = true;
      boton.textContent = 'Comprobando…';
      error.hidden = true;

      const ok = await datos.desbloquear(frase);
      if (ok) { capa.remove(); resolve(true); return; }

      boton.disabled = false;
      boton.textContent = 'Abrir';
      error.hidden = false;
      campo.select();
    }

    boton.addEventListener('click', intentar);
    campo.addEventListener('keydown', e => { if (e.key === 'Enter') intentar(); });
    setTimeout(() => campo.focus(), 60);
  });
}

/* ── Enrutado ─────────────────────────────────────────────── */

async function mostrar(vista) {
  if (!VISTAS.includes(vista)) vista = 'hoy';

  for (const v of VISTAS) $(`vista-${v}`).hidden = v !== vista;
  document.querySelectorAll('.barra-inferior button').forEach(b => {
    b.classList.toggle('activa', b.dataset.vista === vista);
  });

  if (vista === 'hoy') pintarHoy();
  if (vista === 'hoja') await hoja.pintar();
  if (vista === 'plan') pintarPlan();
  if (vista === 'yo') pintarYo();
  if (vista === 'simulacro') await pintarSimulacro();
  if (vista === 'feed') await feed.iniciar(crono);

  if (vista !== 'feed') window.scrollTo(0, 0);
}

function rutaActual() {
  return (location.hash || '#hoy').slice(1);
}

async function arrancar() {
  try {
    crono = await datos.cargarCronograma();
  } catch (e) {
    document.getElementById('vistas').innerHTML =
      `<p class="vacio">No pude cargar el contenido.<br>${escapar(e.message)}
       <br><br>Si abriste el archivo con doble clic, no va a funcionar:
       hay que servirlo por HTTP.</p>`;
    return;
  }

  $('dias-restantes').textContent = datos.diasHasta(crono.examen);

  // Hoy y Plan salen del cronograma, que va en claro; solo el feed necesita la
  // clave. Se pide al arrancar para no interrumpir a mitad del scroll.
  try {
    if (await datos.necesitaClave()) await pedirClave();
  } catch { /* sin manifiesto: el feed avisará por su cuenta */ }

  document.querySelectorAll('.barra-inferior button').forEach(b => {
    b.addEventListener('click', () => { location.hash = b.dataset.vista; });
  });
  window.addEventListener('hashchange', () => mostrar(rutaActual()));

  await mostrar(rutaActual());

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').catch(() => { /* sin conexión */ });
  }

  avisarSiHayContenidoNuevo();
}

arrancar();
