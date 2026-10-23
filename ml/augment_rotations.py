"""Derive 90/180/270 degree rotated copies of TRAIN photos; val/test stay untouched.

Boards are photographed in any orientation (several reviewed photos are rotated), so the rotated
copies exercise orientation invariance. Labels are rotated exactly, never inferred. Copies keep the
model group of the parent, so no model crosses splits. They are augmentation, not new boards.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from PIL import Image
from prepare_dataset import validate
from review_gate import validate_reviews

TURNS = {90: (Image.Transpose.ROTATE_90, lambda x, y, w, h: (y, 1-x, h, w)),
         180: (Image.Transpose.ROTATE_180, lambda x, y, w, h: (1-x, 1-y, w, h)),
         270: (Image.Transpose.ROTATE_270, lambda x, y, w, h: (1-y, x, h, w))}


def rotate_labels(lines, move):
    out = []
    for line in lines:
        cid, x, y, w, h = map(float, line.split())
        nx, ny, nw, nh = move(x, y, w, h)
        out.append(f'{int(cid)} {nx:.8f} {ny:.8f} {nw:.8f} {nh:.8f}')
    return out


def augment(manifest, output, angles):
    manifest, output = Path(manifest).resolve(), Path(output).resolve()
    rows = json.loads(manifest.read_text(encoding='utf-8'))
    validate_reviews(rows)
    validate(manifest)
    if output.exists():
        raise ValueError('Use a new output directory; do not overwrite existing data.')
    (output / 'rotations').mkdir(parents=True)
    derived = []
    for index, row in enumerate(rows):
        image, label = [(manifest.parent / row[k]).resolve() for k in ['image', 'label']]
        derived.append({**row, 'image': os.path.relpath(image, output), 'label': os.path.relpath(label, output)})
        if row['split'] != 'train':
            continue
        lines = label.read_text().splitlines()
        parent = hashlib.sha256(image.read_bytes()).hexdigest()
        with Image.open(image) as source:
            source = source.convert('RGB')
            for angle in angles:
                transpose, move = TURNS[angle]
                stem = f'{index:06}-r{angle}'
                source.transpose(transpose).save(output / 'rotations' / f'{stem}.png')
                (output / 'rotations' / f'{stem}.txt').write_text('\n'.join(rotate_labels(lines, move)) + '\n', encoding='utf-8')
                derived.append({**row, 'image': f'rotations/{stem}.png', 'label': f'rotations/{stem}.txt',
                                'reviewed_by': row['reviewed_by'] + '; exact rotation of reviewed labels',
                                'augmentation': {'type': 'rotation', 'degrees_counter_clockwise': angle,
                                                 'parent_image_sha256': parent, 'parent_model_id': row['model_id']}})
    target = output / 'manifest.json'
    target.write_text(json.dumps(derived, indent=2), encoding='utf-8')
    validate_reviews(derived)
    _, audit = validate(target)
    audit.update({'source_manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
                  'original_images': len(rows), 'derived_train_rotations': len(derived) - len(rows),
                  'limitation': 'Rotations are augmentation, not new motherboards or independent samples.'})
    (output / 'augmentation.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    return {k: audit[k] for k in ['images', 'boards', 'original_images', 'derived_train_rotations']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', required=True)
    parser.add_argument('--angles', type=int, nargs='+', default=[90, 180, 270], choices=[90, 180, 270])
    args = parser.parse_args()
    print(json.dumps(augment(args.manifest, args.output, args.angles)))
