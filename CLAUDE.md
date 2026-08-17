# ANDES — cómo trabajar en este proyecto

> Preparación para el examen de admisión a la Maestría en Ciencias – Física de
> Uniandes. **23 de noviembre de 2026.**

---

## Lo primero de cada sesión

```bash
python3 07_APP/tuberia/reportes.py
```

Lee los reportes de error que Sebastián manda desde la app. Descarga la hoja de
respuestas, baja las capturas adjuntas y cruza el código de la tarjeta con el
corpus, así que sale la pregunta reportada con sus opciones y la respuesta
registrada.

**Si hay reportes nuevos, se arreglan y punto.** Si no hay, la app no se toca.

---

## La regla que ordena todo lo demás

**El tiempo va al estudio, no a la app.**

La app está terminada y en mantenimiento. Se construyó en dos días y ya hace lo
que tiene que hacer: 2.836 tarjetas, feed con repaso espaciado, cronómetro,
modo simulacro, cronograma día a día. Cada hora extra que se le dedique es una
hora que no se dedica a física, y el examen no se aprueba construyendo la
herramienta.

Por eso los cambios entran **solo por el formulario**. No por ideas nuevas que
se le ocurran a nadie a mitad de sesión, incluidas las mías. Si algo parece que
merece la pena, se anota en `07_APP/PLAN_V2.md` bajo "Pendiente" y se decide
más adelante, con calma.

Las excepciones son dos, y conviene que sigan siendo dos:

- Un fallo que impida estudiar (la app no abre, el contenido no descifra).
- Que Sebastián lo pida explícitamente.

---

## Qué sí es trabajo de verdad ahora

Lo que dice el cronograma para hoy. Se consulta en la pestaña **Hoy** de la app
o directamente:

```bash
python3 -c "
import json; from datetime import date
c=json.load(open('docs/contenido/cronograma.json')); h=date.today().isoformat()
s=[x for x in c['semanas'] if x['inicio']<=h<=x['fin']][0]
d=[x for x in s['dias'] if x['fecha']==h][0]
print(f\"{s['id']} · {d['dia']} · {d['bloque']} · {d['horas']} h\")
print(s['titulo']); [print(' -', m) for m in d['material']]"
```

El calendario completo está en `PLAN.md §5`. Las semanas van de S0 a S13; **S1
arranca el 24 de agosto** con Mecánica I.

Y lo que produce cada semana:

- **Formularios propios**, uno por área, en `04_ESTUDIO/formularios/`. Ahora
  mismo esa carpeta está **vacía** y es el entregable de S1. El plan insiste en
  que el formulario tiene que ser propio: el de otro no sirve.
- **Registro de lo que se hace**, con `python3 06_SEGUIMIENTO/medidor.py sesion`.
- **Repaso de lo fallado**, que la app ya reinyecta sola.

---

## El estado, para no volver a averiguarlo

| | |
|---|---|
| App | https://sebrodriguezg.github.io/ANDES_APP |
| Repositorio | `github.com/Sebrodriguezg/ANDES_APP`, rama `app` |
| Clave de la app | `1234` (en `07_APP/.clave`, fuera de git) |
| Paquete de material | Carpeta de Drive, 3 volúmenes, 1 GB |
| Corpus | 2.836 tarjetas · HRW 2.525 · ETS 38 · EUF 35 · Uniandes 12 |

### Diagnóstico D1, que es lo que orienta el estudio

2 de 12. **Base 0/6 y alto 2/6** — al revés de lo normal. La intuición de
posgrado sigue ahí; lo que falla es óxido de Física 1–2, que es el 55 % del
examen. Nueve de diez fallos fueron conceptuales. Y catorce minutos en una sola
pregunta, de ahí el cronómetro.

---

## Antes de publicar cualquier cambio

```bash
bash 07_APP/pruebas/correr.sh          # 26 pruebas + auditoría + datos
python3 07_APP/tuberia/construir_contenido.py   # el portero puede negarse
```

El portero mide siete cosas y se niega a publicar si el corpus se degrada. Ha
parado ya varios builds malos, incluido uno que adjuntaba imágenes de texto a
339 preguntas sin figura.

**Cada bug entra como prueba antes de arreglarse.** Si no, vuelve: varios de
los que están congelados en `07_APP/pruebas/` se rompieron dos veces.

Y nada se da por bueno sin verlo renderizado a 414 px. Lo que se ve bien en el
código no es lo que se ve en el teléfono — los cuatro últimos fallos los
encontró Sebastián usándola, no yo leyendo el código.
