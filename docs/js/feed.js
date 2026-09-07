/* Motor del feed: elige qué tarjeta viene, la pinta y carga más al llegar al fondo.

   No es aleatorio puro. La selección pondera hacia tus áreas flojas y hacia la semana
   del cronograma en la que estés — la gracia es que el scroll haga trabajo útil. */

import * as datos from './datos.js';
import * as almacen from './almacen.js';
import { construir, tarjetaCierre, tarjetaReanudar, pintarOrdinal } from './tarjetas.js';

const POR_LOTE = 6;
// Atraso a partir del cual el repaso ocupa la mitad del lote en vez de un tercio.
const ATRASO_GRANDE = 30;

let cola = [];
let indiceTanda = 0;
let semanaActual = null;
let cerrado = false;
let observador = null;
let observadorLectura = null;
// Ids que hoy tocan por repaso, con su ficha. El feed los sirve primero.
let repasoPendiente = new Map();
// Familias ya servidas hoy. El banco de HRW repite el mismo planteamiento
// cambiando un número: 90 familias con más de una variante. Verlas seguidas
// confunde, porque parecen la misma pregunta con distinta respuesta.
let familiasServidas = new Set();

// Las tarjetas que no se responden —patrón, ecuación, dato, descarte, tu error—
// cuentan para la meta cuando han estado de verdad en pantalla. Sin esto no
// habría forma de completar el día leyendo, y con contarlas al pintarlas el
// progreso se llenaba solo.
const TIPOS_DE_LECTURA = new Set(['patron', 'ecuacion', 'dato', 'descarte', 'error', 'micro']);
const SEGUNDOS_PARA_CONTAR = 1200;

function vigilarLectura(nodo, tarjeta, alContar) {
  if (!TIPOS_DE_LECTURA.has(tarjeta.tipo)) return;

  observadorLectura ??= new IntersectionObserver(entradas => {
    for (const e of entradas) {
      const nodo = e.target;
      if (e.isIntersecting) {
        // Pasar de largo con el pulgar no cuenta como haberla leído.
        nodo._temporizador = setTimeout(() => {
          const t = nodo._tarjeta;
          const n = almacen.contar(t.id, { codigo: t.codigo, tipo: t.tipo, familia: t.familia });
          pintarOrdinal(nodo, n);
          observadorLectura.unobserve(nodo);
          nodo._alContar?.();
        }, SEGUNDOS_PARA_CONTAR);
      } else {
        clearTimeout(nodo._temporizador);
      }
    }
  }, { threshold: 0.55 });

  nodo._tarjeta = tarjeta;
  nodo._alContar = alContar;
  observadorLectura.observe(nodo);
}

/** Peso de una tarjeta: cuánto conviene mostrarla ahora. */
function peso(t, flojas) {
  let p = 1;

  // Lo que aún no has visto va primero.
  if (almacen.fueVista(t.id)) p *= 0.12;

  // Las áreas donde vas peor pesan más: ahí están los puntos baratos.
  const rendimiento = flojas[t.area];
  if (rendimiento && rendimiento.n >= 4) {
    p *= 1 + 1.6 * (1 - rendimiento.ok / rendimiento.n);
  }

  // El tema de la semana en curso, al frente.
  if (semanaActual && t.semana === semanaActual.id) p *= 2.2;

  // No todas las tarjetas rinden igual. Tus propios errores son lo más valioso
  // que hay; después los patrones y las técnicas de descarte, que son lo que
  // convierte tiempo de scroll en puntos el 23 de noviembre.
  const PESO_TIPO = {
    error: 4, patron: 3.5, descarte: 3, ecuacion: 2.5, micro: 2.2, dato: 2, mc: 1,
  };
  p *= PESO_TIPO[t.tipo] ?? 1;

  // Una variante de algo que ya salió hoy se hunde: que aparezcan seguidas
  // parece un error de la app, no una pregunta distinta.
  if (t.familia && familiasServidas.has(t.familia)) p *= 0.05;

  // Lo que toca repasar manda sobre todo lo demás: una pregunta que ya fallaste
  // y vuelve en su momento vale más que cualquier pregunta nueva.
  if (repasoPendiente.has(t.id)) {
    p *= repasoPendiente.get(t.id).hueso ? 12 : 8;
  }

  return p;
}

