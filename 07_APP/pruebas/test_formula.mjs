/* Prosa con matemáticas intercaladas, que es como quedan las notas de la Hoja.
 *
 * «Permite que lo que yo escriba se compile, es decir, que yo use expresiones
 * como \beta y salga el símbolo, de resto será muy difícil usar las notas.»
 * — reporte del 20 de septiembre.
 *
 *     node 07_APP/pruebas/test_formula.mjs
 */

import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = resolve(AQUI, '../../docs/js');

// KaTeX de mentira: devuelve el LaTeX marcado, para poder afirmar qué tramo
// fue por matemáticas y cuál por prosa sin cargar 300 kB de fuentes.
globalThis.window = { katex: { renderToString: (l) => `<katex>${l}</katex>` } };

const { renderMixto } = await import(`${RAIZ}/formula.js`);
const { mate } = await import(`${RAIZ}/mate.js`);

let fallos = 0;
function prueba(nombre, cuerpo) {
  try { cuerpo(); console.log(`  ok    ${nombre}`); }
  catch (e) { fallos++; console.log(`  FALLA ${nombre}\n        ${e.message.split('\n')[0]}`); }
}

prueba('una letra griega suelta no necesita dólares', () => {
  assert.equal(renderMixto('el ángulo \\beta crece', mate), 'el ángulo β crece');
});

prueba('lo que va entre dólares pasa por KaTeX', () => {
  const r = renderMixto('queda $\\frac{a}{b}$ al final', mate);
  assert.ok(r.includes('<katex>\\frac{a}{b}</katex>'));
  assert.ok(r.startsWith('queda '));
  assert.ok(r.endsWith(' al final'));
});

prueba('prosa y fórmula se mezclan en la misma nota', () => {
  const r = renderMixto('con \\gamma pequeño, $\\omega_d=\\sqrt{\\omega^2-2\\gamma^2}$', mate);
  assert.ok(r.includes('γ pequeño'), 'la prosa usa la tabla de símbolos');
  assert.ok(r.includes('<katex>'), 'la fórmula usa KaTeX');
});

prueba('dos fórmulas en una misma nota', () => {
  const r = renderMixto('$E=mc^2$ y también $p=mv$', mate);
  assert.equal((r.match(/<katex>/g) || []).length, 2);
});

prueba('el texto sin matemáticas sigue escapándose', () => {
  assert.ok(renderMixto('5 < 7 & listo', mate).includes('&lt;'));
});

prueba('un dólar suelto no rompe la nota', () => {
  const r = renderMixto('cuesta 5$ el metro', mate);
  assert.ok(r.includes('cuesta 5'));
  assert.ok(!r.includes('<katex>'));
});

prueba('el exponente corto sigue funcionando fuera de los dólares', () => {
  assert.ok(renderMixto('va como r^2', mate).includes('<sup>2</sup>'));
});

console.log();
if (fallos) { console.log(`${fallos} prueba(s) fallaron`); process.exit(1); }
console.log('7 pruebas en verde');
