# Diagnóstico D1 — resultados y análisis

**14 de agosto de 2026.** 12 preguntas, 44,5 minutos usados de 60.
**Resultado: 2 / 12 (16,7 %).**

> Sobre las respuestas correctas: el Departamento no publica la clave, así que las derivé yo.
> En cada pregunta digo qué tan seguro estoy. Dos tienen una salvedad real y están marcadas.

---

## Pregunta por pregunta

| # | Tema | Tu resp. | Correcta | | Tiempo | Seg. | Qué pasó |
|---|---|---|---|---|---|---|---|
| 1 | Rizo con resorte | c | **d** | ✗ | 5:31 | 3 | Sacaste bien `v² = gR` en el tope. Luego igualaste ½kx² = ½mv² y **te faltó la energía potencial de subir 2R**. Con ella: ½kx² = ½mv² + mg(2R) → x = 5 m |
| 2 | Bloques A/B/C con fricción | d | **c** | ✗ | **14:42** | 2 | La fricción entre A y B es **interna** al sistema A+B: no va en la ecuación global. La condición es a = μ_s·g, y del sistema a = m_C·g/(m_A+m_B+m_C). Sale m_C = μ_s/(1−μ_s)·(m_A+m_B) |
| 3 | **P1** Espacio de fase | a | **a** | ✅ | 1:47 | 3 | Correcta, y en menos de 2 minutos |
| 4 | **P2** Corchetes de Poisson | c | **a** ⚠️ | ✗ | 0:43 | 1 | Adivinaste. {l_i, q_k} ∝ q, así que solo *a* tiene la estructura posible |
| 5 | Ampère, cilindro hueco | d | **e** | ✗ | 6:24 | 2 | Ibas bien con límites. La prueba que decide: en r = b debe dar μ₀I/2πb. Solo *e* lo cumple; *d* tiene b² en vez de b²−a² |
| 6 | Dilatación temporal | d | **b** | ✗ | 7:45 | 2 | **Física correcta, matemática fallida.** γ ≈ 1 + β²/2. Te comiste el ½ y por eso te dio 8 en vez de 4 |
| 7 | **P5** Esfera a tierra en campo E | b | **b** | ✅ | 2:37 | 4 | Correcta, rápida y con confianza. Aplicaste Φ(a)=0 exactamente como toca |
| 8 | Potencial esfera + cascarón | d | **c** ⚠️ | ✗ | 2:06 | 4 | ΔV = ∫E·dr = kQ(1/a − 1/b). Solo *c* tiene esa estructura |
| 9 | Calorimetría, espada | e | **d** | ✗ | 1:28 | 1 | 10·0,470·1270 = 5969 kJ del hierro; m·4,190·80 + 2·2300 del agua → m = 4,1 kg |
| 10 | **P7** Contacto térmico | c | **b** | ✗ | 1:00 | 1 | Maximizar Ω_A·Ω_B con Ω ∝ E^n da reparto proporcional a los exponentes: E_A = 10⁶/(10⁶+10²⁴)·E_T |
| 11 | **P8** Dos bosones en caja 2D | c | **e** | ✗ | 2:00 | 1 | El nivel *degenerado* más bajo es 25π²ℏ²/8mL², donde coinciden {(1,1),(1,4)}, {(1,1),(2,2)} y {(1,2),(2,1)} |
| 12 | **P9** Escalón de potencial | d | **b** | ✗ | 0:30 | 1 | E = 9V₀/8 → k₁/k₂ = 3 → R = ((3−1)/(3+1))² = 1/4 |

### Las dos salvedades

- **Pregunta 4 (Poisson).** La derivación estándar da {l_i, q_k} = ε_ikm q_m. La opción *a* está escrita ε_imk q_m, que es el negativo. Es casi seguro una errata del examen o una convención de signo distinta, pero *a* es la única opción estructuralmente posible: *b* es cero, *c* tiene l_m y *d* tiene p_j. En el examen real marcarías *a*.
- **Pregunta 8 (potencial).** El enunciado no dice en qué sentido toma la diferencia, así que podría ser kQ(1/a − 1/b) o su negativo. La opción *c* es la única con esa estructura.

