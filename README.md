# ANDES_APP

Preparación para el examen de admisión a la **Maestría en Ciencias – Física**, Universidad de los Andes.

**Examen: 23 de noviembre de 2026.** 25 preguntas de opción múltiple, 3 horas.

---

## Qué hay aquí

| Carpeta | Contenido |
|---|---|
| `PLAN.md` | Plan maestro: radiografía del examen, calendario de 14 semanas, método, riesgos |
| `00_ADMISION/` | Requisitos del proceso y lista de material faltante |
| `01_EXAMENES/` | Bancos de examen *(no versionado — ver abajo)* |
| `02_BIBLIOTECA/` | `INVENTARIO.md` con el catálogo; los PDF viven solo en local |
| `03_TEMARIO/` | Desglose semana → tema → capítulo, y los **10 patrones** recurrentes |
| `04_ESTUDIO/` | Formularios, notas y mazos de repaso espaciado |
| `05_SIMULACROS/` | Simulacros armados y su análisis |
| `06_SEGUIMIENTO/` | `medidor.py`: registro de sesiones, simulacros y errores + tablero |
| `07_APP/` | Web app móvil de estudio (feed + cronograma), servida por GitHub Pages |

## Material no versionado

Los ~651 MB de libros y bancos de examen en PDF **no están en el repositorio**: son material con
copyright y se quedan en el disco local. `.gitignore` los excluye. El catálogo completo, con la
ubicación de cada archivo, está en `02_BIBLIOTECA/INVENTARIO.md`.

## Seguimiento

```bash
python3 06_SEGUIMIENTO/medidor.py estado      # resumen + mapa de habilidades
python3 06_SEGUIMIENTO/medidor.py sesion      # registrar sesión de estudio
python3 06_SEGUIMIENTO/medidor.py simulacro   # registrar y calificar un simulacro
python3 06_SEGUIMIENTO/medidor.py reporte     # regenerar gráficas y REPORTE.md
```

Instructivo completo en `06_SEGUIMIENTO/INSTRUCTIVO.md`.

---

*Licencia MIT — aplica al código propio de este repositorio, no al material de estudio referenciado.*
