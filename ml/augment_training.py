"""Derive overlapping train crops; preserve board groups and untouched held-out files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from PIL import Image
from prepare_dataset import validate
from review_gate import validate_reviews


def clip_labels(lines, width, height, crop):
    left, top, right, bottom = crop
    output = []
    for line in lines:
        cid, x, y, w, h = map(float, line.split())
        x1, y1 = max(left, (x-w/2)*width), max(top, (y-h/2)*height)
        x2, y2 = min(right, (x+w/2)*width), min(bottom, (y+h/2)*height)
        if x2 <= x1 or y2 <= y1:
            continue
        # Keep every positive intersection: dropping partial objects creates false negatives.
        output.append(f'{int(cid)} {((x1+x2)/2-left)/(right-left):.8f} '
                      f'{((y1+y2)/2-top)/(bottom-top):.8f} '
                      f'{(x2-x1)/(right-left):.8f} {(y2-y1)/(bottom-top):.8f}')
    return output


def augment(manifest, output):
    manifest, output = Path(manifest).resolve(), Path(output).resolve()
    rows = json.loads(manifest.read_text(encoding='utf-8'))
    validate_reviews(rows)
    validate(manifest)
    if output.exists():
        raise ValueError('Use a new output directory; do not overwrite existing data.')
    output.mkdir(parents=True)
    (output / 'crops').mkdir()
    derived = []
    held_out = []
    for index, row in enumerate(rows):
        image, label = [(manifest.parent / row[k]).resolve() for k in ['image', 'label']]
        original = {**row, 'image': os.path.relpath(image, output),
                    'label': os.path.relpath(label, output)}
        derived.append(original)
        if row['split'] != 'train':
            held_out.append({'model_id': row['model_id'], 'split': row['split'],
                             'image_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                             'label_sha256': hashlib.sha256(label.read_bytes()).hexdigest()})
            continue
        lines = label.read_text().splitlines()
        with Image.open(image) as source:
            source = source.convert('RGB')
            width, height = source.size
            cw, ch = round(width*.6), round(height*.6)
            for number, (left, top) in enumerate([(0,0), (width-cw,0), (0,height-ch), (width-cw,height-ch)]):
                crop = (left, top, left+cw, top+ch)
                stem = f'{index:06}-{number}'
                source.crop(crop).save(output / 'crops' / f'{stem}.png')
                text = '\n'.join(clip_labels(lines, width, height, crop))
                (output / 'crops' / f'{stem}.txt').write_text(text+'\n' if text else '', encoding='utf-8')
                derived.append({**row, 'image': f'crops/{stem}.png', 'label': f'crops/{stem}.txt',
                                'reviewed_by': row['reviewed_by']+'; deterministic crop of reviewed labels',
                                'augmentation': {'type':'overlapping_crop', 'rectangle':crop,
                                                 'parent_image_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                                                 'parent_model_id': row['model_id']}})
    target = output / 'manifest.json'
    target.write_text(json.dumps(derived, indent=2), encoding='utf-8')
    validate_reviews(derived)
    _, audit = validate(target)
    audit.update({'source_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
                  'original_images':len(rows), 'derived_train_crops':len(derived)-len(rows),
                  'held_out_originals':held_out,
                  'limitation':'Crops are augmentation, not new motherboards or independent samples. Partial visible boxes retained.'})
    (output / 'augmentation.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    return {k:audit[k] for k in ['images','boards','original_images','derived_train_crops']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(augment(args.manifest, args.output)))