---

## Lo que dicen los números

| Corte | Resultado |
|---|---|
| **BASE** (Física 1–2) | **0 / 6** |
| **ALTO** (patrones de posgrado) | **2 / 6** |
| Mecánica | 1/4 |
| Electromagnetismo | 1/3 |
| Relatividad · Termo/Estadística · Moderna/Cuántica | 0/1 · 0/2 · 0/2 |
| Causa de los fallos | 9 concepto · 1 álgebra |
| Tiempo | 44,5 min de 60 — pero **14,4 min en una sola pregunta** |

---

## La lectura

**El resultado está invertido respecto a lo normal, y eso importa más que el 16,7 %.**

Lo esperable en alguien que lleva tiempo sin ver esto es acertar la base y fallar los patrones.
A ti te pasó al revés: **0/6 en lo básico y 2/6 en lo de posgrado**, incluyendo la esfera conductora
a tierra en campo uniforme —un problema de Griffiths §3.3.2— resuelto en 2 minutos y medio con confianza 4.
Eso no se improvisa. Ese conocimiento sigue ahí.

**Y los fallos de base no son ignorancia, son óxido.** Mira el patrón:

- En la 1 sacaste bien la condición del rizo y se te quedó un término de energía.
- En la 6 sabías que era dilatación temporal y que había que expandir; falló el ½ de la expansión binomial.
- En la 5 estabas verificando límites, que es exactamente la técnica correcta.
- En la 8 razonaste que el potencial baja con la distancia.

Eso es distinto de la 9, la 10, la 11 y la 12, donde escribiste «no sé nada». **Termodinámica, estadística
y cuántica están en cero de verdad**, y ahí sí hay que construir desde el principio. Pero esas semanas
ya están en el cronograma (9 a 12) y no había por qué esperar otra cosa hoy.

**Esto es una buena noticia estructural para un plan de 14 semanas.** Lo caro de construir —la intuición
de posgrado— está parcialmente intacto. Lo que falta es lo que más rápido se recupera: fórmulas,
automatismos y práctica. El óxido se quita en semanas; la intuición toma años.

### Lo que sí preocupa

1. **14 minutos en la pregunta 2.** Casi un tercio del examen en un problema que además fallaste. En el examen real eso son dos preguntas perdidas por reloj, no por ignorancia.
2. **La pregunta 8: confianza 4 y fallada.** Es el caso peligroso —crees que la sabes, así que nunca la vuelves a repasar—. Justo lo que el mapa de habilidades está diseñado para cazar.
3. **Nueve de diez fallos son conceptuales.** No hay atajo: se arregla estudiando.

---

## Qué cambia en el cronograma

Poco, y eso es buena señal: el diagnóstico **confirma** el plan en vez de contradecirlo.

1. **El orden se mantiene.** Mecánica y E&M primero (semanas 1–8) es correcto: son el 58 % del examen y es donde el óxido se quita más rápido. Termo, estadística y cuántica en las semanas 9–12, tal como está.
2. **El cronómetro arranca en la semana 1, no en la 4.** Era la única regla que el plan ponía tarde. Con 14 minutos en un problema, la disciplina de tiempo es un problema desde ya. Regla nueva: **si a los 6 minutos no ves el final, marca lo que creas y sigue.**
3. **Los patrones P1 y P5 ya están.** No los estudies desde cero en las semanas 4 y 7: repásalos y dedica ese tiempo a P2, P7, P8 y P9, que son los que fallaste.
4. **Refuerzo de herramienta matemática.** La pregunta 6 no se perdió por física sino por una expansión binomial. Añade a la semana 1 media sesión de expansiones y límites: (1+x)^n para x pequeño, y las aproximaciones que más caen.

---

## Ahora

```bash
python3 06_SEGUIMIENTO/medidor.py skills     # autoevalúa las 24 habilidades
xdg-open 06_SEGUIMIENTO/tablero.html         # mira el tablero
```

El lunes 17 arranca la semana 1.
