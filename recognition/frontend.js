// Map backend detections to the EXIF-oriented image display size.
// Confidence is intentionally not included in the UI data.
export function toDisplayBoxes(result, displayWidth, displayHeight) {
  if (result?.schemaVersion !== 1 || !Number.isFinite(displayWidth) || !Number.isFinite(displayHeight) || displayWidth <= 0 || displayHeight <= 0 || !Number.isFinite(result.image?.width) || !Number.isFinite(result.image?.height) || result.image.width <= 0 || result.image.height <= 0 || !Array.isArray(result.detections)) throw new Error('Respuesta de reconocimiento inválida.');
  const sx = displayWidth / result.image.width, sy = displayHeight / result.image.height;
  return result.detections.map((d, index) => {
    const b = d.bbox;
    if (typeof d.classId !== 'string' || !b || ![b.x, b.y, b.width, b.height].every(Number.isFinite) || b.x < 0 || b.y < 0 || b.width <= 0 || b.height <= 0 || b.x+b.width > result.image.width+1e-5 || b.y+b.height > result.image.height+1e-5) throw new Error('Caja de reconocimiento inválida.');
    return {id: index, classId: d.classId, x: b.x*sx, y: b.y*sy, width: b.width*sx, height: b.height*sy};
  });
}
