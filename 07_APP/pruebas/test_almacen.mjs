/* Pruebas del estado que la app guarda en el teléfono.
 *
 * Aquí vivió el peor bug hasta ahora: el progreso del día subía al pintar la
 * tarjeta y no al trabajarla, así que abrir el feed marcaba 6 de 30 sin haber
 * tocado nada. Lo encontró Sebastián, no yo.
 *
 *     node 07_APP/pruebas/test_almacen.mjs
 */

import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const AQUI = dirname(fileURLToPath(import.meta.url));
const ALMACEN = resolve(AQUI, '../../docs/js/almacen.js');

let fallos = 0;
let hechas = 0;

/** Cada prueba arranca con un localStorage limpio y una copia nueva del módulo,
 *  porque el almacén guarda estado en variables de módulo. */
async function prueba(nombre, cuerpo) {
  const memoria = new Map();
  globalThis.localStorage = {
    getItem: k => memoria.get(k) ?? null,
    setItem: (k, v) => memoria.set(k, v),
    removeItem: k => memoria.delete(k),
  };
  const almacen = await import(`${ALMACEN}?p=${hechas++}`);
  try {
    await cuerpo(almacen, memoria);
    console.log(`  ok    ${nombre}`);
  } catch (e) {
    fallos++;
    console.log(`  FALLA ${nombre}`);
    console.log(`        ${e.message.split('\n')[0]}`);
  }
}

await prueba('pintar una tarjeta no suma al progreso', a => {
  for (const id of ['q1', 'q2', 'q3', 'q4', 'q5', 'q6']) a.vista(id);
  assert.equal(a.progresoHoy().n, 0, 'salir en pantalla no es haberla hecho');
  assert.equal(a.racha(), 0);
});

await prueba('responder sí suma y numera', a => {
  const n = a.contar('q1', { codigo: 'HRW 5.41', tipo: 'mc' });
  a.registrarRespuesta({ id: 'q1', area: 'mecanica', ok: true, marcada: 'B', correcta: 'B' });
  assert.equal(n, 1);
  assert.deepEqual(a.progresoHoy(), { n: 1, aciertos: 1 });
});

await prueba('contar dos veces la misma tarjeta no cuenta doble', a => {
  a.contar('q1', { codigo: 'A' });
  a.contar('q1', { codigo: 'A' });
  a.contar('q1', { codigo: 'A' });
  assert.equal(a.progresoHoy().n, 1, 'repintar el historial no debe inflar el día');
  assert.equal(a.ordinalDe('q1'), 1);
});

await prueba('la numeración es el orden en que se trabajaron', a => {
  a.contar('b', { codigo: 'B' });
  a.contar('a', { codigo: 'A' });
  a.contar('c', { codigo: 'C' });
  assert.equal(a.ordinalDe('b'), 1);
  assert.equal(a.ordinalDe('a'), 2);
  assert.equal(a.ordinalDe('c'), 3);
  assert.equal(a.posicionHoy(), 3);
});

await prueba('una tarjeta vista pero no trabajada no recibe número', a => {
  a.vista('q9');
  assert.equal(a.ordinalDe('q9'), null);
  assert.equal(a.fueVista('q9'), true, 'pero no debe volver a salir enseguida');
});

await prueba('la respuesta previa se recupera al repintar', a => {
  a.contar('q1', { codigo: 'A' });
  a.registrarRespuesta({ id: 'q1', area: 'mecanica', ok: false, marcada: 'C', correcta: 'D' });
  const p = a.respuestaPrevia('q1');
  assert.equal(p.marcada, 'C');
  assert.equal(p.correcta, 'D');
  assert.equal(p.ok, false);
});

