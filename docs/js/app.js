/* Arranque, enrutado por hash y las vistas Hoy, Plan y Yo. */

import * as datos from './datos.js';
import * as almacen from './almacen.js';
import * as feed from './feed.js';
import { escapar } from './mate.js';

let crono = null;

const $ = id => document.getElementById(id);
const VISTAS = ['hoy', 'feed', 'plan', 'yo'];

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
        <div class="racha">${n ? `${aciertos} de ${n} hoy` : 'Sin tarjetas hoy todavía'}</div>
      </div>
    </div>

    ${dia ? `
      <h2 class="seccion">Hoy toca</h2>
      <div class="tarjeta">
        <div class="etiqueta-tarjeta">
          <span class="punto-area"></span>
          <span class="tipo">${escapar(datos.nombreBloque(dia.bloque))}</span>
          <span class="derecha">${dia.horas} h</span>
        </div>
        <p class="enunciado" style="margin:0">${escapar(dia.que)}</p>
      </div>` : ''}

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

  $('vista-yo').innerHTML = `
    <h2 class="seccion">Tu desempeño en la app</h2>
    <div class="rejilla-cifras">
      <div class="cifra"><div class="n">${t.n}</div><div class="r">respondidas</div></div>
      <div class="cifra"><div class="n">${t.pct}%</div><div class="r">acierto</div></div>
      <div class="cifra"><div class="n">${almacen.racha()}</div><div class="r">racha</div></div>
      <div class="cifra"><div class="n">${repaso.length}</div><div class="r">por repasar</div></div>
    </div>

    <h2 class="seccion">Por área</h2>
    ${barras || '<p class="vacio">Responde algunas preguntas en el feed y aquí aparece el desglose.</p>'}

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
    </div>`;

  $('meta').addEventListener('change', e => {
    almacen.fijarMeta(parseInt(e.target.value, 10) || 30);
    feed.refrescarProgreso();
  });

  $('exportar').addEventListener('click', () => {
    // La app no puede escribir archivos: se copia al portapapeles y de ahí
    // se pega en 06_SEGUIMIENTO para el medidor.
    navigator.clipboard?.writeText(almacen.exportarCSV())
      .then(() => { $('exportar').textContent = 'Copiado al portapapeles'; })
      .catch(() => { $('exportar').textContent = 'No pude copiar'; });
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

/* ── Desbloqueo ───────────────────────────────────────────── */

/** El contenido va cifrado porque el repositorio es público. La frase se pide
 *  una sola vez: después queda la clave derivada guardada en el teléfono. */
function pedirClave() {
  return new Promise(resolve => {
    const capa = document.createElement('div');
    capa.className = 'capa-clave';
    capa.innerHTML = `
      <div class="tarjeta caja-clave">
        <div class="candado">⚛</div>
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
  if (vista === 'plan') pintarPlan();
  if (vista === 'yo') pintarYo();
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
}

arrancar();
