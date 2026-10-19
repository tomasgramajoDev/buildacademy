# Consultas de Compass

Módulo de servidor para que front y back integren el chat en Compatibilidad y Guías. No modifica `dist/`, no crea interfaz ni servidor HTTP, no realiza reconocimiento de imágenes y no sustituye el motor de compatibilidad.

## Proveedor y ejecución

Node.js 22 o posterior, sin dependencias adicionales. El proveedor predeterminado es **Gemini 2.5 Flash** (`gemini-2.5-flash`), con `GEMINI_API_KEY` configurada únicamente en el entorno del servidor. Se eligió para poder utilizar la cuota gratuita publicada por Google. La clave no confirma el plan de facturación: verificar en AI Studio que el proyecto siga en Free. El módulo no activa facturación ni cambia automáticamente a un proveedor pago.

Configuración local: copiar `.env.example` a `.env` sólo si éste no existe, completar `GEMINI_API_KEY` y ejecutar Node con `--env-file=.env`. El archivo `.env` está excluido de Git. En producción usar el gestor de secretos del backend. Nunca usar variables públicas `VITE_*`/`NEXT_PUBLIC_*`, incluir la clave en una respuesta ni pegarla en un chat.

- `CONSULTATION_PROVIDER=gemini` (predeterminado).
- `GEMINI_MODEL=gemini-2.5-flash` (predeterminado). El adaptador también admite `gemini-2.5-flash-lite`, pero hay que evaluar sus respuestas antes de cambiarlo.
- OpenAI se conserva como alternativa explícita: `CONSULTATION_PROVIDER=openai`, `OPENAI_API_KEY` y opcionalmente `CONSULTATION_MODEL`. No se utiliza como fallback.

Cada consulta válida utiliza hasta tres solicitudes: clasificación, explicación y revisión. Rechazos locales no consumen tokens; un rechazo semántico normalmente utiliza una solicitud. Gemini tiene cuotas por proyecto/modelo que pueden cambiar; hay que consultarlas en AI Studio. HTTP 429 produce `rate_limited`, sin reintentos automáticos. Los tokens se contabilizan aunque sean cubiertos por la cuota gratuita; no se calcula un precio con tarifas fijas.

Pregunta, contexto e historial autorizado se envían al proveedor seleccionado. En la modalidad gratuita de Gemini, Google puede utilizar el contenido para mejorar sus productos: usar datos sintéticos para pruebas y no incluir datos personales. El adaptador no crea sesiones remotas ni habilita herramientas, búsqueda, ejecución o caché explícita. En OpenAI se mantiene `store:false`, que no garantiza ausencia de toda retención operativa.

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
import {createConsultationProvider} from './consultation/provider.js';

const bot = createConsultationBot({
  complete: createConsultationProvider(),
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

Para escribir preguntas propias desde una terminal abierta en la raíz del proyecto:

```text
npm run chat:demo
```

Empieza en la alerta de BIOS del ejemplo. `/armado` cambia al paso de colocación del procesador; `/compatibilidad` vuelve a la alerta; `/reiniciar` borra el historial actual y `/salir` termina. También admite una sola pregunta: `npm run chat:demo -- --question "¿Por qué aparece esta alerta?"`. La demo carga `.env`, mantiene sólo turnos aceptados en memoria, limita la sesión a 30 llamadas y las separa por 15 segundos. No es un endpoint de producción ni está vinculada al armado de la web. El límite local se reinicia al cerrar el proceso; backend sigue necesitando control persistente por usuario y proyecto. No ingresar datos personales ni secretos.

```text
node --test tests/consultation.test.mjs
node --env-file=.env consultation/evaluate-live.mjs
```

El primer comando usa un proveedor simulado: comprueba el flujo y sus fronteras, no la resistencia real del modelo. El segundo carga `.env`, requiere la clave del proveedor elegido, utiliza su cuota sobre datos sintéticos e imprime resultados para revisión. Separa las solicitudes por 15 segundos (`EVAL_INTERVAL_MS`, sólo para esta evaluación) y se detiene si el proveedor falla; no reintenta ni cambia de proveedor. No se ejecuta automáticamente con `npm test`.

Antes de integrar, ejecutar la evaluación real y ampliarla con alertas y pasos del backend, conversaciones de varios turnos, instrucciones maliciosas dentro de documentos, errores de diagnóstico, componentes de distintos sockets e intentos en varios idiomas. Una evaluación sin fallas no garantiza bloquear todas las evasiones.

### Verificación del 19/10/2026

- 46 pruebas automáticas del repositorio aprobadas (adaptadores con proveedor simulado).
- Evaluación real con `gemini-2.5-flash`: 9/9 estados esperados, 14 llamadas, sin interrupciones. Tres consultas educativas respondidas (dos sobre BIOS y una de montaje); seis pedidos fuera de alcance rechazados (uno por filtro local, cinco por clasificador).
- Uso reportado en esa ejecución: 5352 tokens de entrada y 445 de salida. Esto documenta consumo, no comprueba el plan de facturación de la cuenta ni garantiza cuota futura.
- Se revisó el texto de las tres respuestas: mantuvieron la BIOS como pendiente de verificar y recomendaron detener el montaje si el procesador no encaja. No se validó una integración HTTP o interfaz, que corresponde a backend/front. El conjunto de nueve casos no prueba resistencia universal a evasiones.

## Referencias de implementación

- https://ai.google.dev/api/generate-content
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits
- https://developers.openai.com/api/docs/guides/structured-outputs
- https://developers.openai.com/api/docs/models/gpt-4.1-mini

No se necesita entrenar ni hacer fine-tuning para esta primera integración: la especialización se implementa mediante contexto, instrucciones y controles.
