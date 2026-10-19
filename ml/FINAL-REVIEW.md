# Revisión posterior al entrenamiento

`finalize_candidates.py` compara dos trabajos completos usando únicamente la validación y su macro F1 de las nueve categorías. Exige los mismos archivos, etiquetas y umbrales de validación. Un empate detiene el proceso.

Después de guardar la selección, verifica los hashes del conjunto independiente y que sus imágenes y modelos no aparezcan en los datos de desarrollo de ninguno de los candidatos. Ejecuta una sola evaluación con el umbral ya fijado y conserva el resultado, aunque sea desfavorable. Un marcador exclusivo impide repetir la inferencia sobre el mismo conjunto. Una interrupción requiere revisar los archivos antes de cualquier recuperación manual.

```powershell
.\.venv\Scripts\python.exe ml/finalize_candidates.py tmp/nine-v3-job tmp/nine-v4-crops-job --holdout datasets/nine-independent-v1 --output tmp/nine-final-review
```

En esta sesión el comando quedó programado localmente para ejecutarse al finalizar el proceso de v4, mediante una espera del sistema operativo sin consultas periódicas al modelo conversacional. No ejecutarlo nuevamente mientras esa tarea esté pendiente.

La evaluación independiente disponible contiene **una motherboard y 18 cajas**. Es una comprobación adicional pequeña, no evidencia suficiente para afirmar generalización a todas las placas. Las anotaciones fueron revisadas visualmente, sin certificación humana independiente. La segunda imagen investigada (`000134`) permanece excluida por identidad ambigua.

Los resultados quedan en `tmp/nine-final-review`: selección, procedencia, métricas independientes y estado. Este paso no publica archivos, no reemplaza el detector de la web y no aprueba automáticamente su uso. Los resultados deben revisarse por categoría antes de integrar otro modelo.
