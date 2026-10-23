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

## Resultado v7 (YOLO11s, 640)

Entrenó hasta ~época 246 (patience). Sin publicar.
- Validación idéntica, macro F1: v7 0.7133 vs v5 0.6977. v7 gana por 0.016 sobre 3 fotos: ventaja no concluyente.
- Mejora DIMM (3 TP vs 1), ATX_POWER y CPU_POWER; empeora SATA (10 vs 12) y FAN_HEADER sigue en 0 TP con 5 FP.
- Ultralytics sobre test reutilizado: P 0.729, R 0.791, mAP50 0.804, mAP50:95 0.483.
- Lejos de 95/95. No se consumió el holdout independiente.

## Resultado v8 (YOLO11s, 640, +8 placas de Wikimedia Commons)

Dataset `datasets/connectors-nine-prepared-34images-33models` (25 train / 4 val / 5 test modelos). Placas nuevas anotadas a mano
sobre fotos de 1280-1920 px (CC BY-SA/CC0, procedencia en `datasets/commons-boards/provenance.json`). Cinco placas más quedaron
reservadas como holdout futuro en `ml/HOLDOUT-RESERVATIONS.json` (sin anotar, sin inferencia). Sin publicar.
- La comparación automática falló a propósito: la validación cambió (ahora 4 modelos), así que v7 y v8 se midieron ambos sobre la nueva val con `ml/pm_metrics.py`.
- Nueva val, punto operativo 0.5: v7 P 78.3 % / R 47.4 %; v8 P 83.9 % / R 34.2 %. v8 NO mejora el recall.
- FAN_HEADER: 0 TP en ambos. PCIe_X16 y SATA empeoran en v8.
- Ocho placas más no bastan; el límite sigue siendo diversidad/cantidad, y a 640 px los conectores pequeños no se resuelven.
- Objetivo 95/95 y métricas del PM: no cumplidos. Holdout Prime Z690-A sin evaluar.

## Resultado v9 (YOLO11s, 960 px, mismo dataset que v8)

Hipótesis: la resolución de entrada limita conectores pequeños. Se añadió soporte 960 (train, empaquetado y runtime). 300 épocas, ~2.4 h CPU. Sin publicar.
- Misma val (4 modelos), punto 0.5: v7 P 78.3/R 47.4; v8 P 83.9/R 34.2; **v9 P 77.0 / R 61.8**, F1 68.6, mAP50 75.2, recall pequeños 43.5.
- DIMM 10/12, PCIe x16 7/7, PCIe x1 5/5; SATA 11/20; FAN_HEADER 1 TP, 8 FP.
- Mejora real de recall con resolución, pero sigue lejos de 95/95 y del panel del PM. Holdout Prime Z690-A sin evaluar.
- El paso `--compare-job` falló sólo porque el job v8 estaba marcado failed; el empaquetado, runtime y HTTP de v9 terminaron.

## Resultado v10 (YOLO11s, 1280 px, 200 épocas)

Misma val (4 modelos), punto 0.5: P 83.3 %, R 52.6 %, F1 64.5, mAP50 80.5, AP50 crítico mínimo 0.41, recall pequeños 41.3.
FAN_HEADER 4 TP / 4 FP / 12 FN (mejor que v9); DIMM 5/12 (peor que v9); SATA 10/20.
No supera a v9 en recall (61.8 %) ni en F1 (68.6): 1280 no aporta sobre 960 con 34 fotos. Mejor candidato actual: v9. Sin publicar; holdout sin evaluar.

## Resultado v11 (YOLO11s, 960 px, 36 fotos / 35 modelos; +2 Gigabyte Z170X anotadas)

Misma val (4 modelos), punto 0.5: **P 86.7 %, R 68.4 %, F1 76.5 %** (v9: 77.0 / 61.8 / 68.6). DIMM 11/12, PCIe x16 7/7, PCIe x1 5/5,
ATX 4/4, FAN_HEADER 6 TP/4 FP/10 FN (mejor candidato hasta ahora), SATA 10/20, M.2 1/3. Mejor candidato actual: v11. Sin publicar; holdouts sin evaluar.
Aún lejos de 95/95 y del panel del PM.

## Resultado v12 (YOLO11s, 960 px, 39 fotos / 37 modelos; +Mucai H61-XB, ASRock AB350M Pro4, Gigabyte G1.Sniper 5 en train)

