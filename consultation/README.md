# Consultas de Compass

Módulo de servidor para que front y back integren el chat en Compatibilidad y Guías. No modifica `dist/`, no crea interfaz ni servidor HTTP, no realiza reconocimiento de imágenes y no sustituye el motor de compatibilidad.

## Proveedor y ejecución

Node.js 22 o posterior, sin dependencias adicionales. OpenAI Responses API, modelo predeterminado `gpt-4.1-mini-2025-04-14`; se puede cambiar con `CONSULTATION_MODEL` por otro compatible con Structured Outputs y estos parámetros, después de evaluar nuevamente. La clave `OPENAI_API_KEY` se configura en el gestor de secretos o entorno del backend. Nunca usar variables públicas `VITE_*`/`NEXT_PUBLIC_*`, incluirla en una respuesta ni pedirla al usuario en el chat.

Se eligió este modelo por su soporte de salidas estructuradas y el tamaño acotado de la tarea. No se hizo una comparación experimental contra Gemini. Cada consulta válida utiliza hasta tres llamadas pagadas: clasificación, explicación y revisión. Rechazos locales no consumen tokens; un rechazo semántico normalmente consume una llamada. Se informa uso real de entrada/salida, sin convertirlo a pesos o dólares con una tarifa fija desactualizable. `store:false` evita almacenar el objeto de respuesta para recuperarlo mediante la API; no significa ausencia de toda retención operativa del proveedor. Se envían pregunta, contexto e historial autorizado a OpenAI.

## Contrato para front y back

Propuesta de endpoint que implementará el equipo de backend: `POST /api/consultations`, con sesión autenticada y protección CSRF cuando corresponda. Cuerpo permitido:

```json
{
  "buildId": "demo-build",
  "contextId": "bios-warning",
  "mode": "compatibility",
  "message": "¿Por qué aparece esta alerta si el socket coincide?"
}
```

`mode` admite `compatibility` o `assembly`. `contextId` identifica UNA alerta o UN paso. El cliente no envía roles, prompts, diagnóstico, evidencia ni historial libre. No se admite texto de imágenes. La pregunta admite hasta 2000 caracteres.

El backend construye una única instancia y llama a `bot.reply(body, {userId: authenticatedSession.userId})`:

```js
import {createConsultationBot} from './consultation/chatbot.js';
import {createOpenAIProvider} from './consultation/openai.js';

const bot = createConsultationBot({
  complete: createOpenAIProvider(),
  loadContext: consultationRepository.loadAuthorizedContext,
  admit: consultationBudget.reserve,
  settle: consultationBudget.settle
});
```

Los tres últimos callbacks son interfaces que debe implementar backend, no servicios incluidos:

| Callback | Obligación |
| --- | --- |
| `loadContext({userId,buildId,contextId,mode})` | Comprobar propiedad/acceso al armado; recuperar el resultado real del motor o el paso vigente. Nunca copiar el contexto enviado por el cliente. |
| `admit({userId,maxCalls,maxOutputTokens,maxInputTokens})` | Reservar atómicamente cuota/coste y concurrencia por usuario; devolver una reserva o `null`. Límites máximos por solicitud: 3 llamadas, 1600 tokens de salida, reserva conservadora de 60000 de entrada. No usar un callback que siempre permita en producción. |
| `settle({userId,reservation,usage})` | Liberar concurrencia y reconciliar consumo, incluso si el proveedor falla. `unknownUsageCalls>0` significa que pudo haber consumo sin reporte: conservar cargo conservador hasta reconciliar, no asumir cero. Debe ser idempotente y manejar sus fallos de persistencia. |

Se rechazan solicitudes sin identidad o con campos no admitidos. La identidad la deriva la sesión del backend, no el body. El backend limita el cuerpo HTTP (por ejemplo 8 KiB) antes de parsear, aplica límite de frecuencia compartido entre instancias y serializa turnos de una conversación. Los errores de validación deben mapearse a 400, falta de sesión a 401 y ausencia de autorización a una respuesta genérica sin revelar armados ajenos.

### Contexto recuperado por backend

Ver `example-context.json`: ejemplo sintético de la alerta de BIOS de las capturas. No contiene una versión de BIOS requerida inventada ni confirma FlashBack. Para un paso:

