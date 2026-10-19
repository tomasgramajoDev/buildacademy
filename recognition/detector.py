"""Local connector inference. No network, UI, or compatibility claims."""
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
import onnxruntime as ort

TARGET_CLASSES = ['CPU_SOCKET', 'DIMM_SLOT', 'PCIe_X16', 'PCIe_X1', 'M2_SLOT',
                  'SATA_PORT', 'ATX_POWER', 'CPU_POWER', 'FAN_HEADER']
PILOT_CLASSES = ['CPU_SOCKET', 'PCIE_SLOT', 'POWER_CONNECTOR', 'DIMM_SLOT']


class RecognitionError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def decode(output, classes, width, height, rw, rh, px, py, threshold):
    if output.ndim != 3 or output.shape[0] != 1 or output.shape[1] != len(classes)+4:
        raise RecognitionError('invalid_model_output', 'Salida del detector incompatible.')
    candidates = []
    for values in output[0].T:
        if not np.isfinite(values).all():
            continue
        cid = int(np.argmax(values[4:])); score = float(values[4+cid])
        cx, cy, w, h = map(float, values[:4])
        if not threshold <= score <= 1 or w <= 0 or h <= 0:
            continue
        x1, y1 = max(0., (cx-w/2-px)*width/rw), max(0., (cy-h/2-py)*height/rh)
        x2, y2 = min(float(width), (cx+w/2-px)*width/rw), min(float(height), (cy+h/2-py)*height/rh)
        if x2 > x1 and y2 > y1:
            candidates.append({'classId': classes[cid], 'confidence': score,
                               'bbox': {'x': x1, 'y': y1, 'width': x2-x1, 'height': y2-y1}})
    kept = []
    for box in sorted(candidates, key=lambda b: -b['confidence']):
        a = box['bbox']; suppress = False
        for previous in kept:
            if previous['classId'] != box['classId']: continue
            b = previous['bbox']
            overlap = max(0, min(a['x']+a['width'], b['x']+b['width'])-max(a['x'], b['x'])) * max(0, min(a['y']+a['height'], b['y']+b['height'])-max(a['y'], b['y']))
            union = a['width']*a['height']+b['width']*b['height']-overlap
            if overlap/union > .45: suppress = True; break
        if not suppress: kept.append(box)
        if len(kept) == 100: break
    return kept


class ConnectorDetector:
    """Create one instance per backend worker; pass only trusted model paths."""
    def __init__(self, model_dir=None):
        root = Path(model_dir) if model_dir else Path(__file__).resolve().parents[1]/'dist/models'
        manifest = json.loads((root/'manifest.json').read_text(encoding='utf-8'))
        self.classes = manifest.get('classes')
        self.size = manifest.get('inputSize')
        if not manifest.get('ready') or self.classes not in [TARGET_CLASSES, PILOT_CLASSES] or self.size not in [320, 416, 640]:
            raise RecognitionError('model_unavailable', 'Modelo no disponible o contrato desconocido.')
        model = (root/'connectors.onnx').read_bytes()
        if hashlib.sha256(model).hexdigest() != manifest.get('sha256'):
            raise RecognitionError('model_integrity', 'La integridad del modelo no coincide.')
        options = ort.SessionOptions(); options.intra_op_num_threads = 2
        self.session = ort.InferenceSession(model, sess_options=options, providers=['CPUExecutionProvider'])
        self.input = self.session.get_inputs()[0]
        if self.input.shape != [1, 3, self.size, self.size]:
            raise RecognitionError('model_unavailable', 'Entrada del modelo incompatible.')
        self.version = manifest['version']

    def recognize(self, image_bytes):
        if not isinstance(image_bytes, bytes) or not 0 < len(image_bytes) <= 15*1024*1024:
            raise RecognitionError('invalid_image_size', 'La imagen debe ocupar entre 1 byte y 15 MB.')
        try:
            with Image.open(io.BytesIO(image_bytes)) as original:
                if original.format not in ['JPEG', 'PNG', 'WEBP'] or getattr(original, 'n_frames', 1) != 1:
                    raise RecognitionError('unsupported_image', 'Usá una imagen JPG, PNG o WebP sin animación.')
                if min(original.size) < 32 or original.width*original.height > 20_000_000:
                    raise RecognitionError('invalid_dimensions', 'Dimensiones de imagen fuera de límites.')
                im = ImageOps.exif_transpose(original).convert('RGB')
        except RecognitionError: raise
        except (OSError, ValueError, Image.DecompressionBombError) as error:
            raise RecognitionError('invalid_image', 'No se pudo leer la imagen.') from error
        width, height = im.size; scale = min(self.size/width, self.size/height)
        rw, rh = math.floor(width*scale+.5), math.floor(height*scale+.5)
        px, py = (self.size-rw)//2, (self.size-rh)//2
        canvas = Image.new('RGB', (self.size, self.size), (114,114,114))
        canvas.paste(im.resize((rw,rh), Image.Resampling.BILINEAR), (px,py))
        tensor = np.asarray(canvas, dtype=np.float32).transpose(2,0,1)[None]/255
        output = self.session.run(None, {self.input.name: tensor})[0]
        detections = decode(output, self.classes, width, height, rw, rh, px, py, .5)
        return {'schemaVersion': 1, 'model': {'version': self.version, 'classes': self.classes,
                'coversNineClasses': self.classes == TARGET_CLASSES},
                'image': {'width': width, 'height': height, 'orientation': 'exif_transposed'},
                'detections': detections, 'compatibilityVerified': False}
