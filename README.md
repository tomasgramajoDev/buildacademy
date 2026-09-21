# BuildAcademy

Prototipo web funcional de acompañamiento para ensamblar una PC. La configuración elegida conecta comprobaciones de compatibilidad, orientación de rendimiento y una guía 3D educativa.

## Ejecutar localmente

Desde este directorio, con Python instalado:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Abrir http://127.0.0.1:8765/ en un navegador con WebGL. No abrir index.html mediante doble clic: los módulos necesitan un servidor HTTP.

## Funciones implementadas

- Visor Three.js con motherboard y piezas esquemáticas, rotación, zoom, vista separada y animación de inserción.
- Ocho pasos educativos con explicación y contexto de la configuración seleccionada. Acceso al manual de la placa.
- Catálogo acotado: AMD Ryzen 5 7600, Intel Core i5-12400F, ASUS PRIME B650-PLUS, MSI PRO B760-P DDR4, familias NVIDIA RTX 4060 y AMD RX 7600. RAM y SSD son perfiles genéricos.
- Reglas de socket, generación y capacidad de memoria, y protocolo M.2. Incluye restricción M2_2/SATA8 de la placa MSI. La capacidad considera CPU y motherboard.
- Orientación de posibles límites según uso. No calcula FPS ni porcentajes y no confirma cuellos de botella sin benchmarks.
- Fotos locales con marcado manual de las nueve clases de conectores, eliminación y cancelación. Sin envío de imágenes al servidor.
- Configuración y pasos revisados guardados en el navegador. Cambiar componentes reinicia los pasos revisados para no conservar una revisión de otra configuración.
- Interfaz adaptable a móvil y escritorio. WebMCP opcional para leer estado y navegar pasos.

## Alcance pendiente

No hay detector YOLO entrenado, extracción automática de especificaciones, base de datos remota ni certificación de compatibilidad completa. Las geometrías y animaciones son genéricas: no reproducen mecanismos, ubicaciones ni montaje exacto de cada modelo. Faltan perfiles detallados de cooler, gabinete, fuente, variantes de GPU, BIOS y kits de memoria. El análisis de rendimiento es orientativo, no un detector validado mediante mediciones.

Las fichas oficiales están enlazadas en la interfaz y en dist/data.js; se consultaron el 21/09/2026. Las selecciones son ejemplos del catálogo inicial, no recomendaciones de compra ni cobertura de todos los fabricantes.

## Verificación

```powershell
node --test tests/rules.test.mjs
```

Las pruebas cubren incompatibilidades independientes, límite CPU/placa, restricciones M.2, estados incompletos, escenarios de uso e entradas inválidas. Se revisan además visor e interacciones en navegador. Three.js 0.180.0 está incluido en dist/vendor junto con su licencia MIT; las fuentes web tienen fallback local.

## Estructura

- dist/index.html y style.css: interfaz.
- dist/data.js: catálogo, pasos y reglas puras.
- dist/scene.js: representación 3D esquemática.
- dist/app.js: interacción y persistencia local.
- PROPUESTA-TECNICA.md: arquitectura futura y criterios de desarrollo.

