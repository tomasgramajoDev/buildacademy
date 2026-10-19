# Detección de conectores

Estado: piloto YOLO de cuatro clases entrenado y exportado; ver EVALUACION-PILOTO.md. La ampliación a nueve clases está pendiente de nuevas anotaciones revisadas. El dataset Motherboard Part Locater de BIS497 (CC BY 4.0) tiene 4 clases generales, requiere cuenta de Roboflow para exportar y no cubre las 9 clases del proyecto. El dataset de miraclefactory es de defectos de fabricación y fue descartado para esta tarea.

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

El script usa CUDA si PyTorch la tiene disponible y CPU en caso contrario. Para entrenamiento prolongado, instalar el wheel CUDA apropiado desde la página oficial de PyTorch. El entorno local utiliza PyTorch CPU. El piloto ya se entrenó; el entrenamiento de nueve clases aún no se ejecutó.

El entrenamiento descarga la inicialización oficial YOLO11n; guarda pesos, métricas por clase, gráficos y exportación ONNX. Ultralytics utiliza AGPL-3.0 o licencia comercial: revisar sus términos para la distribución elegida. No se publica automáticamente un modelo que sólo terminó de entrenar. Medir falsos positivos, recall de conectores pequeños, fotos fuera de distribución y rendimiento en placas no vistas, además de mAP. Conservar procedencia, licencias y versión del dataset.

Fuentes: https://docs.ultralytics.com/modes/train/ ; https://universe.roboflow.com/bis497/motherboard-part-locater ; https://github.com/miraclefactory/motherboard-dataset ; https://pytorch.org/get-started/locally/

## Importar el piloto público de cuatro clases

Cuando esté disponible el ZIP YOLOv8 de BIS497 Motherboard Part Locater, ejecutar:

```powershell
.\.venv\Scripts\python.exe ml/import_roboflow.py "C:\Users\torik\Downloads\dataset.zip" --output datasets/bis497-pilot
```

El importador conserva CPU_SOCKET, DIMM_SLOT, PCIE_SLOT y POWER_CONNECTOR. No divide artificialmente las dos categorías generales en subtipos que no estén etiquetados. Comprueba rutas del ZIP y excluye duplicados de píxeles y nombres originales entre splits. Esto no prueba separación por placa física: el piloto no permite afirmar generalización a modelos de motherboard nuevos. Conserva atribución CC BY 4.0 y un registro de exclusiones. El piloto fue descargado, entrenado y evaluado; dist/models/manifest.json registra su disponibilidad y sus cuatro clases reales.

## Si la ventana de exportación de Roboflow se queda trabada

Ejecutar `Descargar-Dataset.cmd` desde la raíz del proyecto. Solicita la Private API Key existente mediante entrada oculta, la envía únicamente a api.roboflow.com por cabecera Authorization y no la guarda. Obtiene el enlace por la API oficial, limita la espera de exportación, valida destinos de redirección y comprueba que el archivo recibido sea un ZIP íntegro. No sobrescribe archivos existentes ni importa etiquetas automáticamente. La clave se encuentra en https://app.roboflow.com/settings/api . No debe enviarse por chat ni incorporarse al repositorio.

Comprobado el 21/09/2026: localhost responde HTTP 200. La API del dataset responde HTTP 401 sin clave; aún no hay una descarga autenticada verificada. Las tres pruebas del descargador verifican autenticación por cabecera, rechazo de destinos inesperados, ZIP y preservación de archivos. El candidato de Zenodo 19689558 sí se descargó y coincide con su MD5, pero sus imágenes y clases battery/connector_0..4 no corresponden al objetivo de sockets de motherboards; no se incorporó al entrenamiento.

## Descarga y preparación confirmadas

El ZIP BIS497 v5 se recibió el 21/09/2026 por la API. SHA-256: 5021e1337d6c60de540ba8c79723818708ff367c0db379671ba4f69cc8df2442. Contiene 472 imágenes (399 train, 49 val, 24 test), derivadas de 206 grupos de nombres originales. El importador convirtió 1616 polígonos a sus cajas rectangulares envolventes; preservó las cajas existentes y verificó coordenadas y clases. Los originales permanecen intactos en raw. No se encontraron duplicados exactos ni cruces de grupo por nombre; esto no prueba separación por modelo físico de placa.

La salida preparada está en datasets/bis497-detection/prepared. El entrenamiento piloto usa YOLO11n, entrada 320, 30 épocas y semilla 42. La evaluación final y exportación se escriben al terminar. `prepare_web_model.py` valida el contrato ONNX y prepara los pesos para la demo únicamente después de revisar esa evaluación.