await prueba('el acierto por área se acumula bien', a => {
  a.registrarRespuesta({ id: '1', area: 'mecanica', ok: true });
  a.registrarRespuesta({ id: '2', area: 'mecanica', ok: false });
  a.registrarRespuesta({ id: '3', area: 'optica_ondas', ok: true });
  const r = a.aciertoPorArea();
  assert.deepEqual(r.mecanica, { n: 2, ok: 1 });
  assert.deepEqual(r.optica_ondas, { n: 1, ok: 1 });
});

await prueba('el traspaso entre aparatos fusiona, no pisa', async (a) => {
  a.contar('q1', { codigo: 'HRW 5.41' });
  a.registrarRespuesta({ id: 'q1', area: 'mecanica', ok: false, marcada: 'C', correcta: 'D' });
  const codigo = a.exportarEstado();

  // Otro aparato, con una respuesta propia distinta.
  const otra = new Map();
  globalThis.localStorage = {
    getItem: k => otra.get(k) ?? null,
    setItem: (k, v) => otra.set(k, v),
    removeItem: k => otra.delete(k),
  };
  const b = await import(`${ALMACEN}?p=traspaso`);
  b.contar('q2', { codigo: 'P2' });
  b.registrarRespuesta({ id: 'q2', area: 'termo_estadistica', ok: true });

  const r = b.importarEstado(codigo);
  assert.equal(r.ok, true);
  assert.equal(b.totales().n, 2, 'se conservan las respuestas de los dos aparatos');
  assert.ok(b.respuestaPrevia('q1'), 'llegó la del otro aparato');
  assert.ok(b.respuestaPrevia('q2'), 'no se perdió la propia');
});

await prueba('un código inválido se rechaza sin romper nada', a => {
  a.contar('q1', { codigo: 'A' });
  const antes = a.totales().n;
  assert.equal(a.importarEstado('hola').ok, false);
  assert.equal(a.importarEstado('').ok, false);
  assert.equal(a.importarEstado('ANDES1:no-es-base64-valido!!').ok, false);
  assert.equal(a.totales().n, antes, 'el estado no debe quedar a medias');
});

await prueba('el repaso espaciado no propone nada recién fallado', a => {
  a.registrarRespuesta({ id: 'q1', area: 'mecanica', ok: false });
  assert.equal(a.pendientesDeRepaso().length, 0, 'lo de hoy toca mañana, no hoy');
  assert.equal(a.enCola(), 1, 'pero queda en la cola');
});

await prueba('una tarjeta fallada vuelve cuando le toca', async a => {
  a.registrarRespuesta({ id: 'q1', area: 'mecanica', ok: false });
  // Se viaja al futuro adelantando la fecha del próximo repaso.
  const st = JSON.parse(localStorage.getItem('andes.v2'));
  st.repaso.q1.proximo = Date.now() - 2 * 86400000;
  localStorage.setItem('andes.v2', JSON.stringify(st));

  const otra = await import(`${ALMACEN}?p=futuro`);
  const p = otra.pendientesDeRepaso();
  assert.equal(p.length, 1);
  assert.equal(p[0].id, 'q1');
  assert.equal(p[0].dias, 2, 'lleva dos días de retraso');
});

await prueba('dos fallos la marcan como hueso', async a => {
  a.registrarRespuesta({ id: 'q1', ok: false });
  a.registrarRespuesta({ id: 'q1', ok: false });
  const st = JSON.parse(localStorage.getItem('andes.v2'));
  assert.equal(st.repaso.q1.fallos, 2);
  st.repaso.q1.proximo = 0;
  localStorage.setItem('andes.v2', JSON.stringify(st));
  const otra = await import(`${ALMACEN}?p=hueso`);
  assert.equal(otra.pendientesDeRepaso()[0].hueso, true);
});

await prueba('dos aciertos seguidos la sacan de la cola', a => {
  a.registrarRespuesta({ id: 'q1', ok: false });
  a.registrarRespuesta({ id: 'q1', ok: true });
  assert.equal(a.enCola(), 1, 'con un acierto todavía no sale');
  a.registrarRespuesta({ id: 'q1', ok: true });
  assert.equal(a.enCola(), 0, 'con el segundo ya está dominada');
});

