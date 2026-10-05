# Dependencias y fuentes

- Three.js 0.180.0 y OrbitControls: MIT, licencia incluida en `dist/vendor/THREE-LICENSE.txt`.
- WebLLM 0.2.85: Apache-2.0, licencia incluida en `dist/vendor/WEBLLM-LICENSE.txt`. Bundle generado con esbuild 0.25.10.
- Modelo de lenguaje: Qwen2.5-1.5B-Instruct convertido por MLC. Se descarga al activarlo desde https://huggingface.co/mlc-ai/Qwen2.5-1.5B-Instruct-q4f16_1-MLC . Biblioteca de ejecución WebGPU servida por el proyecto MLC. No se incluyen pesos en este repositorio.
- Ultralytics: herramienta separada para entrenamiento de visión, con términos AGPL-3.0/comerciales. Piloto YOLO11n derivado de pesos oficiales, entrenado localmente; licencia incluida en dist/models/ULTRALYTICS-LICENSE.txt.
- Fichas oficiales de ASUS, MSI, Intel, AMD, Sapphire, Noctua y Corsair: enlazadas por componente en `dist/data.js`. Datos consultados el 21/09/2026; confirmar revisión exacta de producto. Las geometrías de la web son propias y esquemáticas.
- Dataset BIS497 Motherboard Part Locater: CC BY 4.0 según Roboflow Universe. Incorporado al piloto; 1616 polígonos convertidos a cajas envolventes. Sus métricas públicas no son resultados de BuildAcademy.
- PDF y encuesta del usuario: usados como contexto. No se publican los archivos originales ni respuestas individuales.
- ONNX Runtime Web 1.22.0: MIT, licencia en dist/vendor/ort/LICENSE.txt. Ejecuta la exportación ONNX del detector piloto.

## Galería de motherboards

Cuatro fotografías de Wikimedia Commons, redistribuidas como miniaturas sin edición. Autor, licencia y enlace al original constan en `dist/gallery/catalog.json` y en cada tarjeta de la interfaz. Las licencias son CC BY 4.0 o CC BY-SA 4.0 según la imagen. La búsqueda consulta la API pública de Commons y conserva los créditos devueltos por ella. Los nombres proceden de los títulos de archivo; no verifican el modelo ni sus especificaciones.

## Referencias de rendimiento

- Intel, What Is Bottlenecking My PC?: https://www.intel.com/content/www/us/en/gaming/resources/what-is-bottlenecking-my-pc.html
- Intel, Locate and Resolve CPU-GPU Bottlenecks: https://www.intel.com/content/www/us/en/developer/articles/technical/locate-and-resolve-cpu-gpu-bottlenecks.html

Las explicaciones son orientativas. Los umbrales de mediciones son reglas exploratorias propias, no un diagnóstico ni una metodología certificada por Intel.
