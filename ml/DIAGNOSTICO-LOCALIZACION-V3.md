# Diagnóstico de RAM y conectores pequeños

Se revisaron únicamente las tres imágenes de validación de v3, con un umbral diagnóstico interno de 0,25. No se consultó la prueba independiente. El detalle está en `DIAGNOSTICO-LOCALIZACION-V3.json`.

En RAM hay errores distintos:

- En ASRock B550M Steel Legend, dos de las cuatro ranuras no tienen predicciones que se superpongan a ellas; otra tiene localización insuficiente (IoU 0,379).
- En Gigabyte H610M S2H DDR4, una predicción se desplaza hacia la izquierda y produce una caja demasiado ancha. Su coincidencia máxima con una ranura real es 0,492, inferior al criterio fijo de 0,5.
- En MSI A55M-E35, una caja es demasiado angosta y omite parte de los extremos: IoU 0,497. La otra alcanza 0,605, pero su puntuación interna queda por debajo del filtro predeterminado.

Las dos últimas imágenes se inspeccionaron visualmente con etiquetas reales en verde y predicciones RAM en rojo. Las etiquetas incluyen las trabas conforme a la política vigente. No se modificaron las etiquetas para ajustarlas al modelo ni se redujo el IoU exigido para contabilizar aciertos.

El análisis de caja más cercana no aplica asignación exclusiva y no sustituye las métricas oficiales. Sirve para distinguir omisión de localización incorrecta. Bajar el filtro no resuelve ambos errores y aumenta falsos positivos, como muestra la calibración.

La siguiente ampliación debe aportar fotos de entrenamiento con ranuras individuales claramente visibles y revisar la consistencia de las cajas, especialmente trabas y perspectiva. Los conectores pequeños necesitan ejemplos legibles y variados; los recortes derivados no equivalen a nuevas motherboards. Mantener separadas las placas de validación y reservar nuevas placas para una futura evaluación independiente.
