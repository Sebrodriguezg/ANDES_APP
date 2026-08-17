/* Renderizador de notación matemática, mínimo y sin dependencias.

   El corpus sale del extractor con exponentes y subíndices en notación de llaves
   —10^{-9}, m/s^{2}, x_{i}— porque es lo que se puede reconstruir con fiabilidad
   desde la geometría del PDF. Aquí se convierte a <sup> y <sub>.

   No hace falta KaTeX: son 300 kB y fuentes propias para cubrir un caso que estas
   veinte líneas resuelven. Si algún día el contenido autoral necesita matrices o
   integrales de verdad, se reevalúa. */

const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

export function escapar(texto) {
  return String(texto ?? '').replace(/[&<>"']/g, c => ESCAPES[c]);
}

const SIMBOLOS = [
  [/\\times/g, '×'],
  [/\\cdot/g, '·'],
  [/\\pm/g, '±'],
  [/\\approx/g, '≈'],
  [/\\neq/g, '≠'],
  [/\\leq/g, '≤'],
  [/\\geq/g, '≥'],
  [/\\infty/g, '∞'],
  [/\\hbar/g, 'ℏ'],
  [/\\alpha/g, 'α'], [/\\beta/g, 'β'], [/\\gamma/g, 'γ'], [/\\delta/g, 'δ'],
  [/\\epsilon/g, 'ε'], [/\\theta/g, 'θ'], [/\\lambda/g, 'λ'], [/\\mu/g, 'μ'],
  [/\\pi/g, 'π'], [/\\rho/g, 'ρ'], [/\\sigma/g, 'σ'], [/\\tau/g, 'τ'],
  [/\\phi/g, 'φ'], [/\\omega/g, 'ω'], [/\\Omega/g, 'Ω'], [/\\Delta/g, 'Δ'],
];

/** Devuelve HTML seguro: escapa primero, sustituye después. */
export function mate(texto) {
  let s = escapar(texto);
  for (const [re, ch] of SIMBOLOS) s = s.replace(re, ch);
  // Los índices pueden anidar una vez (x_{i}^{2}), pero no más: basta con repetir.
  for (let i = 0; i < 2; i++) {
    s = s.replace(/\^\{([^{}]*)\}/g, '<sup>$1</sup>')
         .replace(/_\{([^{}]*)\}/g, '<sub>$1</sub>');
  }
  // Forma corta sin llaves: x^2, v_0, K_rot, I_cm.
  // Toma hasta tres caracteres, no uno: con uno solo "K_rot" salía como K con
  // la r debajo y "ot" al lado. El tope de tres y el lookahead evitan que se
  // coma cosas como "03_TEMARIO" cuando aparecen en prosa.
  s = s.replace(/\^([+-]?[\p{L}\d]{1,3})(?![\p{L}\d])/gu, '<sup>$1</sup>')
       .replace(/_([+-]?[\p{L}\d]{1,3})(?![\p{L}\d])/gu, '<sub>$1</sub>');
  // Énfasis al estilo Markdown, que es como está escrito el contenido autoral.
  // Sin esto los asteriscos salían crudos: "el nivel *degenerado* más bajo".
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
       .replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s.,;:)]|$)/g, '$1<em>$2</em>');
  return s;
}
