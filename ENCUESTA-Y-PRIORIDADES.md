# Encuesta y prioridades de BuildAcademy

## Fuente y método

Archivo aportado: Encuesta_ Experiencia al armar o actualizar una PC (Respuestas).xlsx. Hoja: Respuestas de formulario 1. Encabezados en A1:Q1; 223 registros en A2:Q224. Lectura realizada el 21/09/2026 sin modificar el archivo. No se encontraron filas completamente vacías ni duplicados exactos de fila; esto no demuestra unicidad de personas.

Los porcentajes siguientes usan como denominador los 223 registros y se redondean a un decimal. Las preguntas citadas en esta tabla no tienen respuestas faltantes. Las escalas numéricas se informan por puntuación, ya que el Excel no conserva las leyendas de todos sus extremos.

| Hallazgo | Conteo | Porcentaje | Rango fuente |
| --- | ---: | ---: | --- |
| Declaran consultar 3, 4 o 5 fuentes | 139 | 62,3% | I2:I224 |
| Puntúan con 4 o 5 la utilidad de un verificador automático | 182 | 81,6% | L2:L224 |
| Puntúan con 4 o 5 la probabilidad de usar una herramienta gratuita | 162 | 72,6% | P2:P224 |
| Eligen compatibilidad como dificultad principal | 52 | 23,3% | K2:K224 |
| Eligen ensamblaje como dificultad principal | 44 | 19,7% | K2:K224 |
| Eligen rendimiento conjunto como dificultad principal | 41 | 18,4% | K2:K224 |
| Puntúan con 4 o 5 la dificultad de determinar compatibilidad | 110 | 49,3% | D2:D224 |
| Puntúan su seguridad con 1, 2 o 3 | 141 | 63,2% | G2:G224 |
| Declaran compra o casi compra incompatible | 41 | 18,4% | E2:E224 |
| No están seguros de haber comprado o casi comprado algo incompatible | 66 | 29,6% | E2:E224 |
| Ya armaron o actualizaron una PC | 111 | 49,8% | B2:B224 |
| No lo hicieron, pero les interesa | 75 | 33,6% | B2:B224 |
| No lo hicieron ni les interesa | 37 | 16,6% | B2:B224 |

## Contraste con la primera entrega

La base confirma N = 223 y el 62% redondeado de consulta de tres o más fuentes. El valor de dificultad de compatibilidad en las puntuaciones 4 y 5 es 49,3%; corresponde corregir la afirmación de que supera el 50%.

El 48,0% que surge de sumar 41 respuestas afirmativas y 66 inciertas no representa compras incompatibles verificadas. Debe describirse como la unión de experiencia declarada de compra/casi compra e incertidumbre, manteniendo ambos grupos separados. Tampoco puede interpretarse una puntuación de confianza como una medición directa de miedo.

Compatibilidad, ensamblaje y rendimiento son opciones diferentes en la pregunta de prioridad. No se debe presentar el 23,3% de compatibilidad como una categoría conjunta de compatibilidad y rendimiento.

## Calidad de datos

Las columnas M, N y O mezclan respuestas etiquetadas como "3 Muy útil" y "5 Muy útil", junto con números y "1 Nada útil". Esto es consistente con escalas distintas o modificaciones del formulario, pero el Excel no permite confirmar su causa. No se calculará una media común de esas columnas sin revisar las versiones del formulario. Hay 5, 7 y 4 respuestas faltantes respectivamente, por lo que sus denominadores válidos son 218, 216 y 219.

La columna Q contiene 125 respuestas no vacías, incluidas respuestas breves sin contenido sustantivo. Una lectura exploratoria identificó dificultades con cableado, colocación del procesador, espacio en el gabinete, selección de fuentes de información y tutoriales que muestran otras piezas. No se asignan porcentajes a estos temas sin una codificación cualitativa completa y criterios explícitos.

Los resultados describen esta muestra. No se conoce el método de reclutamiento ni su representatividad. El interés declarado en una herramienta gratuita no prueba uso real, disposición a pagar ni efectividad del prototipo. Las 37 personas sin interés deben conservarse visibles en cualquier segmentación posterior.

## Decisiones de producto

| Evidencia | Decisión | Estado |
| --- | --- | --- |
| Consulta de múltiples fuentes y utilidad de verificar compatibilidad | Una configuración compartida, resultados explicados y enlaces a fichas oficiales | Implementado para catálogo inicial y reglas parciales |
| Ensamblaje como segunda dificultad más elegida | Guía de ocho pasos, repetición y vista 3D de piezas | Implementado con modelo genérico |
| Tutoriales con componentes distintos | Contexto y manual según placa seleccionada; geometrías específicas por modelo en una etapa posterior | Contexto implementado; montaje exacto pendiente |
| Rendimiento conjunto como tercera dificultad más elegida | Pedir uso previsto y explicar qué medir | Orientación implementada; benchmarks y detector validado pendientes |
| Problemas de cables y espacio | Priorizar fuentes, pinouts, dimensiones de GPU/cooler y restricciones del gabinete en la siguiente ampliación | Pendiente; la interfaz expone esos límites |
| Dificultad con especificaciones | Explicar cada resultado en lenguaje claro y distinguir incompatibilidad de información insuficiente | Implementado |

La encuesta no pregunta por detección de sockets en fotos ni por preferencia específica por 3D. Valida problemas que estas funciones podrían abordar, pero su valor debe probarse con usuarios. La siguiente evaluación debería medir si pueden elegir una configuración, interpretar una incompatibilidad y completar un paso de armado usando el prototipo.

No se incorporaron respuestas individuales ni el archivo original al sitio. Este documento contiene exclusivamente agregados y conclusiones de producto.