function elegir(candidatos, cuantos) {
  const flojas = almacen.aciertoPorArea();
  const pesados = candidatos.map(t => ({ t, p: peso(t, flojas) }));
  const salida = [];

  for (let i = 0; i < cuantos && pesados.length; i++) {
    const total = pesados.reduce((s, x) => s + x.p, 0);
    let r = Math.random() * total;
    let k = 0;
    while (k < pesados.length - 1 && (r -= pesados[k].p) > 0) k++;
    salida.push(pesados[k].t);
    pesados.splice(k, 1);
  }
  return salida;
}

/* El repaso espaciado solo servía de adorno: se calculaba qué tocaba y se
   pintaba un número en la pestaña Yo, sin que el feed lo sirviera nunca. Aquí
   se traen esas tarjetas y se marcan para que salgan las primeras. */
async function cargarRepaso() {
  const pendientes = almacen.pendientesDeRepaso();
  repasoPendiente = new Map(pendientes.map(p => [p.id, p]));
  if (!pendientes.length) return [];

  const tarjetas = await datos.buscarPorIds(pendientes.map(p => p.id));
  for (const t of tarjetas) t.repaso = repasoPendiente.get(t.id);
  return tarjetas;
}

/* Cuántas de la cola no son repaso. Contar la cola entera era el bug: con 50
   preguntas pendientes de repasar la cola nunca bajaba del mínimo, así que no
   se cargaba ninguna tanda nueva y el feed servía repaso hasta agotarlo. */
export function cuantasNuevas(lista, pendientes = repasoPendiente) {
  let n = 0;
  for (const t of lista) if (!pendientes.has(t.id)) n++;
  return n;
}

/** Cupos de repaso en un lote. Nunca el lote entero: siempre entra algo nuevo. */
export function cupoDeRepaso(pendientes, cuantos) {
  const proporcion = pendientes > ATRASO_GRANDE ? 0.5 : 1 / 3;
  return Math.max(0, Math.min(Math.round(cuantos * proporcion), pendientes, cuantos - 1));
}

/** Mezcla las dos listas repartiéndolas parejo, para que el repaso no salga en bloque. */
export function intercalar(repaso, nuevas) {
  if (!repaso.length) return [...nuevas];
  if (!nuevas.length) return [...repaso];
  const salida = [];
  let r = 0, n = 0;
  while (r < repaso.length || n < nuevas.length) {
    // Sirve del lado que va más atrasado respecto a su propia proporción.
    const tocaRepaso = (r + 0.5) / repaso.length <= (n + 0.5) / nuevas.length;
    if (tocaRepaso && r < repaso.length) salida.push(repaso[r++]);
    else if (n < nuevas.length) salida.push(nuevas[n++]);
    else salida.push(repaso[r++]);
  }
  return salida;
}

/* Arma un lote con cupo reservado para cada lado. Si un lado se queda corto
   —no hay repaso pendiente, o se agotó el corpus— el otro completa el lote.
   `tomar` se inyecta para poder probarlo sin el sorteo ponderado. */
export function componerLote(pendientes, nuevas, cuantos, tomar) {
  const deRepaso = tomar(pendientes, cupoDeRepaso(pendientes.length, cuantos));
  const deNuevas = tomar(nuevas, cuantos - deRepaso.length);

  const faltan = cuantos - deRepaso.length - deNuevas.length;
  if (faltan > 0) {
    const ya = new Set([...deRepaso, ...deNuevas].map(t => t.id));
    const resto = [...pendientes, ...nuevas].filter(t => !ya.has(t.id));
    deRepaso.push(...tomar(resto, faltan));
  }
  return intercalar(deRepaso, deNuevas);
}

async function asegurarCola(minimo) {
  while (cuantasNuevas(cola) < minimo && indiceTanda < datos.numeroDeTandas()) {
    try {
      const tanda = await datos.cargarTanda(indiceTanda++);
      cola.push(...tanda);
    } catch (e) {
      if (e.message === 'sin-clave') throw e;
      // Una tanda que no llega no debe tumbar el feed: se sigue con las demás.
      console.warn('tanda ilegible, sigo con la siguiente', e);
    }
  }
  // Si se agotó el corpus, se vuelve a empezar: lo visto reaparece con poco peso,
  // así que en la práctica salen primero las falladas y las que quedaron sin ver.
  if (!cuantasNuevas(cola) && datos.numeroDeTandas()) {
    indiceTanda = 0;
    cola.push(...await datos.cargarTanda(indiceTanda++));
  }
}

