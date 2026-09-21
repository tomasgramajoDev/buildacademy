# Detección de conectores

Estado: pipeline implementado; entrenamiento real bloqueado por falta de imágenes etiquetadas. No se entregan pesos ni métricas inventadas. El dataset Motherboard Part Locater de BIS497 (CC BY 4.0) tiene 4 clases generales, requiere cuenta de Roboflow para exportar y no cubre las 9 clases del proyecto. El dataset de miraclefactory es de defectos de fabricación y fue descartado para esta tarea.

## Recolección

Fotografiar placas con permiso, sin datos personales visibles, de frente y también con variación de luz y ángulo. Identificar cada placa física con un `board_id`, además de marca/modelo. Etiquetar todas las conexiones visibles; no inventar etiquetas para zonas tapadas. Si hay duda entre PCIe x1/x16 físico, contrastar el manual. Las etiquetas visuales no afirman cantidad de líneas eléctricas ni protocolo M.2. No mezclar todas las ranuras DIMM en una sola caja.

La web exporta anotaciones JSON y etiquetas YOLO normalizadas. Guardar cada `.txt` con el mismo nombre base que su foto. El orden de las nueve clases está en `prepare_dataset.py`. Exportar una imagen sin marcas representa una negativa: revisar antes de incorporarla al dataset.

Crear un manifiesto JSON de filas `{image, label, board_id, source, license, split}` con rutas relativas al manifiesto. Asignar `train`, `val`, `test` por placa; nunca repartir tomas de la misma placa entre conjuntos. Incluir negativos y variedad de fabricantes. El conjunto de test debe permanecer reservado hasta cerrar decisiones de entrenamiento. La presencia de una sola caja por clase cumple el formato, no es suficiente para un modelo confiable.

## Ejecución desde la raíz del proyecto

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ml/requirements.txt
.\.venv\Scripts\python.exe ml/prepare_dataset.py datasets/manifest.json
.\.venv\Scripts\python.exe ml/train.py --epochs 80 --batch 8
```

El script usa CUDA si PyTorch la tiene disponible y CPU en caso contrario. Para entrenamiento prolongado, instalar el wheel CUDA apropiado desde la página oficial de PyTorch. El entorno local instalado inicialmente utiliza CPU; no se descargó un modelo de visión ni se ejecutó entrenamiento.

El entrenamiento descarga la inicialización oficial YOLO11n; guarda pesos, métricas por clase, gráficos y exportación ONNX. Ultralytics utiliza AGPL-3.0 o licencia comercial: revisar sus términos para la distribución elegida. No se publica automáticamente un modelo que sólo terminó de entrenar. Medir falsos positivos, recall de conectores pequeños, fotos fuera de distribución y rendimiento en placas no vistas, además de mAP. Conservar procedencia, licencias y versión del dataset.

Fuentes: https://docs.ultralytics.com/modes/train/ ; https://universe.roboflow.com/bis497/motherboard-part-locater ; https://github.com/miraclefactory/motherboard-dataset ; https://pytorch.org/get-started/locally/
