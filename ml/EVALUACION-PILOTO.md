# Evaluación del detector piloto · 21/09/2026

YOLO11n preentrenado oficial, ajuste local de 30 épocas, entrada 320×320, batch 8, CPU y semilla 42. Mejor checkpoint elegido con validación; evaluación final única sobre test. Dataset BIS497 Motherboard Part Locater v5, CC BY 4.0: https://universe.roboflow.com/bis497/motherboard-part-locater/dataset/5 .

472 imágenes: 399 de entrenamiento, 49 de validación, 24 de test (150 cajas). Hay 206 grupos por nombre original. Se convirtieron 1616 polígonos a cajas envolventes, conservando originales y categorías. No se encontraron duplicados exactos/cruces por nombre original. No se verificó separación por modelo físico de motherboard.

## Test

| Métrica | Resultado |
|---|---:|
| metrics/precision(B) | 0.8506 |
| metrics/recall(B) | 0.8140 |
| metrics/mAP50(B) | 0.8689 |
| metrics/mAP50-95(B) | 0.5559 |

| Clase | mAP@50–95 |
|---|---:|
| CPU_SOCKET | 0.6513 |
| PCIE_SLOT | 0.4865 |
| POWER_CONNECTOR | 0.4623 |
| DIMM_SLOT | 0.6233 |

La mAP no es un porcentaje de fotos correctas. Los valores no garantizan rendimiento en otras placas, ángulos o iluminación. Alimentación tiene el peor mAP@50–95; se observaron falsas detecciones y omisiones. PCIe y alimentación son categorías genéricas: no separan x1/x16 ni ATX/EPS. M.2, SATA y FAN_HEADER no se entrenaron. El modelo ubica candidatos y no decide compatibilidad eléctrica.

Exportación ONNX: float32, entrada [1,3,320,320], salida [1,8,2100], opset 17, sin NMS incorporada. El navegador filtra confianza y aplica NMS por clase. La evaluación de arriba corresponde al modelo PyTorch; la integración ONNX se comprueba adicionalmente en el navegador.

SHA-256 ONNX: 8312df3e829f590093845813e1abc81e9ba935be984e0d057160b79f3d52a03d

Prueba ONNX en localhost: 000000.jpg del test produjo 3 candidatos al 50%, en 0,8 s incluida la carga inicial, sin errores de consola. Es una observación puntual, no un benchmark de latencia.

Segunda prueba local: 000008.jpg produjo 8 candidatos de las cuatro clases al 50%, en 0,1 s con el modelo ya cargado.
