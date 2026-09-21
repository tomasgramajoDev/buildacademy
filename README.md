# BuildAcademy

Prototipo funcional de acompañamiento para armar una PC: componentes, compatibilidad explicada, guía 3D y asistente. La encuesta orienta las prioridades; el análisis agregado está en ENCUESTA-Y-PRIORIDADES.md.

## Abrir

Para ejecución local, doble clic en Iniciar-BuildAcademy.cmd o ejecutar desde esta carpeta:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Abrir http://127.0.0.1:8765/ . Los módulos requieren HTTP; no abrir el HTML directamente.

## Implementado

- Ocho pasos, escena Three.js esquemática, rotación, zoom, animación, vista separada y selección de piezas visibles. Algunos perfiles cambian proporciones/color; no es CAD de las piezas reales.
- Configuración de CPU, motherboard, RAM, SSD, GPU exacta, gabinete, cooler y fuente. Referencias Intel/AMD, ASUS/MSI, MSI/Sapphire, Corsair y Noctua.
- Once comprobaciones: socket, generación/capacidad de RAM, M.2, formato, medidas, potencia recomendada y conectores. Los datos ausentes quedan pendientes. BIOS y validación integral no están confirmadas.
- Incorporación local de GPU, gabinete ATX, cooler de aire y fuente ATX mediante texto estructurado, extracción y revisión antes de guardar. Procedencia obligatoria, contradicciones y magnitudes validadas. Las fichas aportadas no se convierten en datos oficiales por importarlas. No hay scraping universal ni lectura automática de PDFs.
- Asistente Qwen2.5 1.5B con WebLLM/WebGPU. Activación voluntaria, descarga inicial aproximada de 1 GB y caché del navegador. Sin clave de API ni servicio de IA pago. La IA clasifica la intención de la pregunta mediante JSON restringido; las respuestas se construyen con guías revisadas, el paso y los resultados del motor. No se muestran recomendaciones técnicas generadas libremente. Puede interpretar mal una pregunta; no verifica físicamente el armado. Requiere navegador/GPU compatibles y acceso inicial a Hugging Face/MLC. La guía contextual funciona sin cargar el modelo y se identifica como sin IA.
- Orientación de rendimiento por uso e importación JSON de 30–10.000 muestras. Reglas exploratorias para GPU, CPU, RAM y VRAM, con tratamiento de FPS limitados. No inventa porcentajes de cuello de botella ni predice otra configuración.
- Fotos locales, cajas manuales, exportación JSON/YOLO de nueve clases, cancelación y eliminación. Las marcas manuales no tienen confianza IA.
- Persistencia local, respaldo/restauración de configuración y fichas, impresión del resumen, interfaz móvil y WebMCP opcional de lectura/navegación.
- Pipeline Python: validación de etiquetas y procedencia, separación por placa, duplicados exactos, entrenamiento, evaluación de test y exportación ONNX. Ver ml/README.md.

## Bloqueos y límites reales

**Detector:** no hay dataset propio descargado. El usuario ya tiene cuenta de Roboflow en Edge; su descarga aún está pendiente. No se entrenó YOLO y no hay detección automática publicada. El candidato público tiene cuatro categorías generales. Se necesitan etiquetas de las nueve clases, placas de prueba reservadas y evaluación real. El pipeline no sustituye esos datos.

**Guía física:** faltan activos y revisión de mecanismos/posiciones por modelo para una réplica exacta. No se conoce la BIOS instalada ni el kit exacto de RAM/SSD. El visor y los márgenes nominales no certifican todas las interferencias ni el armado.

**Datos:** almacenamiento en navegador y respaldos JSON. No hay cuenta multiusuario, sincronización ni base central; PostgreSQL/FastAPI en la propuesta son alternativas, no servicios desplegados. El análisis de rendimiento usa datos aportados y no recoge sensores.

## Verificar y reconstruir

```powershell
npm ci
npm test
npm run build:ai
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_dataset.py
```

ML tiene dependencias separadas en ml/requirements.txt. El entorno instalado usa PyTorch CPU; se interrumpió la descarga CUDA al confirmar que faltaba el dataset. Las pruebas no implican entrenamiento o evaluación de un detector.

Dist contiene los activos publicables. La encuesta, fotos originales, pruebas, entorno Python y pesos de entrenamiento quedan excluidos. Dependencias y fuentes: THIRD-PARTY.md.