## Ampliación a nueve clases (19/10/2026)

Se eligió completar las anotaciones y entrenar YOLO. No se reemplaza el detector por Gemini.

`annotation_queue.py` prepara una foto por grupo de nombre original, conserva las etiquetas de cuatro clases en `reference_labels` y deja identidad, split y etiquetas nuevas pendientes. Estos grupos no demuestran placas físicas diferentes. No usar las etiquetas de referencia como nueve clases ni asignar splits hasta revisar identidad y duplicados visuales.

```powershell
.\.venv\Scripts\python.exe ml/annotation_queue.py datasets/bis497-pilot/manifest.json
```

La cola local contiene 206 fotos de 472 variantes; ninguna está todavía revisada para las nueve clases. Para cada foto, identificar marca/modelo y placa física cuando sea posible, dibujar todas las conexiones visibles, separar ranuras DIMM individuales, comprobar formato físico PCIe y distinguir ATX/EPS. No etiquetar un disipador como un socket M.2 oculto ni un soporte de ventilador como FAN_HEADER. Reservar placas/modelos completos para validación y test. Una vez revisadas, crear el manifiesto descrito arriba y ejecutar la validación antes del entrenamiento.

Fuente adicional candidata: [Motherboard Sockets](https://universe.roboflow.com/computer-vision-assembly-instructions/motherboard-sockets), Computer Vision Assembly Instructions, CC BY 4.0. Publica clases de alimentación y M.2, pero requiere revisión y no resuelve por sí sola SATA, FAN_HEADER ni la división PCIe x1/x16. Descarga autenticada completada el 19/10/2026; ROBOFLOW_API_KEY permanece sólo en el entorno local. La auditoría detectó problemas de etiquetas y separación: ver CANDIDATO-SOCKETS-V2.json. No está aprobado para entrenar sin corregirlo.

La pantalla no muestra porcentajes ni un selector de confianza. El detector conserva su umbral interno de 0.5 y NMS; el campo confidence sigue en las anotaciones técnicas exportadas.

### Resultado de la auditoría del candidato

La exportación v2 contiene 4.399 imágenes de 640×640 (4.051 train, 348 test, sin validación), 13 clases y 3.745 polígonos. Hay 163 grupos de nombres originales compartidos entre train y test, aunque no se encontraron duplicados exactos de píxeles entre ambos. La revisión visual de muestras encontró M.2 etiquetado sobre el disipador que lo oculta y ranuras PCIe visibles sin etiquetar. No se convirtió este candidato en datos de entrenamiento ni se reemplazó el modelo piloto.

Los originales y 13 hojas de muestras permanecen en `datasets/motherboard-sockets-v2-audited/`. El informe reproducible sin imágenes ni secretos está en `ml/CANDIDATO-SOCKETS-V2.json`. Las anotaciones deben corregirse y completarse en todas las fotos seleccionadas, incluyendo SATA y FAN_HEADER, y separarse por placa/modelo antes de entrenar.

```powershell
.\.venv\Scripts\python.exe ml/download_roboflow.py --endpoint https://api.roboflow.com/computer-vision-assembly-instructions/motherboard-sockets/2/yolov8 --output datasets/motherboard-sockets-v2-yolov8.zip
.\.venv\Scripts\python.exe ml/audit_candidate.py datasets/motherboard-sockets-v2-yolov8.zip --output datasets/motherboard-sockets-v2-audited
```

Ambos comandos preservan salidas existentes. El descargador toma ROBOFLOW_API_KEY del entorno o de .env; si falta, la solicita de forma oculta. Sólo envía la clave por cabecera al endpoint de exportación de api.roboflow.com.

## Revisión posterior al entrenamiento de 40 épocas

`review_models.py` compara ambos ONNX con confianza 0,5, NMS 0,45 y coincidencia IoU 0,5 sobre las mismas 24 imágenes de test (150 cajas). Usa el preprocesado de Ultralytics; no equivale a una prueba en navegador. Resultados reproducibles en REVISION-CUATRO-CLASES.json:

| Modelo | TP | FP | FN | Precisión | Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Actual, 320 px | 100 | 7 | 50 | 93,46 % | 66,67 % |
| Candidato, 416 px | 98 | 11 | 52 | 89,91 % | 65,33 % |

Aunque el candidato mejora el mAP global, no mejora este punto de operación. Se conserva el modelo actual en la web. El test reutilizado no sirve como certificación independiente de generalización.

## Anotaciones e identidad

ANOTACION-Z690-BORRADOR.json registra 27 cajas propuestas para una foto de MSI PRO Z690-A DDR4, contrastadas con el esquema del manual oficial. Incluye nueve categorías, pero sigue siendo un borrador: la vista no separa los puertos SATA apilados y quedan límites de cajas pequeños por revisar. No es un dataset de entrenamiento. Las fotos 000010 y 000031 de la cola corresponden al mismo modelo y deben permanecer juntas. El resto de las identidades y anotaciones siguen pendientes; no se afirma haber revisado 206 imágenes.

`review_gate.py manifest.json --output datasets/connectors-nine-prepared` exige identidad con evidencia, revisión completa, ausencia de ambigüedades y separación por modelo. Luego ejecuta la validación geométrica y de cobertura. Estos controles verifican lo declarado en el manifiesto, no sustituyen la inspección de fotos. `train.py` exige este informe para entrenar las nueve clases. La auditoría de cuatro clases conserva su flujo existente.

Estado: revisión del candidato de cuatro clases terminada. Conjunto inicial de nueve clases anotado y separado por modelo; primera corrida de entrenamiento iniciada. Evaluación e incorporación del modelo ampliado pendientes.

## Progreso de anotación revisada

La fuente vigente es `ml/annotations/*.json`, bajo la política `ml/ANNOTATION-POLICY.md`. El borrador ANOTACION-Z690-BORRADOR.json se conserva como antecedente; la anotación revisada de esa foto está en annotations/msi-pro-z690-a-ddr4-000031.json. Los criterios de carcasas SATA y sockets con tapa están documentados explícitamente, no se afirma contar puertos a partir de cajas.

Se revisaron dieciséis imágenes de dieciséis modelos, con 316 cajas en total, usando esquemas del fabricante. Hay diez modelos en train, tres en val y tres en test; los modelos reservados quedan excluidos del entrenamiento. La cobertura de nueve categorías pasa en los tres conjuntos. Se alcanzó el objetivo inicial de recolección de 10/3/3 modelos, que no garantiza generalización. Se inició la primera corrida de nueve clases a 640 px, hasta 80 épocas, batch 4. Estado y conteos en NINE-DATASET-PROGRESS.json. Entrenamiento y evaluación todavía pendientes de cierre; no se autoriza publicar estos pesos por completar la corrida.

`python ml/build_reviewed_manifest.py` verifica los hashes de las fotos, genera etiquetas YOLO y vistas de revisión en datasets/nine-reviewed. El manifiesto pasa los controles geométricos, de identidad declarada y cobertura; esto no implica suficiencia del dataset ni aprobación del modelo. La cola de 206 imágenes es un inventario inicial, no una certificación de revisión de todas ellas.

## Primera evaluación de nueve categorías

La corrida inicial terminó sus 80 épocas y exportó ONNX de forma correcta. La prueba obtuvo mAP50 0,2953 y mAP50-95 0,1418, con recall 0,2052 en la evaluación Ultralytics. Esto no equivale al punto de operación del servicio: con su umbral fijo 0,5, NMS 0,45 y matching IoU 0,5, el runtime real detectó sólo 2 de 55 cajas de test. En train detectó 19 de 205, con un falso positivo. No se aprueba este candidato para despliegue.

La evidencia queda en REVISION-NUEVE-CLASES-V1.json. `evaluate_runtime.py` ejecuta el mismo ConnectorDetector usado por el backend y reporta TP/FP/FN por clase; no ajusta umbrales a partir del test. Se inició otra corrida desde los pesos generales YOLO11n, con 300 épocas, batch 2 y paciencia 100, manteniendo el dataset y sus separaciones. Los pesos del piloto de cuatro clases no se usan como inicialización porque su dataset podría incluir las placas reservadas. El test ya consultado se considera diagnóstico, no certificación independiente. La muestra pequeña sigue limitando las conclusiones.

## Trazabilidad del conjunto preparado

NINE-DATASET-PROVENANCE.json vincula las 16 imágenes y etiquetas usadas por ambas corridas con modelo, split, fuente, manual y hashes SHA-256. Se verificaron las copias preparadas contra los originales revisados, incluyendo ausencia de archivos extra. No acredita revisión humana independiente ni precisión de las anotaciones.

```powershell
python ml/verify_prepared_dataset.py --manifest datasets/nine-reviewed/manifest.json --prepared datasets/connectors-nine-prepared-16models --output tmp/provenance.json
```
