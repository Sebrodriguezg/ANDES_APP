/* Renderizado de fórmulas con KaTeX.

   La primera versión pintaba las fórmulas en monoespaciada con <sup> y <sub>.
   Servía para un exponente suelto dentro de una frase, pero una ecuación de
   verdad —una integral, una fracción, un sumatorio— quedaba ilegible. Para eso
   hace falta tipografía matemática de verdad.

   KaTeX va incrustado en vendor/, con sus fuentes: la app tiene que funcionar
   sin datos, y depender de un CDN rompería eso. */

const OPCIONES = {
  throwOnError: false,
  errorColor: '#FF4F9A',
  strict: false,
  trust: false,
  output: 'html',
};

function disponible() {
  return typeof window !== 'undefined' && typeof window.katex !== 'undefined';
}

/** Una línea de LaTeX como bloque centrado. */
export function renderBloque(latex) {
  if (!disponible()) return `<pre class="formula-cruda">${latex}</pre>`;
  try {
    return window.katex.renderToString(latex, { ...OPCIONES, displayMode: true });
  } catch {
    return `<pre class="formula-cruda">${latex}</pre>`;
  }
}

/** LaTeX dentro de una frase. */
export function renderEnLinea(latex) {
  if (!disponible()) return latex;
  try {
    return window.katex.renderToString(latex, { ...OPCIONES, displayMode: false });
  } catch {
    return latex;
  }
}

/** Bloque de fórmula de una tarjeta.
 *
 *  El contenido autoral trae `formula` como lista de renglones. Cada renglón es
 *  o LaTeX, o un rótulo de texto que separa grupos ("Gauge de Lorenz:"). Se
 *  distinguen por un prefijo: los rótulos empiezan por '#'.
 */
export function renderFormula(formula) {
  const renglones = Array.isArray(formula) ? formula : String(formula ?? '').split('\n');

  return renglones.map(linea => {
    const texto = String(linea).trim();
    if (!texto) return '<div class="hueco-formula"></div>';
    if (texto.startsWith('#')) {
      return `<div class="rotulo-formula">${escaparTexto(texto.slice(1).trim())}</div>`;
    }
    return `<div class="renglon-formula">${renderBloque(texto)}</div>`;
  }).join('');
}

const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const escaparTexto = t => String(t).replace(/[&<>"']/g, c => ESCAPES[c]);
