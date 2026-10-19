# Política de anotación connectors-v1

El objetivo es localizar conexiones visibles para orientar al usuario. No determina cuántos dispositivos admite una conexión ni su compatibilidad.

- CPU_SOCKET: conjunto visible del socket y su mecanismo de retención. Se admite tapa protectora instalada porque forma parte del conjunto visible; se excluye cuando lo oculta un cooler. No etiquetar un procesador separado como socket.
- DIMM_SLOT: una caja por ranura física, incluyendo trabas. No agrupar el banco completo.
- PCIe_X16 / PCIe_X1: tamaño físico de la ranura, sin afirmar número de líneas eléctricas. Excluir PCI y otros formatos.
- M2_SLOT: cuerpo del conector visible, no toda el área del SSD. Excluir SSD instalado o disipador cuando oculten el conector. Se incluyen conectores M.2 de SSD y de WiFi: no deducir key, protocolo, versión ni compatibilidad con un SSD.
- SATA_PORT: cuerpo visible del conector. Si varios puertos apilados comparten una carcasa inseparable en la vista, una caja alrededor de esa carcasa; nunca interpretar la cantidad de cajas como cantidad de puertos. Cuando las carcasas se distinguen, separar las cajas.
- ATX_POWER: conector principal de alimentación de la motherboard. No confundir con USB interno.
- CPU_POWER: conector EPS/ATX12V de CPU identificado por ubicación, serigrafía y manual. No inferir sólo por parecido a PCIe de alimentación.
- FAN_HEADER: conectores de ventilador CPU/sistema y bomba identificados en el manual. No incluir soportes mecánicos, RGB, USB ni otros headers parecidos.

Cajas ajustadas al cuerpo visible; no inventar cajas de partes totalmente ocultas. Una foto ambigua permanece fuera del entrenamiento hasta resolver la duda. Registrar fabricante/modelo, fuente, licencia y manual. Todas las fotos del mismo modelo permanecen en un solo split, incluso si no se conoce qué unidad física se fotografió. Este agrupamiento conservador no afirma conocer la identidad física.

Las revisiones visuales asistidas por el manual no son una certificación humana independiente. Los estados de revisión no sustituyen inspección, diversidad ni evaluación en placas reservadas.

## Borradores para ampliar la colección

`python ml/propose_annotations.py --model-dir PAQUETE_NUEVE_CLASES --output DIRECTORIO_NUEVO` genera propuestas y vistas numeradas para las fotos todavía no anotadas. Los números corresponden al orden de clases del detector. Conserva fuente y hash, no asigna modelo ni split y no escribe en `ml/annotations`. Revisar también las fotos sin detecciones: el modelo omite conectores y no debe decidir qué existe en la imagen.

Las discrepancias de identidad se registran en `ml/annotation-review-notes`. Una foto con identidad sin resolver no se incorpora al entrenamiento. Las propuestas no reemplazan la inspección del manual ni las anotaciones canónicas revisadas.

## Recortes derivados de entrenamiento

`python ml/augment_training.py MANIFIESTO_REVISADO --output DIRECTORIO_NUEVO` conserva las fotos completas y añade cuatro recortes por foto de entrenamiento. Cada recorte ocupa el 60 % del ancho y alto original y conserva todas las intersecciones positivas de las cajas, incluidas partes recortadas. No infiere conexiones ocultas ni genera etiquetas nuevas mediante el detector.

Cada variante conserva el modelo y grupo de la placa original. Las fotos y etiquetas de validación/prueba se referencian sin transformaciones y sus hashes quedan registrados. Los recortes no aumentan la cantidad de placas independientes. Pasar el manifiesto resultante por `review_gate.py` antes de entrenar. Evaluar después sobre fotos completas: ampliar detalles durante entrenamiento no demuestra por sí mismo una mejora en inferencia.

## Reserva para evaluación independiente

`ml/HOLDOUT-RESERVATIONS.json` registra placas excluidas del conjunto de desarrollo. La reserva no equivale a anotaciones terminadas. `build_reviewed_manifest.py` rechaza los nombres de modelo reservados; revisar manualmente variantes, nombres alternativos y fotos duplicadas. Mantener sus etiquetas en una colección separada. No generar propuestas con los candidatos ni medirlos sobre esas fotos antes de fijar la selección mediante validación. Registrar el primer resultado independiente, incluso si es malo; usarlo después para ajustes convierte ese conjunto en datos de desarrollo y requiere otra reserva futura.
