# Explicaciones

Una explicación por tarjeta, indexada por su `id`. Un archivo por bloque de
revisión, para que el diff de cada bloque se pueda leer entero.

## Formato

```json
{
  "ets-gr1775-q001": {
    "idea": "Una línea: qué concepto decide la pregunta.",
    "pasos": [
      "El camino, de dos a cinco pasos.",
      "Las fórmulas van en LaTeX entre signos de dólar: $R = (k_1-k_2)^2$."
    ],
    "porque_fallan": {
      "A": "Qué error concreto te lleva a marcar esta.",
      "C": "..."
    },
    "confirma": "B"
  }
}
```

## La regla

`confirma` es la letra a la que llega la explicación. **Tiene que coincidir con
la respuesta registrada en el corpus.** Si no coincide, el portero no publica:
o la explicación está mal, o lo está la clave, y hay que mirarlo.

Las tarjetas que no se hayan podido resolver simplemente no aparecen aquí. Una
tarjeta sin explicación te deja donde estabas; una con una explicación mal
razonada te enseña física falsa.
