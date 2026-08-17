# Plan de desarrollo — app de estudio

> Reemplazar el scroll de Instagram y TikTok por un scroll que meta a la maestría.
> Mismo gesto, misma dosis de recompensa variable, contenido que sí sirve el 23 de noviembre.

**Rama de trabajo:** `app` · **Repo:** `github.com/Sebrodriguezg/ANDES_APP` (público)
**Sirve:** GitHub Pages desde `main` → carpeta `/docs`

---

## Principio de diseño

Las apps que desinstalaste funcionan por cuatro mecanismos. Los tres primeros se copian tal cual;
el cuarto se invierte a propósito.

| Mecanismo | Cómo se usa aquí |
|---|---|
| **Recompensa variable** | No sabes qué tipo de tarjeta viene: pregunta, ecuación, patrón, dato, reto de descarte |
| **Retroalimentación inmediata** | Tocas una opción y sabes al instante si acertaste, con la explicación abajo |
| **Racha y progreso visible** | Anillo de meta diaria, racha de días, combo de aciertos seguidos |
| **Scroll infinito sin final** | **Invertido.** El feed tiene cierre: al llegar a la meta aparece una tarjeta de cierre y para |

La diferencia de fondo: Instagram optimiza tiempo en pantalla, esto optimiza aciertos en noviembre.
Por eso el feed **no** es aleatorio puro — pondera hacia tus áreas débiles y hacia la semana del cronograma
en la que estés.

---

## Arquitectura

```
ANDES/
├── docs/                        ← lo que publica GitHub Pages
│   ├── index.html               una sola página, enrutado por hash
│   ├── app.webmanifest          para anclarla como app en el celular
│   ├── sw.js                    service worker: funciona sin datos
│   ├── css/  js/                sin framework, sin paso de compilación
│   ├── vendor/katex/            KaTeX local, para que las fórmulas rendericen sin internet
│   └── contenido/
│       ├── manifiesto.json      índice de tandas y metadatos
│       ├── cronograma.json      las 14 semanas, día por día
│       └── tanda-NN.json.enc    contenido cifrado, cargado bajo demanda
└── 07_APP/
    ├── tuberia/                 extractores y constructor en Python
    └── autoral/                 tarjetas escritas a mano (patrones, ecuaciones, descarte)
```

**Sin framework y sin `npm`.** JavaScript de módulos ES y CSS plano: se sirve tal cual, no hay nada que
compilar y no se rompe en dos años cuando cambie alguna herramienta. Es la misma decisión que ya tomó
`medidor.py` al no depender de matplotlib.

**Sobre el tamaño y la rotación.** GitHub Pages aguanta ~1 GB, y el corpus completo comprimido cabe en
pocos MB — no hace falta volver a subir contenido cuando termines el feed. Lo que se hace es partirlo en
**tandas** que la app descarga solo cuando las necesita: la primera carga es rápida, y al terminar una
tanda la siguiente ya está en el repositorio esperando. La tubería puede regenerar y rebarajar todo con
un comando cuando quieras contenido nuevo.

**Cifrado.** Los shards van cifrados con AES-GCM (WebCrypto). Metes una clave la primera vez y queda
guardada en el teléfono. El repositorio es público y gratuito, pero el banco HRW no queda legible ni
indexable para nadie más.

---

## Las cuatro pestañas

| Pestaña | Qué hace |
|---|---|
| **HOY** | Cuenta regresiva al 23-nov · en qué semana vas · qué toca hoy según el cronograma · anillo de meta diaria · racha |
| **FEED** | El scroll. Tarjetas de 9 tipos, carga infinita, cierre al llegar a la meta |
| **PLAN** | Las 14 semanas completas. Tocas una semana → ves temas, lecturas BASE/ALTO, problemas y entregable |
| **YO** | Aciertos por área, los 10 patrones, mapa de 24 habilidades, exportar a `medidor.py` |

## Los nueve tipos de tarjeta

| Tipo | Qué es | De dónde sale |
|---|---|---|
| `mc` | Pregunta de opción múltiple, 5 opciones, respuesta inmediata | HRW, ETS, EUF, Uniandes |
| `flash` | Pregunta al frente, tocas y se revela | Autoral + derivadas |
| `ecuacion` | Fórmula grande + qué significa + dónde está la trampa | Autoral |
| `patron` | Uno de los 10 patrones, condensado a una tarjeta | Autoral |
| `descarte` | Mata 4 opciones por dimensiones o casos límite, sin resolver | Autoral |
| `micro` | Micro-lección conceptual de ~150 palabras | Autoral |
| `error` | Un problema que **tú** fallaste, reinyectado a los 3 y 14 días | `06_SEGUIMIENTO/datos/` |
| `dato` | Constante, orden de magnitud, valor que hay que tener en la cabeza | Autoral |
| `cierre` | Resumen de la sesión y freno explícito | Generada |

---

## Fases

### F0 · Andamiaje y despliegue
Estructura de `docs/`, cascarón de la app, manifiesto PWA, service worker, KaTeX local.
Activar Pages y **anclarla en el celular**. Se despliega vacía a propósito: primero se prueba la cadena
completa hasta el teléfono, después se llena.
*Entregable: la app abre en tu celular desde el ícono.*

### F1 · Corpus
Extractores con reconstrucción de superíndices por geometría (`pdftotext -bbox-layout`):
HRW (~2.650), ETS Practice Book (100), Uniandes 2024 (25), EUF 2020-2+ (~400).
Normalizador a un esquema único con área, nivel BASE/ALTO, semana, patrón y etiquetas.
*Entregable: `corpus.json` con ~3.200 preguntas verificadas.*

### F2 · Cronograma
Parser de `03_TEMARIO/*.md` y `PLAN.md` → `cronograma.json` con las 14 semanas desglosadas por día
según la estructura de semana tipo. Pestañas **HOY** y **PLAN**.
*Entregable: abres la app y sabes qué estudiar hoy.*

### F3 · Feed
Motor de tarjetas, los 9 tipos, carga perezosa de tandas, barajado con semilla, memoria de vistos,
ponderación por área débil y por semana en curso.
*Entregable: el scroll funciona.*

### F4 · Progreso
Racha, meta diaria, combo, repaso espaciado a 3 y 14 días, estadísticas por área y patrón,
exportación a CSV compatible con `medidor.py`.
*Entregable: lo que haces en el celular alimenta el tablero que ya existe.*

### F5 · Contenido autoral ✅
52 tarjetas escritas a mano, priorizadas según el diagnóstico D1 (base 0/6):
los 10 patrones, 19 ecuaciones por área, 8 técnicas de descarte —cinco de ellas
atadas a un fallo concreto tuyo del D1—, 5 fichas de constantes y órdenes de
magnitud, más tus 10 errores reinyectados. Crece cada semana.

### F6 · Cifrado ✅
Tandas cifradas con AES-256-GCM, clave derivada por PBKDF2-SHA256 con 210 000
iteraciones. La frase se escribe una vez y queda guardada en el teléfono. Un
canario en el manifiesto permite decir "clave incorrecta" al instante en vez de
reventar al descifrar. La frase vive en `07_APP/.clave`, fuera de git.

### Pendiente
Rotación de tandas con semilla nueva, ajustes de diseño tras usarla en el
celular, y más contenido autoral conforme avancen las semanas.

---

*Creado el 16 de agosto de 2026 · 99 días para el examen*