function progreso() {
  const { n, aciertos } = almacen.progresoHoy();
  const meta = almacen.metaDiaria();
  const barra = document.getElementById('barra-meta');
  if (barra) barra.style.width = `${Math.min(100, 100 * n / meta)}%`;

  const conteo = document.getElementById('progreso-conteo');
  if (conteo) conteo.textContent = `${n} / ${meta}`;

  const acierto = document.getElementById('progreso-acierto');
  if (acierto) {
    acierto.textContent = n ? `${Math.round(100 * aciertos / n)}% de acierto` : '';
  }
  return { n, aciertos, meta };
}

async function pintarLote() {
  const contenedor = document.getElementById('feed');
  if (!contenedor) return;

  const { n, aciertos, meta } = progreso();
  if (!cerrado && n >= meta) {
    cerrado = true;
    contenedor.append(tarjetaCierre({
      n, aciertos,
      alSeguir: () => { pintarLote(); },
    }));
    return;
  }

  try {
    await asegurarCola(POR_LOTE * 4);
  } catch (e) {
    if (e.message === 'sin-clave' && !contenedor.querySelector('.vacio')) {
      contenedor.innerHTML =
        '<p class="vacio">El contenido está cifrado y falta la clave.<br>' +
        'Recarga la página para volver a escribirla.</p>';
    }
    return;
  }

  const pendientes = cola.filter(t => repasoPendiente.has(t.id));
  const nuevas = cola.filter(t => !repasoPendiente.has(t.id));
  const elegidas = componerLote(pendientes, nuevas, POR_LOTE, elegir);

  for (const t of elegidas) {
    cola = cola.filter(x => x.id !== t.id);
    almacen.vista(t.id);
    if (t.familia) familiasServidas.add(t.familia);
    const nodo = construir(t, () => progreso());
    if (!nodo) continue;
    contenedor.append(nodo);
    vigilarLectura(nodo, t, () => progreso());
  }
  progreso();
}

function cabeceraRepaso(n) {
  const nodo = document.createElement('div');
  nodo.className = 'cabecera-repaso';
  nodo.innerHTML = `
    <span class="rotulo">Hoy toca repasar</span>
    <span class="cuenta">${n} ${n === 1 ? 'pregunta' : 'preguntas'} que fallaste, intercaladas con las nuevas</span>`;
  return nodo;
}

/** Si ya habías avanzado hoy, el feed abre diciendo por dónde ibas. */
async function restaurarSesion(contenedor) {
  const historial = almacen.historialHoy();
  if (!historial.length) return;

  const { n, aciertos } = almacen.progresoHoy();

  contenedor.append(tarjetaReanudar({
    n, aciertos,
    meta: almacen.metaDiaria(),
    ultimo: historial.at(-1)?.codigo || '',
    alVerAnteriores: async () => {
      const tarjetas = await datos.buscarPorIds(historial.map(h => h.id));
      const fragmento = document.createDocumentFragment();
      for (const t of tarjetas) {
        const nodo = construir(t, null);
        if (nodo) fragmento.append(nodo);
      }
      // Se insertan arriba, en el orden en que salieron.
      contenedor.prepend(fragmento);
    },
  }));
}

export async function iniciar(crono) {
  semanaActual = datos.semanaDe(crono);
  await datos.cargarManifiesto();

  const contenedor = document.getElementById('feed');
  contenedor.innerHTML = '';
  cola = [];
  indiceTanda = 0;
  cerrado = false;
  familiasServidas = new Set(almacen.familiasDeHoy());
  observadorLectura?.disconnect();
  observadorLectura = null;

  await restaurarSesion(contenedor);

  // El repaso encabeza la cola, antes de traer nada nuevo.
  const aRepasar = await cargarRepaso();
  if (aRepasar.length) {
    cola.unshift(...aRepasar);
    contenedor.append(cabeceraRepaso(aRepasar.length));
  }

  await pintarLote();

  const centinela = document.getElementById('centinela');
  observador?.disconnect();
  observador = new IntersectionObserver(entradas => {
    if (entradas.some(e => e.isIntersecting)) pintarLote();
  }, { rootMargin: '400px' });
  observador.observe(centinela);
}

export function refrescarProgreso() { progreso(); }
