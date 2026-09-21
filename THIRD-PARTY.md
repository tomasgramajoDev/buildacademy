# Dependencias y fuentes

- Three.js 0.180.0 y OrbitControls: MIT, licencia incluida en `dist/vendor/THREE-LICENSE.txt`.
- WebLLM 0.2.85: Apache-2.0, licencia incluida en `dist/vendor/WEBLLM-LICENSE.txt`. Bundle generado con esbuild 0.25.10.
- Modelo de lenguaje: Qwen2.5-1.5B-Instruct convertido por MLC. Se descarga al activarlo desde https://huggingface.co/mlc-ai/Qwen2.5-1.5B-Instruct-q4f16_1-MLC . Biblioteca de ejecución WebGPU servida por el proyecto MLC. No se incluyen pesos en este repositorio.
- Ultralytics: herramienta separada para entrenamiento de visión, con términos AGPL-3.0/comerciales. Piloto YOLO11n derivado de pesos oficiales, entrenado localmente; licencia incluida en dist/models/ULTRALYTICS-LICENSE.txt.
- Fichas oficiales de ASUS, MSI, Intel, AMD, Sapphire, Noctua y Corsair: enlazadas por componente en `dist/data.js`. Datos consultados el 21/09/2026; confirmar revisión exacta de producto. Las geometrías de la web son propias y esquemáticas.
- Dataset BIS497 Motherboard Part Locater: CC BY 4.0 según Roboflow Universe. Incorporado al piloto; 1616 polígonos convertidos a cajas envolventes. Sus métricas públicas no son resultados de BuildAcademy.
- PDF y encuesta del usuario: usados como contexto. No se publican los archivos originales ni respuestas individuales.
- ONNX Runtime Web 1.22.0: MIT, licencia en dist/vendor/ort/LICENSE.txt. Ejecuta la exportación ONNX del detector piloto.
