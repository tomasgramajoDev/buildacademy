"""Inspect a downloaded YOLO dataset without promoting it to training data."""
import argparse
import hashlib
import json
import math
import shutil
import stat
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageOps


def audit(archive, output):
    archive, output = Path(archive), Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('La salida debe estar vacía.')
    raw = output / 'raw'
    with zipfile.ZipFile(archive) as z:
        if sum(i.file_size for i in z.infolist()) > 2_000_000_000:
            raise ValueError('ZIP demasiado grande.')
        for item in z.infolist():
            path = (raw / item.filename).resolve()
            if not path.is_relative_to(raw) or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError('Ruta insegura en ZIP.')
            if item.is_dir() or path.suffix.lower() not in {'.yaml', '.txt', '.jpg', '.jpeg', '.png', '.webp', '.md'}:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with z.open(item) as src, path.open('xb') as dst:
                shutil.copyfileobj(src, dst)
    configs = list(raw.rglob('data.yaml'))
    if len(configs) != 1:
        raise ValueError('Se esperaba un data.yaml.')
    config = yaml.safe_load(configs[0].read_text(encoding='utf-8'))
    names = config['names']
    if isinstance(names, dict):
        names = [names[i] for i in range(len(names))]
    base = configs[0].parent
    counts, sizes, split_counts = Counter(), Counter(), Counter()
    converted_polygons = 0
    groups, hashes, samples = defaultdict(set), defaultdict(set), defaultdict(list)
    for image in sorted(base.glob('*/images/*')):
        if image.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
            continue
        split = image.parent.parent.name
        label = image.parent.parent / 'labels' / (image.stem + '.txt')
        boxes = []
        for line in label.read_text().splitlines():
            if not line.strip():
                continue
            parts = line.split()
            cid = int(parts[0])
            if not 0 <= cid < len(names):
                raise ValueError('Etiqueta de detección inválida.')
            coords = list(map(float, parts[1:]))
            if len(coords) == 4:
                x, y, w, h = coords
            elif len(coords) >= 6 and len(coords) % 2 == 0:
                if not all(math.isfinite(v) and 0 <= v <= 1 for v in coords):
                    raise ValueError('Polígono inválido.')
                left, right = min(coords[::2]), max(coords[::2])
                top, bottom = min(coords[1::2]), max(coords[1::2])
                x, y, w, h = (left+right)/2, (top+bottom)/2, right-left, bottom-top
                converted_polygons += 1
            else:
                raise ValueError('Etiqueta de detección inválida.')
            if not all(math.isfinite(v) for v in [x, y, w, h]) or min(w, h) <= 0 or min(x-w/2, y-h/2) < -1e-5 or max(x+w/2, y+h/2) > 1.00001:
                raise ValueError('Caja fuera de imagen.')
            counts[names[cid]] += 1
            boxes.append((names[cid], x, y, w, h))
        with Image.open(image) as im:
            rgb = im.convert('RGB')
            sizes[str(im.size)] += 1
            digest = hashlib.sha256(rgb.tobytes() + str(im.size).encode()).hexdigest()
        hashes[digest].add(split)
        groups[image.stem.split('.rf.')[0]].add(split)
        split_counts[split] += 1
        for name in {b[0] for b in boxes}:
            if len(samples[name]) < 6:
                samples[name].append((image, boxes))
    previews = output / 'previews'
    previews.mkdir()
    for index, (name, entries) in enumerate(samples.items()):
        canvas = Image.new('RGB', (1200, 840), 'white')
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 4), name, fill='black')
        for j, (path, boxes) in enumerate(entries):
            with Image.open(path) as im:
                im = im.convert('RGB')
                pen = ImageDraw.Draw(im)
                for cls, x, y, w, h in boxes:
                    if cls == name:
                        pen.rectangle(((x-w/2)*im.width, (y-h/2)*im.height, (x+w/2)*im.width, (y+h/2)*im.height), outline='red', width=3)
                thumb = ImageOps.contain(im, (390, 380))
            left, top = (j % 3)*400, 30+(j//3)*400
            canvas.paste(thumb, (left, top))
            draw.text((left+3, top+380), path.name[:48], fill='black')
        canvas.save(previews / f'{index:02}.jpg')
    report = {'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'images': dict(split_counts), 'classes': names, 'boxes': dict(counts),
              'image_sizes': dict(sizes), 'filename_groups': len(groups),
              'polygons_previewed_as_enclosing_boxes': converted_polygons,
              'filename_groups_crossing_splits': sum(len(s)>1 for s in groups.values()),
              'pixel_hashes_crossing_splits': sum(len(s)>1 for s in hashes.values()),
              'status': 'candidate_only_requires_visual_review_and_board_identity'}
    (output / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.archive, args.output), indent=2))