await prueba('un fallo reinicia la escalera', a => {
  a.registrarRespuesta({ id: 'q1', ok: false });
  a.registrarRespuesta({ id: 'q1', ok: true });
  const antes = JSON.parse(localStorage.getItem('andes.v2')).repaso.q1.seguidos;
  a.registrarRespuesta({ id: 'q1', ok: false });
  const despues = JSON.parse(localStorage.getItem('andes.v2')).repaso.q1.seguidos;
  assert.equal(antes, 1);
  assert.equal(despues, 0, 'volver a fallar vuelve al principio');
});

await prueba('acertar sin haber fallado nunca no crea cola', a => {
  a.registrarRespuesta({ id: 'q1', ok: true });
  assert.equal(a.enCola(), 0);
  assert.equal(a.pendientesDeRepaso().length, 0);
});

await prueba('el tiempo medio solo cuenta lo cronometrado', a => {
  a.registrarRespuesta({ id: 'q1', ok: true, segundos: 60 });
  a.registrarRespuesta({ id: 'q2', ok: true, segundos: 120 });
  a.registrarRespuesta({ id: 'q3', ok: true });          // sin cronómetro
  assert.equal(a.tiempoMedio(), 90);
});

await prueba('las causas del fallo se agrupan', a => {
  a.registrarRespuesta({ id: 'q1', ok: false, causa: 'concepto' });
  a.registrarRespuesta({ id: 'q2', ok: false, causa: 'concepto' });
  a.registrarRespuesta({ id: 'q3', ok: false, causa: 'algebra' });
  a.registrarRespuesta({ id: 'q4', ok: true, causa: 'concepto' });  // acertada: no cuenta
  assert.deepEqual(a.porCausa(), { concepto: 2, algebra: 1 });
});

await prueba('la calibración cruza confianza con acierto', a => {
  a.registrarRespuesta({ id: 'q1', ok: true, confianza: 4 });
  a.registrarRespuesta({ id: 'q2', ok: false, confianza: 4 });
  a.registrarRespuesta({ id: 'q3', ok: false, confianza: 1 });
  const c = a.calibracion();
  assert.deepEqual(c[4], { n: 2, ok: 1 }, 'confianza alta con la mitad fallada');
  assert.deepEqual(c[1], { n: 1, ok: 0 });
});

await prueba('el CSV lleva las columnas del medidor', a => {
  a.registrarRespuesta({ id: 'q1', area: 'mecanica', nivel: 'BASE', ok: false,
                         marcada: 'C', correcta: 'D', segundos: 95,
                         causa: 'concepto', confianza: 3 });
  const csv = a.exportarCSV();
  const [cab, fila] = csv.trim().split('\n');
  assert.equal(cab, 'fecha,id,area,nivel,patron,marcada,correcta,ok,segundos,causa,confianza');
  assert.ok(fila.includes('95'), 'los segundos van en el CSV');
  assert.ok(fila.includes('concepto'));
});

await prueba('las familias servidas hoy se recuerdan', a => {
  a.contar('q1', { codigo: 'HRW 2.1', familia: 'un coche va de a a b' });
  a.contar('q2', { codigo: 'HRW 2.5', familia: 'una masa cuelga de' });
  a.contar('q3', { codigo: 'P2' });
  assert.deepEqual(a.familiasDeHoy().sort(),
    ['un coche va de a a b', 'una masa cuelga de'],
    'las tarjetas sin familia no cuentan');
});

await prueba('la meta diaria se acota a un rango sensato', a => {
  a.fijarMeta(0);
  assert.ok(a.metaDiaria() >= 5);
  a.fijarMeta(99999);
  assert.ok(a.metaDiaria() <= 200);
});

console.log();
if (fallos) {
  console.log(`${fallos} prueba(s) fallaron`);
  process.exit(1);
}
console.log(`${hechas} pruebas en verde`);
