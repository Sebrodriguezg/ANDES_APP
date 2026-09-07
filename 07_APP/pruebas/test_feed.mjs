/* Pruebas del reparto del feed.
 *
 * El bug: con 50 preguntas pendientes de repaso, `asegurarCola` contaba la cola
 * entera contra el mínimo, así que nunca cargaba una tanda nueva y el feed
 * servía 20–40 repasos seguidos antes de que apareciera una pregunta nueva.
 * Lo encontró Sebastián estudiando, no yo leyendo el código.
 *
 *     node 07_APP/pruebas/test_feed.mjs
 */

import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const AQUI = dirname(fileURLToPath(import.meta.url));
const FEED = resolve(AQUI, '../../docs/js/feed.js');

const memoria = new Map();
globalThis.localStorage = {
  getItem: k => memoria.get(k) ?? null,
  setItem: (k, v) => memoria.set(k, v),
  removeItem: k => memoria.delete(k),
};

const feed = await import(FEED);

let fallos = 0;
function prueba(nombre, cuerpo) {
  try {
    cuerpo();
    console.log(`  ok    ${nombre}`);
  } catch (e) {
    fallos++;
    console.log(`  FALLA ${nombre}`);
    console.log(`        ${e.message.split('\n')[0]}`);
  }
}

/** Toma las primeras `n`, sin sorteo: así el reparto se puede afirmar. */
const tomar = (lista, n) => lista.slice(0, Math.max(0, n));
const hacer = (prefijo, n) =>
  Array.from({ length: n }, (_, i) => ({ id: `${prefijo}${i}` }));
const esRepaso = t => t.id.startsWith('r');

prueba('la cola cuenta como nuevas solo las que no son repaso', () => {
  const pendientes = new Map([['r0', {}], ['r1', {}]]);
  const cola = [...hacer('r', 2), ...hacer('n', 3)];
  assert.equal(feed.cuantasNuevas(cola, pendientes), 3);
});

prueba('el cupo de repaso nunca se come el lote entero', () => {
  assert.equal(feed.cupoDeRepaso(50, 6), 3, 'con atraso grande, la mitad');
  assert.equal(feed.cupoDeRepaso(10, 6), 2, 'sin atraso grande, un tercio');
  assert.equal(feed.cupoDeRepaso(1, 6), 1, 'no inventa repaso que no hay');
  assert.equal(feed.cupoDeRepaso(0, 6), 0);
  assert.equal(feed.cupoDeRepaso(99, 1), 0, 'un lote de uno trae pregunta nueva');
});

prueba('un lote con 50 repasos pendientes trae preguntas nuevas', () => {
  const lote = feed.componerLote(hacer('r', 50), hacer('n', 24), 6, tomar);
  assert.equal(lote.length, 6);
  assert.equal(lote.filter(esRepaso).length, 3);
  assert.equal(lote.filter(t => !esRepaso(t)).length, 3);
});

prueba('el repaso no sale en bloque', () => {
  const lote = feed.componerLote(hacer('r', 50), hacer('n', 24), 6, tomar);
  const seguidas = lote.reduce(
    (max, t, i) => (esRepaso(t) && i && esRepaso(lote[i - 1]) ? max + 1 : max), 0);
  assert.ok(seguidas <= 1, `salieron ${seguidas + 1} repasos seguidos: ${lote.map(t => t.id)}`);
});

prueba('sin repaso pendiente el lote es todo nuevo', () => {
  const lote = feed.componerLote([], hacer('n', 24), 6, tomar);
  assert.equal(lote.length, 6);
  assert.equal(lote.filter(esRepaso).length, 0);
});

prueba('agotado el corpus, el repaso completa el lote', () => {
  const lote = feed.componerLote(hacer('r', 50), [], 6, tomar);
  assert.equal(lote.length, 6, 'el feed no se queda corto');
  assert.equal(new Set(lote.map(t => t.id)).size, 6, 'sin repetir tarjeta en el mismo lote');
});

prueba('con poco de todo, el lote no repite ni se pasa', () => {
  const lote = feed.componerLote(hacer('r', 2), hacer('n', 2), 6, tomar);
  assert.equal(lote.length, 4);
  assert.equal(new Set(lote.map(t => t.id)).size, 4);
});

prueba('intercalar reparte parejo y conserva todo', () => {
  const salida = feed.intercalar(hacer('r', 2), hacer('n', 4));
  assert.equal(salida.length, 6);
  assert.ok(!esRepaso(salida[0]), 'el feed abre con algo nuevo');
  assert.deepEqual(salida.filter(esRepaso).map(t => t.id), ['r0', 'r1']);
});

console.log();
if (fallos) {
  console.log(`${fallos} prueba(s) fallaron`);
  process.exit(1);
}
console.log('8 pruebas en verde');
