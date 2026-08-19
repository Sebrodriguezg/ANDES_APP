/* Vista HOJA — la hoja de repaso, dentro de la app.

   Es el mismo material que produce 07_APP/tuberia/hoja_definitiva.py como
   página suelta, pero servido desde el corpus que la app ya tiene: los diez
   patrones, las ecuaciones por área, las constantes, los casos de descarte, el
   expediente del D1 y el protocolo del día.

   Dos cosas que conviene no olvidar:

   - El material llega en `contenido/hoja.bin`, un paquete aparte. Estas
     cuarenta tarjetas están dispersas por las trece tandas, y reunirlas desde
     el feed obligaría a bajarse 1,2 MB para usar el 1,5 %.
   - El color no decora: codifica riesgo. Un patrón sale caliente si lo fallaste
     en el diagnóstico y frío si lo dominas. Es la única forma de ver de un
     vistazo dónde está el peligro. */

import * as datos from './datos.js';
import { renderFormula } from './formula.js';
import { escapar, mate } from './mate.js';

const $ = id => document.getElementById(id);

/* El orden en que caen en el examen, no el alfabético. */
const ORDEN_AREAS = [
  'mecanica', 'electromagnetismo', 'termo_estadistica',
  'relatividad', 'moderna_cuantica', 'optica_ondas', 'transversal',
];

const ESTADOS = {
  fallado:  { clase: 'falla',   texto: 'Fallado en el D1' },
  acertado: { clase: 'acierta', texto: 'Acertado en el D1' },
};
const SIN_EVALUAR = { clase: 'virgen', texto: 'Sin evaluar aún' };

const SECCIONES = [
  ['reparto', 'Reparto'],
  ['patrones', 'Patrones'],
  ['ecuaciones', 'Ecuaciones'],
  ['constantes', 'Constantes'],
  ['descarte', 'Descarte'],
  ['expediente', 'D1'],
  ['protocolo', 'Protocolo'],
];

/* ── Piezas ───────────────────────────────────────────────── */

function barraReparto(reparto) {
  return `<div class="hoja-barra">${reparto.map(r => `
    <div class="hoja-tramo" style="flex:${r.pct};--color-area:var(--${r.area})">
      <span class="pc">${r.pct}%</span>
      <span class="nb">${escapar(r.nombre)}</span>
      <span class="np">${r.preguntas} preg.</span>
    </div>`).join('')}</div>`;
}

function fichaPatron(t) {
  const e = ESTADOS[t.estado_d1] || SIN_EVALUAR;
  return `
    <article class="hoja-patron ${e.clase}" id="hoja-${escapar(t.patron)}">
      <header>
        <span class="num">${escapar(t.patron)}</span>
        <div class="cab">
          <h3>${mate(t.titulo)}</h3>
          <p class="meta">
            <span class="area" style="--color-area:var(--${t.area})">${escapar(nombreArea(t.area))}</span>
            <span class="sem">${escapar(t.semana || '')}</span>
            <span class="estado">${e.texto}</span>
          </p>
        </div>
      </header>
      <p class="idea">${mate(t.idea)}</p>
      <div class="formula">${renderFormula(t.formula)}</div>
      <div class="hoja-nota">
        <span class="rotulo">Cuándo aparece</span>
        <p>${mate(t.cuando)}</p>
      </div>
      <div class="hoja-nota trampa">
        <span class="rotulo">La trampa</span>
        <p>${mate(t.trampa)}</p>
      </div>
    </article>`;
}

function fichaEcuacion(t) {
  return `
    <article class="hoja-ecuacion">
      <h3>${mate(t.titulo)}</h3>
      <div class="formula">${renderFormula(t.formula)}</div>
      <p class="significa">${mate(t.significa)}</p>
      <p class="hoja-trampilla"><span class="rotulo">Trampa</span> ${mate(t.trampa)}</p>
    </article>`;
}

function fichaDato(t) {
  const filas = String(t.tabla || '').split('\n').map(linea => {
    if (!linea.trim()) return '<tr class="hueco"><td colspan="2"></td></tr>';
    const m = linea.match(/^(.*?)\s{2,}(.+)$/) || linea.match(/^(.*?[:=])\s*(.+)$/);
    if (!m) return `<tr><td colspan="2">${mate(linea)}</td></tr>`;
    return `<tr><td>${mate(m[1].replace(/:$/, ''))}</td><td>${mate(m[2])}</td></tr>`;
  }).join('');

  return `
    <article class="hoja-dato">
      <h3>${mate(t.titulo)}</h3>
      <p class="porque">${mate(t.porque)}</p>
      <table>${filas}</table>
    </article>`;
}

