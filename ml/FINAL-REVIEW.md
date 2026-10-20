# Revisión posterior al entrenamiento

`finalize_candidates.py` compara dos trabajos completos usando únicamente la validación y su macro F1 de las nueve categorías. Exige los mismos archivos, etiquetas y umbrales de validación. Un empate detiene el proceso.

Después de guardar la selección, verifica los hashes del conjunto independiente y que sus imágenes y modelos no aparezcan en los datos de desarrollo de ninguno de los candidatos. Ejecuta una sola evaluación con el umbral ya fijado y conserva el resultado, aunque sea desfavorable. Un marcador exclusivo impide repetir la inferencia sobre el mismo conjunto. Una interrupción requiere revisar los archivos antes de cualquier recuperación manual.

```powershell
.\.venv\Scripts\python.exe ml/finalize_candidates.py tmp/nine-v3-job tmp/nine-v4-crops-job --holdout datasets/nine-independent-v1 --output tmp/nine-final-review
```

La tarea terminó correctamente el 19 de octubre de 2026. Eligió v3 usando validación y guardó su única evaluación independiente: 9 aciertos, 0 falsos positivos y 9 omisiones. Los informes se conservan en `ml/SELECCION-NUEVE-CLASES.json` y `ml/EVALUACION-INDEPENDIENTE-V3.json`. No repetir la inferencia ni ajustar el modelo con esta placa como si siguiera siendo una prueba nueva.

La evaluación independiente disponible contiene **una motherboard y 18 cajas**. Es una comprobación adicional pequeña, no evidencia suficiente para afirmar generalización a todas las placas. Las anotaciones fueron revisadas visualmente, sin certificación humana independiente. La segunda imagen investigada (`000134`) permanece excluida por identidad ambigua.

Los resultados quedan en `tmp/nine-final-review`: selección, procedencia, métricas independientes y estado. Este paso no publica archivos, no reemplaza el detector de la web y no aprueba automáticamente su uso. Los resultados deben revisarse por categoría antes de integrar otro modelo.

## Calibración posterior de v3

Se comparó un conjunto fijo de umbrales internos (0,25; 0,35; 0,5) sólo en las tres placas de validación. En `CALIBRACION-V3.json`, 0,25 alcanzó el mayor macro F1 (0,669), frente a 0,582 con 0,5. Pasó de 24 a 32 aciertos, pero también de 12 a 23 falsos positivos sobre las mismas 56 conexiones reales. Por ese aumento de errores y la falta de una nueva evaluación independiente, el umbral predeterminado sigue en 0,5. El resultado reservado anterior corresponde exclusivamente a 0,5 y no se reutilizó para calibrar. No presentar esta calibración como mejora confirmada en placas nuevas ni exponer sus valores como controles al usuario.


## Quinta corrida: revisión del 20 de octubre de 2026

V5 terminó tras 279 épocas sobre 22 fotos de 21 modelos y 440 cajas. Superó a v3 en validación (macro F1: 0,698 frente a 0,582). En dos placas nuevas encontró 15 de 48 conexiones y agregó 5 falsas detecciones: precisión 75% y recall 31,25%. La muestra es pequeña y no demuestra generalización. El paquete `ml/artifacts/nine-reviewed-v5` es experimental; el piloto de cuatro clases sigue predeterminado. Ver `ml/SELECCION-V3-V5.json` y `ml/EVALUACION-INDEPENDIENTE-V5.json`.

Las dos placas reservadas quedaron consumidas tras esta evaluación. No reutilizarlas para ajustar el modelo y luego presentarlas como independientes. El objetivo confirmado es precisión >= 95% y recall >= 95% en placas independientes. Reportar también resultados por categoría para que el agregado no oculte fallos. El resultado actual no cumple ninguno de los dos requisitos. No equivale a subir el umbral interno a 0,95. La siguiente mejora requiere más anotaciones y diversidad, especialmente en DIMM, M.2, SATA y FAN_HEADER, y una nueva reserva de evaluación.
