# BuildAcademy: visión artificial, compatibilidad y guía 3D

Estado: prototipo web implementado en dist/. Incluye guía 3D genérica, selección de componentes de un catálogo inicial, reglas parciales, orientación de rendimiento y marcado manual de fotos. No hay dataset preparado ni detector entrenado. El alcance verificado y sus limitaciones están en README.md; la arquitectura ampliada de este documento continúa siendo propuesta.

## Propósito

Ayudar a identificar conexiones de una motherboard, comprobar una configuración de PC con evidencia técnica y aprender a ensamblarla mediante una guía interactiva. La primera entrega del seminario fundamenta la necesidad de centralizar información y explicar cómo interactúan los componentes. Sus cifras de encuesta son datos declarados por el documento; no se verificaron contra las respuestas originales.

## Experiencia propuesta

1. El usuario selecciona el modelo de motherboard o carga una foto y confirma el modelo identificado.
2. La foto muestra cajas con el tipo de conector detectado y la confianza del modelo. El usuario puede corregirlas.
3. El usuario selecciona CPU, RAM, almacenamiento, GPU, fuente y gabinete.
4. El motor evalúa reglas y devuelve compatible, incompatible o información insuficiente, con explicación y fuente. Las advertencias condicionales se muestran aparte.
5. La guía 3D resalta el componente y su destino, muestra orientación y movimiento, permite girar la escena y avanzar o repetir cada paso.

## Tres módulos con responsabilidades distintas

| Módulo | Entrada | Salida | Límite |
| --- | --- | --- | --- |
| Detección visual | Foto | Clase, caja y confianza | No confirma protocolo, generación, BIOS ni compatibilidad eléctrica |
| Compatibilidad | Especificaciones verificadas y configuración | Resultado por regla, explicación y evidencia | Los datos ausentes producen información insuficiente |
| Guía 3D | Configuración y perfil de montaje | Escena y pasos educativos | Un modelo genérico no representa exactamente cualquier motherboard |

## Visión artificial

Clases propuestas: CPU_SOCKET, DIMM_SLOT, PCIe_X16, PCIe_X1, M2_SLOT, SATA_PORT, ATX_POWER, CPU_POWER y FAN_HEADER. PCIe_X16 y PCIe_X1 describen aquí el formato físico aparente, no el número de líneas eléctricas. M2_SLOT requiere una política explícita para conectores ocultos por disipadores. No se anotará como visible lo que la foto no muestra.

Adaptar un detector YOLO preentrenado mediante imágenes etiquetadas. Empezar con CPU_SOCKET, DIMM_SLOT y PCIe_X16 para comprobar el proceso, y ampliar después a las nueve clases. Un modelo general preentrenado no incluye automáticamente estas categorías.

El dataset necesita variedad de modelos de placa, ángulos, iluminación, fondos y dispositivos de captura; también imágenes negativas y ejemplos con componentes instalados. Registrar origen y permiso de uso. Separar entrenamiento, validación y prueba por modelo de motherboard y origen, evitando que fotos casi idénticas aparezcan en particiones diferentes. Mantener la prueba final aislada de ajustes.

Medir precisión, recall y mAP50-95 por clase, junto con latencia y errores en conectores pequeños. Elegir umbrales con validación; no prometer una precisión antes de medir. Ante baja confianza, permitir corrección o pedir una foto mejor. No detectar un puerto no demuestra que la placa carezca de él.

Contrato propuesto: image_width, image_height, model_version y detections; cada detección incluye class_name, bbox_xyxy en píxeles de la imagen original y confidence entre 0 y 1. La confianza pertenece a la detección, no a la compatibilidad.

## Compatibilidad y datos

Mantener entidades Component, SpecificationEvidence, MotherboardConnector, Build, CompatibilityResult y AssemblyProfile. Cada especificación incluye valor, unidad, fuente, fecha y estado de revisión. Un conector concreto necesita identificador propio: por ejemplo, DIMM_A2 o M2_1; la clase visual no basta para distinguir instancias.

