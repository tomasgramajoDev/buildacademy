"""One fixed validation-only experiment; does not change the deployed runtime."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageOps
import evaluate_runtime
from evaluate_runtime import ConnectorDetector, iou

SMALL_CLASSES = {'M2_SLOT', 'SATA_PORT', 'FAN_HEADER'}


def xyxy(detection):
    b = detection['bbox']
    return [b['x'], b['y'], b['x'] + b['width'], b['y'] + b['height']]


def merge(detections):
    kept = []
    for d in sorted(detections, key=lambda d: -d['confidence']):
        if not any(d['classId'] == k['classId'] and iou(xyxy(d), xyxy(k)) > .45
                   for k in kept):
            kept.append(d)
        if len(kept) == 100:
            break
    return kept


class TiledDetector:
    def __init__(self, base):
        self.base, self.classes, self.version = base, base.classes, base.version

    def recognize(self, payload):
        result = self.base.recognize(payload)
        with Image.open(io.BytesIO(payload)) as source:
            im = ImageOps.exif_transpose(source).convert('RGB')
        w, h = im.size
        cw, ch = round(w * .6), round(h * .6)
        detections = list(result['detections'])
        for x, y in [(0, 0), (w-cw, 0), (0, h-ch), (w-cw, h-ch)]:
            encoded = io.BytesIO()
            im.crop((x, y, x+cw, y+ch)).save(encoded, format='PNG')
            for original in self.base.recognize(encoded.getvalue())['detections']:
                if original['classId'] not in SMALL_CLASSES:
                    continue
                a, b, c, d = xyxy(original)
                # Discard boxes cut by an internal crop boundary.
                if ((x > 0 and a <= 1) or (y > 0 and b <= 1)
                        or (x+cw < w and c >= cw-1)
                        or (y+ch < h and d >= ch-1)):
                    continue
                item = copy.deepcopy(original)
                item['bbox']['x'] += x
                item['bbox']['y'] += y
                detections.append(item)
        result['detections'] = merge(detections)
        return result


def macro_f1(report):
    return sum(2*r['tp'] / (2*r['tp']+r['fp']+r['fn'])
               if 2*r['tp']+r['fp']+r['fn'] else 0
               for r in report['per_class'].values()) / len(report['per_class'])


def experiment(model, data):
    base = ConnectorDetector(model, threshold=.5)
    with patch.object(evaluate_runtime, 'ConnectorDetector', return_value=base):
        baseline = evaluate_runtime.evaluate(model, data, 'val')
    with patch.object(evaluate_runtime, 'ConnectorDetector', return_value=TiledDetector(base)):
        tiled = evaluate_runtime.evaluate(model, data, 'val')
    tiled['runtime'] = 'Experimental full image plus four 60% corner crops; small classes only'
    return {
        'scope': 'Validation only; one predeclared preset; no holdout inference.',
        'model_sha256': hashlib.sha256((Path(model)/'connectors.onnx').read_bytes()).hexdigest(),
        'dataset_manifest_sha256': json.loads((Path(data)/'audit.json').read_text())['manifest_sha256'],
        'baseline': baseline, 'tiled': tiled,
        'baseline_macro_f1': macro_f1(baseline), 'tiled_macro_f1': macro_f1(tiled),
        'onnx_calls_per_image': {'baseline': 1, 'tiled': 5},
        'deployment_approved': False,
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True)
    p.add_argument('--data', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    result = experiment(args.model, args.data)
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['baseline_macro_f1', 'tiled_macro_f1']}))
