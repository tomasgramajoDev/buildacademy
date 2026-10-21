# Resultado v6 (rechazado frente a v5)

Run `nine-reviewed-26images-25models-v6`, job `tmp/nine-v6-job`, sin publicar.

- Comparación en validación idéntica (macro F1, nueve clases): v5 0.6977, v6 0.6815. v5 sigue preferido.
- Runtime en validación (conf. interna 0.5, NMS 0.45, IoU 0.5): 29 TP, 10 FP, 27 FN; precision micro 74.36 %, recall micro 51.79 %.
- Peores clases: FAN_HEADER (0 TP, 4 FP, 12 FN) y DIMM_SLOT (2 TP, 6 FN).
- Ultralytics sobre test reutilizado: P 0.731, R 0.696, mAP50 0.791, mAP50:95 0.480. No es prueba independiente.
- Objetivo de Tomi (P y R >= 95 %) y mínimos del PM: no cumplidos.

## Objetivos del PM pendientes de implementar en la evaluación

Precision, recall, F1 en punto operativo fijo; mAP@50 y mAP@50:95; AP@50 y precision por clase crítica;
recall sin subclases; exactitud de identificación; confusión entre críticos (<= 1 %);
placas completas (>= 90 %); recall de conectores pequeños (>= 90 %).
Se mantiene recall >= 95 % (instrucción directa de Tomi) sobre el 92 % propuesto por el PM.
Clases críticas, criterio de objeto pequeño y promedio micro/macro aún por acordar.

## v7

Hipótesis: YOLO11s (más capacidad) con mismo dataset, split y tamaño 640 que v6. Job `tmp/nine-v7-job`.