Misma val de 4 modelos que v11; test de 5 modelos (medido una sola vez más).
- Val: P 78.8 %, R 68.4 %, F1 73.2 % (v11: 86.7 / 68.4 / 76.5). Empate en recall, peor precision.
- Test: P 83.7 %, R 46.1 %, F1 59.4 % (v11: 67.7 / 49.4 / 57.1). Más precision, menos recall.
- No hay mejora clara sobre v11: +3 placas cambian el resultado dentro del ruido de una val/test de 4-5 placas. Mejor candidato sigue siendo v11 (por val); ninguno publicado.
- Aviso de calidad: varias placas nuevas dejan sin etiquetar conectores reales (SATA oscuros, headers de ventilador, M.2 Wi-Fi) por ambigüedad; eso penaliza el recall que se mide.

## Fuentes revisadas y descartadas (2026-10-22)

- Roboflow `motherboard_segmentation` (CC BY 4.0, 550 img): solo CPU_Socket, RAM, Port PCI, Northbridge; segmentación.
- Roboflow `Mother_board` (72 img): una sola clase.
- Roboflow `motherboard` de hanan ali: clases de defectos.
- Roboflow `merged_motherboard_yolo` (pokalokaopa, CC BY 4.0, 1.770 img; clases atx_12v/atx_power/cpu-slot/m-2-ssd-slot/pcie-slot/ram-slot/sata): no descargado. Parece derivado de `motherboard-sockets` ya auditado (cajas sobre disipadores, PCIe incompleto, fotos repetidas, 640 px) y no tiene FAN_HEADER ni separa x16/x1.

## Resultados v12-v14 sobre las particiones de 46 fotos / 44 modelos (val 6 placas, test 6 placas), punto 0.5

| Modelo | Val P / R / F1 | Test P / R / F1 |
|---|---|---|
| v11 (36 fotos, 960) | 88.5 / 63.9 / 74.2 | 70.5 / 53.9 / 61.1 |
| v12 (39 fotos) | 80.8 / 58.3 / 67.7 | 80.0 / 47.1 / 59.3 |
| v13 (44 fotos) | 81.6 / 57.4 / 67.4 | 81.8 / 44.1 / 57.3 |
| v14 (46 fotos + 102 rotaciones de train) | 83.5 / 61.1 / 70.6 | 72.1 / 48.0 / 57.6 |

- Más placas (v12, v13) y rotaciones exactas 90/180/270 (v14, `ml/augment_rotations.py`) no superan a v11. No hay subentrenamiento (pérdida de train igual, parada por paciencia).
- Diferencias de pocos puntos con 6 placas de evaluación (~100 objetos) están dentro del ruido; no se puede elegir modelo con esa resolución.
- GPU: `.venv-gpu` (torch 2.11+cu128, RTX 4060 8 GB) entrena 300 épocas a 960 px en ~20 min con 44 fotos (CPU: horas).
- Mejor candidato sigue siendo v11. Ninguno publicado. Holdouts (Prime Z690-A y 5 placas de Commons) sin evaluar. 95/95 y panel del PM sin cumplir.

## v15 (YOLO11m, 960 px, 46 fotos / 44 modelos) y barrido de umbral

- Punto 0.5: val P 89.5 / R 31.5; test P 69.6 / R 31.4. Peor que v11 (val 88.5/63.9; test 70.5/53.9).
- Barrido de umbral sólo con val (0.15-0.5) y aplicado una vez a test: v11 mejor F1 en 0.5 (test P 70.5 / R 53.9); v15 mejor en 0.25 (test P 59.3 / R 52.9). Mayor capacidad no ayuda con ~45 placas; el techo sigue siendo la cantidad/diversidad de datos.
- El umbral 0.5 de v11 es razonable; no hay umbral que acerque ningún modelo a 95/95 (a 0.15 el recall val no pasa de 70 % y la precision cae a 71 %).

## Evaluación independiente de v11 (5 placas de Commons reservadas, evaluada una sola vez)

Placas nunca vistas (ASUS ROG STRIX Z390-H, MSI MAG B550 Tomahawk, ASUS M5A99X EVO, ASUS B85-PLUS, MSI Z97A GAMING 5), anotadas a mano antes de cualquier inferencia. v11 elegido por validación. Umbral 0.5, sin ajustes.
- 54 TP / 28 FP / 36 FN: **precision 65.9 %, recall 60.0 %**, F1 62.8 %, mAP50 0.55, recall de objetos pequeños 40.4 %.
- Por clase (TP/FP/FN): DIMM 16/8/4, PCIe x16 12/3/1, PCIe x1 10/3/2, ATX 5/0/0, SATA 5/1/13, CPU_POWER 1/3/4, CPU_SOCKET 3/2/2, M.2 2/1/1, FAN_HEADER 0/7/9.
- Conclusión honesta: muy lejos de 95/95. Resultado coherente con test y validación; la ordenación de modelos no cambia. Los holdouts quedan consumidos: no usarlos para ajustar. Prime Z690-A (000087) sigue sin evaluar.