function fichaDescarte(t) {
  const falsas = (t.opciones_falsas || [])
    .map(o => `<li>${mate(o)}</li>`).join('');
  return `
    <article class="hoja-descarte">
      <header>
        <span class="tecnica">${escapar(t.tecnica)}</span>
        ${t.estado_d1 === 'fallado'
          ? '<span class="estado falla">Lo fallaste en el D1</span>' : ''}
      </header>
      <h3>${mate(t.titulo)}</h3>
      <p class="situacion">${mate(t.situacion)}</p>
      <span class="rotulo">Muere por descarte</span>
      <ul class="hoja-falsas">${falsas}</ul>
      <p class="conclusion">${mate(t.conclusion)}</p>
      <p class="hoja-trampilla"><span class="rotulo">La regla</span> ${mate(t.regla)}</p>
    </article>`;
}

function fichasD1(d1) {
  const filas = d1.preguntas.map(p => `
    <div class="hoja-d1-fila ${p.ok ? 'bien' : 'mal'}">
      <div class="linea">
        <span class="n">${p.n}.</span>
        <span class="tema">${mate(p.tema)}</span>
        ${p.patron ? `<span class="pat">${escapar(p.patron)}</span>` : ''}
      </div>
      <div class="linea metricas">
        <span class="resp">marcaste <span class="letra">${escapar(p.tuya)}</span></span>
        <span class="buena">→ ${escapar(p.buena)}</span>
        <span class="t ${p.lento ? 'lento' : ''}">${escapar(p.tiempo)}</span>
        <span class="conf c${p.confianza}">confianza ${p.confianza}</span>
      </div>
      <p class="nota">${mate(p.nota)}</p>
    </div>`).join('');

  const avisos = d1.avisos.map(a => `
    <div class="hoja-aviso">
      <h4>${mate(a.titulo)}</h4>
      <p>${mate(a.texto)}</p>
    </div>`).join('');

  return { filas, avisos };
}

function nombreArea(a) {
  const N = {
    mecanica: 'Mecánica', electromagnetismo: 'Electromagnetismo',
    termo_estadistica: 'Termo y estadística', moderna_cuantica: 'Cuántica y moderna',
    relatividad: 'Relatividad', optica_ondas: 'Óptica y ondas',
    transversal: 'Transversal',
  };
  return N[a] || a || '—';
}

/* ── La vista ─────────────────────────────────────────────── */

