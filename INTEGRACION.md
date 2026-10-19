# Entrega para front y back

Los módulos se integran en la interfaz y el backend del equipo. No es necesario reutilizar la web de demostración de `dist/`.

## Consultas sobre alertas y pasos

El contrato y el ejemplo ejecutable de integración están en `consultation/README.md`. Backend importa `consultation/chatbot.js`, obtiene componentes, alertas y pasos desde su propia base y autoriza el acceso al armado. Front envía `buildId`, `contextId`, `mode` y `message`; no envía prompts, roles, diagnóstico ni historial arbitrario.

El proveedor predeterminado es Gemini. `GEMINI_API_KEY` pertenece exclusivamente al servidor. El módulo aplica filtros de alcance, clasificación y revisión de respuesta. Estas capas reducen evasiones; no constituyen una garantía absoluta frente a cualquier ataque. Las pruebas locales no consumen API; `npm run chat:demo` sí utiliza la clave y contexto ficticio. No confundir esa demo con datos de la web.

## Reconocimiento de conectores

Código y contrato: `recognition/README.md`. Paquetes disponibles en el repositorio:

| Paquete | Ubicación | Estado |
|---|---|---|
| Piloto de cuatro clases | `dist/models` | Predeterminado; se conservó tras comparar el candidato de cuatro clases |
| Nueve clases, segunda corrida | `ml/artifacts/nine-reviewed-v2` | Experimental, disponible para integración; no aprobado para reemplazar el piloto |
| Nueve clases, tercera corrida | `ml/artifacts/nine-reviewed-v3` | Candidato elegido frente a v4 por validación; experimental, con omisiones importantes |

Instalar las dependencias de inferencia con `python -m pip install -r recognition/requirements.txt` en un entorno Python. No hace falta instalar las herramientas de entrenamiento para ejecutar el ONNX. Para probar el modelo de nueve clases desde la raíz:

```powershell
python -m recognition.server --model-dir ml/artifacts/nine-reviewed-v3 --port 8771
```

Backend envía la foto como cuerpo binario a `POST http://127.0.0.1:8771/v1/recognitions`. El proceso escucha en loopback; el backend del equipo debe aplicar autenticación, límites y autorización antes de llamarlo. No incluye una API pública desplegada.

Front utiliza `toDisplayBoxes` de `recognition/frontend.js` para adaptar las coordenadas al tamaño mostrado. No muestra confianza. El resultado identifica conexiones visibles; no determina compatibilidad ni modifica el armado automáticamente. Backend conserva esa responsabilidad mediante especificaciones técnicas verificadas.

## Evidencia y límites del modelo ampliado

La cuarta corrida terminó con 20 modelos de motherboard y 56 recortes adicionales sólo de entrenamiento. No superó a v3: macro F1 en las mismas tres placas de validación fue 0,541 frente a 0,582. La selección se hizo sin consultar la prueba independiente. El paquete v3 queda disponible para la integración experimental.

En una motherboard reservada, v3 encontró 9 de 18 conexiones sin falsos positivos: omitió las cuatro ranuras RAM, M.2, una PCIe x1 y tres de cuatro conectores de ventiladores. Una sola placa no demuestra generalización. No se ajustó el umbral con este resultado ni se reemplazó el piloto. Ver `ml/SELECCION-NUEVE-CLASES.json` y `ml/EVALUACION-INDEPENDIENTE-V3.json`.

Los siguientes resultados de v2 se conservan como referencia histórica:

El paquete contiene pesos ONNX, manifiesto con hash y evaluación. Sus nueve salidas son CPU_SOCKET, DIMM_SLOT, PCIe_X16, PCIe_X1, M2_SLOT, SATA_PORT, ATX_POWER, CPU_POWER y FAN_HEADER.

La segunda corrida utilizó 16 fotos/modelos: 10 entrenamiento, 3 validación y 3 prueba, con 316 cajas revisadas visualmente contra manuales. La separación se hizo por modelo de motherboard. No hay certificación humana independiente. Los borradores de otras 190 fotos no forman parte del entrenamiento.

En las tres fotos de prueba, al umbral predeterminado 0,5, detectó correctamente 19 de 55 conexiones y produjo 6 falsos positivos. Seleccionar 0,35 mediante validación llevó a 25 aciertos y 13 falsos positivos en el test reutilizado. Hay fallos importantes en conectores pequeños. Las métricas completas y las condiciones están en `ml/REVISION-NUEVE-CLASES-V2.json`; no representan una prueba final independiente.

La integración técnica puede probarse ahora. Antes de publicar nueve clases como función confiable quedan: ampliar y revisar fotos diversas, entrenar de nuevo, evaluar en placas reservadas y decidir si los errores son aceptables para el producto. El paquete experimental no se activa automáticamente.

## Verificación reproducible

```powershell
python -m unittest discover -s tests -p test_recognition.py
node --test tests/recognition.test.mjs
python ml/smoke_integration.py --model-dir ml/artifacts/nine-reviewed-v2 --image RUTA_FOTO_JPG --output informe.json
```

El último comando carga el ONNX real, abre un servidor local efímero y comprueba respuestas HTTP 200/400/415/405. La foto de prueba es un archivo local; los datasets y las claves no se distribuyen con Git. El informe incluye la respuesta que front puede pasar al adaptador. Esto verifica transporte y contrato, no precisión sobre cualquier motherboard.
