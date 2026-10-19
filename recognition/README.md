# Reconocimiento de conectores: integración

Estado: módulo ejecutable con el piloto de cuatro clases por defecto y soporte probado para paquetes de nueve clases. Tres corridas de nueve clases terminaron; el segundo candidato se conserva en `ml/artifacts/nine-reviewed-v2` para pruebas de integración. La tercera revisión está en `ml/REVISION-NUEVE-CLASES-V3.json`; detectó 25/55 conexiones del test reutilizado con 11 falsos positivos a umbral 0,5, y todavía falla en M.2 y ventiladores. Hay una prueba posterior con recortes en evaluación pendiente. `coversNineClasses` describe el contrato del modelo cargado, no certifica precisión. No cambiar el modelo predeterminado hasta aprobar su evaluación. Ver `INTEGRACION.md` para la entrega conjunta con el chatbot.

## Backend Python

Instalar `python -m pip install -r recognition/requirements.txt` para ejecutar el detector. Este archivo contiene las dependencias de inferencia; `ml/requirements.txt` corresponde al entrenamiento y exportación. ONNX Runtime ejecuta en CPU sin llamadas externas ni API keys. Crear una instancia por worker y reutilizarla:

```python
from recognition import ConnectorDetector, RecognitionError
detector = ConnectorDetector()
result = detector.recognize(image_bytes)
```

El modelo se valida mediante el SHA-256 del manifiesto local. Las rutas del modelo son configuración de confianza del servidor, nunca datos del cliente. La imagen no se guarda ni se envía a Gemini. Se admiten JPG, PNG y WebP estáticos, hasta 15 MB, 20 megapíxeles y mínimo 32 px por dimensión.

## Adaptador HTTP local

```powershell
.\.venv\Scripts\python.exe -m recognition.server
```

Escucha exclusivamente en `127.0.0.1:8770`. `POST /v1/recognitions`, cuerpo binario de imagen, Content-Type image/jpeg, image/png o image/webp y Content-Length. No enviar multipart ni JSON base64. Backend puede reutilizar `create_app()` como WSGI o llamar directamente al detector.

Ejemplo desde Node/backend:

```js
const response = await fetch('http://127.0.0.1:8770/v1/recognitions', {
  method: 'POST', headers: {'Content-Type': imageMime}, body: imageBytes,
  signal: AbortSignal.timeout(30000)
});
const result = await response.json();
if (!response.ok) throw new Error(result.error.code);
```

El servidor incluido es para desarrollo/integración local. Producción requiere servidor WSGI adecuado, límite y timeout de lectura en el proxy, autenticación, autorización del armado, cuotas y registro de errores del backend. No exponer el servidor de desarrollo a Internet. No se ofrece CORS directo: frontend utiliza el backend autenticado de la aplicación. No hay reintentos automáticos.

## Respuesta estable v1

```json
{
  "schemaVersion": 1,
  "model": {
    "version": "bis497-v5-yolo11n-pilot-1",
    "classes": ["CPU_SOCKET", "PCIE_SLOT", "POWER_CONNECTOR", "DIMM_SLOT"],
    "coversNineClasses": false
  },
  "image": {"width": 640, "height": 480, "orientation": "exif_transposed"},
  "detections": [
    {"classId": "CPU_SOCKET", "confidence": 0.8,
     "bbox": {"x": 100, "y": 100, "width": 80, "height": 90}}
  ],
  "compatibilityVerified": false
}
```

Ejemplo ilustrativo. Las cajas usan píxeles de la imagen original después de aplicar EXIF. `x,y` es la esquina superior izquierda. Una lista vacía significa que no hubo detecciones claras; no certifica que la placa carezca de conectores. El resultado no determina compatibilidad, protocolo M.2, líneas PCIe, versión ni estado eléctrico.

Se filtra con 0,5 y NMS por clase con IoU 0,45; máximo 100 cajas. Es un detalle interno. No mostrar porcentajes de confianza ni controles de umbral al usuario.

Errores HTTP: 400 imagen inválida/incompleta, 413 tamaño excedido, 415 tipo no admitido, 429 detector ocupado, 500 fallo interno. Respuesta `{ "error": { "code": "..." } }`; no devuelve rutas internas, traceback ni secretos.

## Frontend, sin construir una interfaz nueva

Importar `toDisplayBoxes` de `recognition/frontend.js` y pasar la respuesta más el ancho/alto del área ocupada por la imagen. Devuelve cajas escaladas sin confianza. Si se utiliza object-fit:contain, sumar por separado los márgenes de la imagen dentro del contenedor. Mostrar la imagen orientada con EXIF, nombres de conexiones y una indicación de revisar las marcas. No modificar la configuración del armado por una detección.

## Prueba por terminal

```powershell
.\.venv\Scripts\python.exe -m recognition foto.jpg
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_recognition.py
node --test tests/recognition.test.mjs
```

## Modelo ampliado pendiente

La segunda corrida de nueve clases terminó (300 épocas, 16 modelos de placa separados: 10/3/3). La revisión está en `ml/REVISION-NUEVE-CLASES-V2.json`. A umbral 0,5 encontró 19 de 55 conexiones de prueba con 6 falsos positivos. Una comparación limitada de umbrales en validación seleccionó 0,35; en el test reutilizado encontró 25 de 55 con 13 falsos positivos. Esto todavía no justifica desplegarlo: faltan ejemplos diversos, especialmente de conectores pequeños. Se conserva el detector actual de cuatro clases.

`ConnectorDetector(model_dir=..., threshold=0.35)` permite reproducir esa evaluación experimental desde código de backend. El valor por defecto sigue en 0,5. No exponer este parámetro ni la confianza en la interfaz. Los resultados del test reutilizado son diagnósticos y requieren otra evaluación independiente antes de afirmar generalización.

El contrato admite el orden de nueve clases de `ml/prepare_dataset.py`. Cambiar el manifiesto sin entrenar pesos de nueve clases no agrega capacidades. Antes de integrar ese modelo: completar anotaciones revisadas, separar por motherboard/modelo, entrenar, evaluar fotos independientes y validar el ONNX. El objetivo de nueve categorías sigue abierto.

## Paquetes de candidatos

`ml/prepare_web_model.py RUN --output NUEVO_DIRECTORIO --version VERSION` acepta los contratos de cuatro y nueve clases. Requiere evaluación terminada y ONNX compatible; para nueve clases también exige la auditoría de revisión. Produce connectors.onnx, manifest.json y evaluation.json. Rechaza sobrescribir directorios existentes o dist/models. `ready` significa que el paquete puede cargarse, no aprobación de precisión; `releaseStatus: experimental` exige revisar las métricas y errores antes de desplegar.

El backend puede cargarlo con `ConnectorDetector(model_dir=...)` y entregarlo a `create_app(detector)`. Para pruebas locales independientes:

```powershell
python -m recognition foto.jpg --model-dir tmp/candidato
python -m recognition.server --model-dir tmp/candidato --port 8771
```

No se cambia el contrato de respuesta ni se muestran porcentajes de confianza al usuario. La ubicación del modelo es configuración del servidor, nunca un parámetro del cliente HTTP.

## Verificación de integración

`python ml/smoke_integration.py --model-dir PAQUETE --image FOTO_JPG --output INFORME_JSON` levanta un servidor efímero en loopback, envía una imagen al modelo real y verifica respuestas 200/400/415/405. Cierra el servidor al finalizar. El campo `result` del informe puede pasarse a `toDisplayBoxes` para probar el frontend. No certifica precisión del detector ni sustituye las pruebas del backend de producción.
