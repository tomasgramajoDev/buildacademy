"""Generate review-only proposals. Never write canonical labels or assign splits."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from recognition.detector import ConnectorDetector, TARGET_CLASSES


def propose(model_dir, queue_dir, output):
    queue_dir, output = Path(queue_dir).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('Use a new output directory to preserve previous reviews.')
    reviewed = {
        json.loads(p.read_text(encoding='utf-8'))['image_sha256']
        for p in (ROOT / 'ml/annotations').glob('*.json')
    }
    reservation_file = ROOT / 'ml/HOLDOUT-RESERVATIONS.json'
    reserved = {r['image_sha256'] for r in json.loads(reservation_file.read_text(encoding='utf-8'))['reservations']} if reservation_file.exists() else set()
    detector = ConnectorDetector(model_dir, threshold=.25)
    if detector.classes != TARGET_CLASSES:
        raise ValueError('Proposals require the nine-class model.')
    output.mkdir(parents=True)
    records = []
    for row in json.loads((queue_dir / 'queue.json').read_text(encoding='utf-8')):
        path = (queue_dir / row['image']).resolve()
        if not path.is_relative_to(queue_dir):
            raise ValueError('Image path outside review queue.')
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest in reviewed or digest in reserved:
            continue
        result = detector.recognize(data)
        with Image.open(path) as image:
            preview = ImageOps.exif_transpose(image).convert('RGB')
        draw = ImageDraw.Draw(preview)
        boxes = []
        for detection in result['detections']:
            box = detection['bbox']
            bounds = [box['x'], box['y'], box['x']+box['width'], box['y']+box['height']]
            name = detection['classId']
            boxes.append([name, *bounds])
            draw.rectangle(bounds, outline='orange', width=2)
            draw.text((bounds[0], bounds[1]), str(TARGET_CLASSES.index(name)), fill='red')
        draft = {
            'image': str(path.relative_to(ROOT)), 'image_sha256': digest,
            'status': 'pending', 'model_id': None, 'split': None,
            'proposal_model': detector.version, 'proposal_threshold': .25,
            'boxes_xyxy': boxes, 'source': row['source'], 'license': row['license'],
            'unresolved': ['Verify identity and model-level split.',
                           'Inspect every visible connector, including missed detections.',
                           'Correct false positives and geometry against manufacturer manual.'],
        }
        (output / f'{path.stem}.json').write_text(json.dumps(draft, indent=2), encoding='utf-8')
        preview.save(output / f'{path.stem}.png')
        records.append({'image': draft['image'], 'proposed_boxes': len(boxes),
                        'small_connector_proposals': sum(b[0] in ['FAN_HEADER', 'M2_SLOT', 'PCIe_X1'] for b in boxes)})
    report = {'status': 'pending_manual_review_not_training_data', 'count': len(records),
              'model': detector.version, 'images': records,
              'warning': 'Review all images, including zero detections. Proposal counts are not truth or model identity.'}
    (output / 'index.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return {'images': len(records), 'output': str(output), 'status': report['status']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--queue', default='datasets/connectors-nine-review')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(propose(args.model_dir, args.queue, args.output)))