export async function pintar() {
  const caja = $('vista-hoja');
  caja.innerHTML = '<div class="cargando">Cargando la hoja…</div>';

  let material, examen;
  try {
    [material, examen] = await Promise.all([
      datos.cargarHoja(), datos.cargarExamen(),
    ]);
  } catch (e) {
    caja.innerHTML = `<p class="vacio">${e.message === 'sin-clave'
      ? 'Necesito la clave para abrir la hoja. Recarga y métela.'
      : 'No pude cargar la hoja de repaso.'}</p>`;
    return;
  }

  const de = tipo => material.filter(t => t.tipo === tipo);
  const patrones = de('patron').sort(
    (a, b) => Number(a.patron.slice(1)) - Number(b.patron.slice(1)));
  const ecuaciones = de('ecuacion');
  const { filas, avisos } = fichasD1(examen.d1);

  const fallados = patrones.filter(p => p.estado_d1 === 'fallado').length;
  const acertados = patrones.filter(p => p.estado_d1 === 'acertado').length;

  const gruposEcuaciones = ORDEN_AREAS.map(a => {
    const suyas = ecuaciones.filter(e => e.area === a);
    if (!suyas.length) return '';
    return `
      <h3 class="hoja-area" style="--color-area:var(--${a})">${nombreArea(a)}</h3>
      ${suyas.map(fichaEcuacion).join('')}`;
  }).join('');

  caja.innerHTML = `
    <div class="cabecera-hoy">
      <div class="fecha">Para el 22 de noviembre por la noche</div>
      <h1>Hoja de repaso</h1>
      <div class="semana">Los diez patrones, las ecuaciones, las constantes y
        las formas de descartar sin calcular</div>
    </div>

    <nav class="hoja-indice" id="hoja-indice">
      ${SECCIONES.map(([id, n]) =>
        `<button type="button" data-ir="hoja-${id}">${n}</button>`).join('')}
    </nav>

    <section id="hoja-reparto">
      <h2 class="seccion">Cómo se reparte el examen</h2>
      ${barraReparto(examen.reparto)}
      <p class="hoja-lectura">Poco más de la mitad se responde con Física 1–2
        bien hecha y rápida: <strong>ahí es donde se aprueba</strong>. El resto
        son patrones de pregrado superior, que no son difíciles <em>si los has
        visto</em> y son imposibles <em>si no</em>.</p>
    </section>

    <section id="hoja-patrones">
      <h2 class="seccion">Los diez patrones</h2>
      <p class="hoja-lectura">Si solo alcanza para repasar diez cosas, son
        estas. El color dice cómo te fue en el diagnóstico:
        <span class="hoja-clave falla">${fallados} fallados</span>
        <span class="hoja-clave acierta">${acertados} acertados</span>
        <span class="hoja-clave virgen">${patrones.length - fallados - acertados} sin evaluar</span>.</p>
      ${patrones.map(fichaPatron).join('')}
    </section>

    <section id="hoja-ecuaciones">
      <h2 class="seccion">Las ecuaciones que sostienen el resto</h2>
      <p class="hoja-lectura">No son los patrones caros: son el 60 % del examen,
        lo que hay que tener automatizado para que sobre tiempo.</p>
      ${gruposEcuaciones}
    </section>

    <section id="hoja-constantes">
      <h2 class="seccion">Constantes, atajos y órdenes de magnitud</h2>
      ${de('dato').map(fichaDato).join('')}
    </section>

    <section id="hoja-descarte">
      <h2 class="seccion">Descartar sin calcular</h2>
      <p class="hoja-lectura">En un examen de opción múltiple sin penalización,
        descartar es tan valioso como resolver y cuesta un cuarto del tiempo.</p>
      ${de('descarte').map(fichaDescarte).join('')}
    </section>

    <section id="hoja-expediente">
      <h2 class="seccion">Tu expediente del D1</h2>
      <p class="hoja-lectura">${examen.d1.aciertos} de ${examen.d1.total}, con
        ${examen.d1.minutos_usados} minutos de ${examen.d1.minutos_disponibles}.
        Salió invertido respecto a lo normal —<strong>${examen.d1.base} en lo
        básico y ${examen.d1.alto} en lo de posgrado</strong>—, y eso importa
        más que el porcentaje: lo caro de construir sigue ahí.</p>
      ${filas}
      ${avisos}
    </section>

    <section id="hoja-protocolo">
      <h2 class="seccion">Protocolo del día</h2>
      <ol class="hoja-protocolo">
        ${examen.protocolo.map(r => `
          <li><h4>${mate(r.titulo)}</h4><p>${mate(r.texto)}</p></li>`).join('')}
      </ol>
    </section>`;

  // El índice se queda pegado bajo la barra superior, que tiene alto variable
  // por el área segura del teléfono: se mide en vez de suponerlo.
  const barra = document.querySelector('.barra-superior');
  if (barra) {
    document.documentElement.style.setProperty(
      '--alto-barra', `${barra.offsetHeight}px`);
  }

  // El índice no puede navegar por href: la app enruta con el hash, así que un
  // "#hoja-patrones" dispararía hashchange y saltaría a la vista Hoy.
  const enlaces = [...caja.querySelectorAll('.hoja-indice button')];
  for (const b of enlaces) {
    b.addEventListener('click', () => {
      const destino = $(b.dataset.ir);
      if (!destino) return;
      const alto = barra ? barra.offsetHeight : 0;
      const y = destino.getBoundingClientRect().top + window.scrollY - alto - 52;
      window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    });
  }

  // Marcar en el índice la sección que se está leyendo.
  const vigia = new IntersectionObserver(entradas => {
    for (const e of entradas) {
      if (!e.isIntersecting) continue;
      for (const b of enlaces) {
        b.classList.toggle('aqui', b.dataset.ir === e.target.id);
      }
    }
  }, { rootMargin: '-25% 0px -70% 0px' });
  caja.querySelectorAll('section').forEach(s => vigia.observe(s));
}