```json
{
  "buildId": "demo-build",
  "contextId": "cpu-install",
  "mode": "assembly",
  "revision": "build-12-guide-3",
  "title": "Colocación del procesador",
  "status": "step",
  "evidence": [
    {"id": "instruction", "text": "La guía pide comprobar la orientación con el manual del modelo exacto antes de insertar el procesador. Si no encaja, detener el montaje sin forzarlo."}
  ],
  "history": []
}
```

`status`: `pass`, `fail`, `unknown` o `step`. Evidencia: hasta 16 fragmentos, IDs únicos, texto hasta 2000 caracteres por fragmento. Seleccionar sólo datos relevantes y fragmentos de manuales verificados; conservar procedencia/URL del documento en el repositorio del backend. No incluir secretos, correo ni datos personales. Límite total de pregunta + contexto: 14000 bytes UTF-8.

Historial: máximo seis mensajes `user`/`assistant`, 2000 caracteres cada uno, de la misma conversación, usuario, armado, revisión y alerta/paso. Backend guarda sólo turnos aceptados y entregados; no persiste borradores del proveedor. Al cambiar revisión/paso/alerta, reiniciar o seleccionar historial correspondiente. Los turnos rechazados no se incorporan. La biblioteca no almacena conversaciones por sí misma.

### Respuesta

```json
{
  "status": "answered",
  "answer": "El socket por sí solo no confirma soporte con la BIOS instalada. Falta verificar su versión y la lista oficial del modelo exacto.",
  "evidenceIds": ["diagnosis"],
  "contextId": "bios-warning",
  "revision": "demo-1",
  "usage": {"inputTokens": 1700, "outputTokens": 140, "calls": 3, "unknownUsageCalls": 0}
}
```

Los números anteriores son ilustrativos, no un benchmark. Otros estados: `out_of_scope`, `insufficient_context`, `rate_limited`, `unavailable`. En rechazos/errores se entrega texto fijo, nunca el borrador sin validar. `revision` se incluye en respuestas aceptadas: front debe descartar respuestas de una revisión que ya no está mostrando. Renderizar `answer` como texto plano, nunca `innerHTML`. Backend puede omitir `usage` en su respuesta pública y guardarlo para control de costes.

## Alcance y defensas

Se permiten dudas que ayuden a comprender la alerta o paso y sus conceptos relacionados: por qué coincide socket pero falta verificar BIOS, por qué DDR4 no entra en DDR5, qué revisar si una pieza no encaja. No se responde como asistente general sobre cualquier tema de PC: programar una calculadora, escribir scripts o tareas ajenas siguen fuera de alcance aunque mencionen armado.

1. Validación de identidad, tamaño y campos; contexto recuperado por backend.
2. Bloqueo local de desvíos evidentes, normalizando Unicode. Puede tener falsos positivos; reformular la consulta sobre la alerta.
3. Clasificador semántico: rechaza pedidos mixtos, cambios de rol y evasiones.
4. Generación con evidencia, esquema estricto, sin herramientas, navegación ni ejecución.
5. Validación local de salida y referencias, seguida por auditoría semántica de fundamentación y alcance. Fallos se cierran sin entregar la respuesta candidata.

Los prompts no son una barrera infalible. Un segundo pase del mismo modelo tampoco demuestra inmunidad a inyección ni exactitud técnica. Hace falta evaluar casos reales/adversariales y revisar falsos positivos antes de producción. La biblioteca no toma acciones, marca BIOS como actualizada ni cambia resultados de compatibilidad. No valida los porcentajes o watts ilustrativos del wireframe: si el motor no provee metodología y datos, se pide información.

## Pruebas

```text
node --test tests/consultation.test.mjs
node consultation/evaluate-live.mjs
```

El primer comando usa un proveedor simulado: comprueba el flujo y sus fronteras, no la resistencia real de GPT. El segundo requiere `OPENAI_API_KEY`, realiza llamadas pagadas sobre datos sintéticos e imprime resultados para revisión. No se ejecuta automáticamente con `npm test`.

Antes de integrar, ejecutar la evaluación real y ampliarla con alertas y pasos del backend, conversaciones de varios turnos, instrucciones maliciosas dentro de documentos, errores de diagnóstico, componentes de distintos sockets e intentos en varios idiomas. Una evaluación sin fallas no garantiza bloquear todas las evasiones.

## Referencias de implementación

- https://developers.openai.com/api/docs/guides/structured-outputs
- https://developers.openai.com/api/docs/models/gpt-4.1-mini

No se necesita entrenar ni hacer fine-tuning para esta primera integración: la especialización se implementa mediante contexto, instrucciones y controles.
