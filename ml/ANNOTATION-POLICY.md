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
