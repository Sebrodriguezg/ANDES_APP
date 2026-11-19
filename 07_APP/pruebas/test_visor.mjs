// Qué simulación ofrece cada tarjeta del feed. Casos tomados del corpus real.
import { simulacionesPara, htmlAccesos } from '../../docs/js/visor.js';

let fallos = 0;
function caso(nombre, t, esperado) {
  const r = simulacionesPara(t).join(',');
  const ok = r === esperado.join(',');
  console.log(`  ${ok ? 'ok   ' : 'FALLA'} ${nombre}${ok ? '' : `  → [${r}], esperaba [${esperado}]`}`);
  if (!ok) fallos++;
}

caso('relojes en movimiento', { area: 'relatividad', etiquetas: ['dilatacion'],
  enunciado: "A consequence of Einstein's theory of relativity is:",
  opciones: { A: 'moving clocks run more slowly than when they are at rest', B: 'moving rods are longer' } },
  ['dilatacion', 'contraccion']);
caso('vida del muón', { area: 'relatividad', enunciado: 'The mean lifetime of a muon at rest is 2.2 μs…', opciones: {} },
  ['dilatacion']);
caso('Doppler relativista', { area: 'relatividad', etiquetas: ['doppler'],
  enunciado: 'A galaxy recedes; the wavelength observed is…', opciones: {} }, ['doppler']);
caso('"longitud de onda" no es contracción', { area: 'relatividad',
  enunciado: 'Un átomo se acerca a una fuente que emite fotones de longitud de onda 400 nm', opciones: {} }, ['doppler']);
caso('relatividad sin pista: las dos', { area: 'relatividad', enunciado: 'Which postulate…', opciones: {} },
  ['dilatacion', 'contraccion']);
caso('imagen en plano a tierra', { area: 'electromagnetismo',
  enunciado: 'A point charge q is brought to a distance d from a grounded conducting plane.', opciones: {} }, ['imagenes']);
caso('plano infinito', { area: 'electromagnetismo', enunciado: 'An infinite sheet of charge…', opciones: {} }, ['borde']);
caso('adiabática', { area: 'termo_estadistica', enunciado: 'An ideal gas expands adiabatically', opciones: {} }, ['adiabatica']);
caso('Doppler acústico: nada', { area: 'optica_ondas', etiquetas: ['doppler'],
  enunciado: 'A siren approaches at 30 m/s; the sound frequency heard is', opciones: {} }, []);
caso('viaje a una estrella', { area: 'relatividad', enunciado: 'A spaceship travels to a star 4 light-years away at 0.8c. How long does the trip take according to the astronaut clock?', opciones: {} },
  ['nave', 'dilatacion', 'contraccion']);
caso('escalón', { area: 'moderna_cuantica', enunciado: 'Electrons incident on a potential step of height V0…', opciones: {} }, ['escalon']);
caso('bosones en una caja', { area: 'moderna_cuantica', enunciado: 'Two identical bosons in a 2D box…', opciones: {} }, ['caja']);
caso('oscilador', { area: 'moderna_cuantica', enunciado: 'For a quantum harmonic oscillator in a superposition…', opciones: {} }, ['oscilador']);
caso('mecánica: nada', { area: 'mecanica', enunciado: 'A block slides down an incline', opciones: {} }, []);

if (htmlAccesos({ area: 'mecanica', enunciado: 'x' }) !== '') { console.log('  FALLA tarjeta sin simulación pinta botones'); fallos++; }
else console.log('  ok    tarjeta sin simulación no pinta nada');

if (fallos) { console.log(`${fallos} fallos`); process.exit(1); }