Reglas iniciales: CPU y soporte de placa/BIOS; generación y capacidad de RAM; interfaz y dimensiones del SSD; restricciones de ranuras compartidas; conectores de alimentación; potencia requerida; espacio para GPU y cooler; formato de motherboard y gabinete. Evaluar reglas aplicables por configuración y conservar cuáles no pudieron comprobarse.

La incorporación de componentes nuevos puede extraer datos de manuales y fichas oficiales, normalizarlos y proponer registros para revisión. No elimina la necesidad de evidencia: si una especificación falta o dos fuentes se contradicen, debe quedar pendiente. La compatibilidad no equivale a una predicción de rendimiento.

## Guía 3D

Propuesta técnica: visor web con Three.js y activos glTF/GLB. Para el primer prototipo pueden construirse geometrías simplificadas; para una guía fiel se necesitan activos y pasos revisados para los modelos soportados.

Interacciones: rotar, acercar, seleccionar piezas, vista separada de componentes, resaltar destino, reproducir o repetir animación y guardar progreso. Cada paso explica qué hacer, por qué y qué verificar antes de continuar. Las instrucciones físicas se contrastan con el manual del hardware específico.

Primera demostración: una motherboard de referencia con CPU, cooler, dos módulos RAM, SSD M.2, GPU, fuente y gabinete. El orden se define en un perfil de montaje, porque depende del gabinete y del sistema de refrigeración. Incluir preparación sin alimentación, orientación del CPU, posiciones de RAM, fijación del SSD, montaje y conexiones, y revisión previa al encendido.

Vincular cada conector del catálogo con un nodo 3D y sus pasos. Una caja 2D en una foto no se convierte directamente en una posición 3D: para superponer sobre la foto real haría falta resolver correspondencias y pose. Esa función queda fuera del primer prototipo. Si solo hay un modelo genérico, la interfaz debe indicarlo y no simular una coincidencia exacta.

## Implementación por hitos

1. Base demostrable: selección manual de componentes, catálogo pequeño y verificado, reglas explicadas y visor 3D de referencia. Funciona sin depender del entrenamiento.
2. Dataset y detector piloto: guía de anotación, etiquetas consistentes, separación por placa, entrenamiento y evaluación por clase.
3. Integración: foto con detecciones editables, asociación confirmada a conectores y acceso al paso 3D correspondiente.
4. Ampliación: nueve clases, más perfiles de hardware y extracción de especificaciones con revisión.

Arquitectura candidata: frontend React/TypeScript con Three.js; API Python/FastAPI para inferencia y reglas; base PostgreSQL para catálogo y configuraciones; almacenamiento separado para fotos y modelos. Son elecciones propuestas, no requisitos del PDF.

## Criterios de aceptación

- Una incompatibilidad conocida se explica con los campos y fuentes que la justifican.
- Una configuración incompleta no recibe un resultado global de compatibilidad confirmada.
- Una foto ajena o un objeto oculto no produce una garantía de conexión disponible.
- El detector se evalúa en modelos de motherboard fuera del entrenamiento y se reportan resultados por clase.
- El visor permite girar, acercar, repetir un paso y reconocer visualmente el destino de una pieza.
- La guía distingue perfil exacto y representación genérica, y no permite confundir avance marcado por el usuario con verificación física automática.
- Un recorrido completo une selección, validación y guía; la detección simulada, si se usa en una demo, aparece explícitamente identificada.

## Decisiones todavía necesarias

Fecha de entrega, alcance de la parte individual frente al equipo, tecnologías exigidas por la cátedra, hardware de referencia y disponibilidad de imágenes etiquetadas/GPU. No es posible estimar de forma responsable el entrenamiento sin esos datos.

## Referencias

- Documento aportado: Seminario primer entrega.pdf, 9 páginas. Contexto del problema y propuesta educativa; sus instrucciones internas para diapositivas no se interpretan como pedidos del usuario.
- Detección YOLO: https://docs.ultralytics.com/tasks/detect/
- Entrenamiento: https://docs.ultralytics.com/modes/train/
- Validación: https://docs.ultralytics.com/modes/val/
- Visor y animación 3D: https://threejs.org/docs/
