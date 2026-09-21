# Validación de la ampliación · 21/09/2026

- 14 pruebas Node: incompatibilidades, memoria CPU/placa, restricción M2_2/SATA8, dimensiones y cables, datos ausentes, mediciones limitadas por FPS, valores inválidos, contexto del asistente y normalización de fichas.
- 5 pruebas Python: preparación de splits, placa repetida entre splits, duplicados de píxeles, cajas fuera de rango y clases ausentes. Usan imágenes sintéticas únicamente como fixtures del validador; no entrenan ni evalúan visión artificial.
- Navegador: once coincidencias en la configuración inicial y un resultado pendiente de validación integral. Fuente desconocida produce cuatro pendientes. Ficha de GPU creada, persistida tras recarga y eliminada; su procedencia permanece explícitamente no verificada.
- Captura de prueba importada: señal exploratoria de GPU; al activar límite de FPS deja de presentarla como posible saturación de GPU. Son datos de prueba, no benchmarks del equipo.
- IA: modelo Qwen2.5 1.5B descargado (~830 MB de parámetros) y ejecutado con WebGPU. Se observó generación real en español y recarga desde caché. Una primera respuesta expandió incorrectamente EPS; se corrigió el flujo para que consultas técnicas críticas de cableado reciban texto controlado claramente etiquetado. No constituye evaluación exhaustiva del modelo.
- Respuesta generativa revisada sobre la conveniencia de avanzar paso a paso; respuesta controlada revisada para ATX24, EPS 4+4 y PCIe 6+2. Sin herramientas del modelo que puedan modificar configuraciones o marcar pasos.
- Visor funcionando con piezas, instrucciones y controles; revisión de escritorio y móvil, sin desborde horizontal detectado ni errores de consola en los flujos probados.

No se ha entrenado un detector de conectores. No se han medido precisión/recall/mAP, latencia de visión, exactitud de montaje físico ni rendimiento real de las PCs del catálogo. No se garantiza ausencia de errores de lenguaje ni compatibilidad integral. Los resultados automatizados y de navegador se distinguen de estas validaciones pendientes.
